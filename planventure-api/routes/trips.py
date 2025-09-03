from flask import Blueprint, request, jsonify
from datetime import datetime, date
from models import Trip, User
from models.base import db
from utils.validation import ValidationUtils, validate_json
from utils.middleware import AuthMiddleware, get_current_user
from utils.itinerary import ItineraryTemplate
import logging
import json

# Create blueprint
trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')

def validate_trip_data(data, is_update=False):
    """
    Validate trip creation/update data
    
    Args:
        data (dict): Trip data to validate
        is_update (bool): Whether this is an update operation
        
    Returns:
        dict: Validation result with errors
    """
    errors = {}
    
    # Validate destination (required for creation, optional for updates)
    if not is_update or 'destination' in data:
        destination = data.get('destination', '').strip()
        if not destination:
            errors['destination'] = 'Destination is required'
        elif len(destination) > 255:
            errors['destination'] = 'Destination must not exceed 255 characters'
    
    # Validate dates
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not is_update or 'start_date' in data:
        if not start_date:
            errors['start_date'] = 'Start date is required'
        else:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                if start_date < date.today():
                    errors['start_date'] = 'Start date cannot be in the past'
            except ValueError:
                errors['start_date'] = 'Invalid start date format. Use YYYY-MM-DD'
    
    if not is_update or 'end_date' in data:
        if not end_date:
            errors['end_date'] = 'End date is required'
        else:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                if start_date and end_date < start_date:
                    errors['end_date'] = 'End date cannot be before start date'
            except ValueError:
                errors['end_date'] = 'Invalid end date format. Use YYYY-MM-DD'
    
    # Validate coordinates (optional)
    if 'latitude' in data and data['latitude'] is not None:
        try:
            lat = float(data['latitude'])
            if not -90 <= lat <= 90:
                errors['latitude'] = 'Latitude must be between -90 and 90'
        except (ValueError, TypeError):
            errors['latitude'] = 'Invalid latitude format'
    
    if 'longitude' in data and data['longitude'] is not None:
        try:
            lng = float(data['longitude'])
            if not -180 <= lng <= 180:
                errors['longitude'] = 'Longitude must be between -180 and 180'
        except (ValueError, TypeError):
            errors['longitude'] = 'Invalid longitude format'
    
    # Validate budget (optional)
    if 'budget' in data and data['budget'] is not None:
        try:
            budget = float(data['budget'])
            if budget < 0:
                errors['budget'] = 'Budget cannot be negative'
        except (ValueError, TypeError):
            errors['budget'] = 'Invalid budget format'
    
    # Validate status (optional)
    valid_statuses = ['planned', 'active', 'completed', 'cancelled']
    if 'status' in data:
        status = data.get('status')
        if status and status not in valid_statuses:
            errors['status'] = f'Status must be one of: {", ".join(valid_statuses)}'
    
    # Validate description length (optional)
    if 'description' in data and data['description']:
        if len(data['description']) > 1000:
            errors['description'] = 'Description must not exceed 1000 characters'
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

@trips_bp.route('', methods=['POST'])
@AuthMiddleware.require_auth
@validate_json(['destination', 'start_date', 'end_date'])
def create_trip():
    """
    Create a new trip
    
    Expected JSON:
    {
        "destination": "Paris, France",
        "start_date": "2024-06-01",
        "end_date": "2024-06-07",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "description": "Summer vacation to Paris",
        "budget": 2500.00,
        "status": "planned",
        "generate_itinerary": true,
        "trip_style": "balanced"
    }
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Validate trip data
        validation = validate_trip_data(data)
        if not validation['valid']:
            return jsonify({
                'error': 'Validation failed',
                'details': validation['errors']
            }), 400
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Generate default itinerary if requested
        itinerary = None
        if data.get('generate_itinerary', False):
            destination_type = data.get('destination_type')
            default_itinerary = ItineraryTemplate.generate_default_itinerary(
                data['destination'], 
                start_date, 
                end_date, 
                destination_type
            )
            itinerary = ItineraryTemplate.format_itinerary_for_storage(default_itinerary)
        
        # Create trip
        trip = Trip(
            user_id=user.id,
            destination=data['destination'].strip(),
            start_date=start_date,
            end_date=end_date,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            description=data.get('description', '').strip() if data.get('description') else None,
            budget=data.get('budget'),
            status=data.get('status', 'planned'),
            itinerary=itinerary
        )
        
        trip.save()
        
        response_data = {
            'message': 'Trip created successfully',
            'trip': trip.to_dict()
        }
        
        # Include itinerary summary if generated
        if itinerary:
            parsed_itinerary = ItineraryTemplate.parse_itinerary_from_storage(itinerary)
            response_data['itinerary_summary'] = ItineraryTemplate.get_itinerary_summary(parsed_itinerary)
        
        return jsonify(response_data), 201
        
    except Exception as e:
        logging.error(f"Trip creation error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create trip',
            'message': 'An unexpected error occurred'
        }), 500

@trips_bp.route('', methods=['GET'])
@AuthMiddleware.require_auth
def get_trips():
    """
    Get all trips for the authenticated user
    
    Query parameters:
    - status: Filter by trip status (planned, active, completed, cancelled)
    - upcoming: Boolean to get only upcoming trips
    - page: Page number for pagination (default: 1)
    - per_page: Items per page (default: 10, max: 100)
    """
    try:
        user = get_current_user()
        
        # Get query parameters
        status = request.args.get('status')
        upcoming = request.args.get('upcoming', '').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        
        # Build query
        query = Trip.query.filter_by(user_id=user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        if upcoming:
            today = date.today()
            query = query.filter(Trip.start_date > today)
        
        # Order by start date (newest first)
        query = query.order_by(Trip.start_date.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        trips = [trip.to_dict() for trip in pagination.items]
        
        return jsonify({
            'trips': trips,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except ValueError:
        return jsonify({
            'error': 'Invalid pagination parameters'
        }), 400
    except Exception as e:
        logging.error(f"Get trips error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve trips'
        }), 500

@trips_bp.route('/<int:trip_id>', methods=['GET'])
@AuthMiddleware.require_auth
def get_trip(trip_id):
    """Get a specific trip by ID"""
    try:
        user = get_current_user()
        
        trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': 'Trip does not exist or you do not have permission to view it'
            }), 404
        
        return jsonify({
            'trip': trip.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Get trip error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve trip'
        }), 500

@trips_bp.route('/<int:trip_id>', methods=['PUT'])
@AuthMiddleware.require_auth
def update_trip(trip_id):
    """
    Update a specific trip
    
    Expected JSON (all fields optional):
    {
        "destination": "Updated destination",
        "start_date": "2024-06-01",
        "end_date": "2024-06-07",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "description": "Updated description",
        "budget": 3000.00,
        "status": "active"
    }
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        # Find trip
        trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': 'Trip does not exist or you do not have permission to update it'
            }), 404
        
        # Validate update data
        validation = validate_trip_data(data, is_update=True)
        if not validation['valid']:
            return jsonify({
                'error': 'Validation failed',
                'details': validation['errors']
            }), 400
        
        # Update fields
        if 'destination' in data:
            trip.destination = data['destination'].strip()
        
        if 'start_date' in data:
            trip.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in data:
            trip.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'latitude' in data:
            trip.latitude = data['latitude']
        
        if 'longitude' in data:
            trip.longitude = data['longitude']
        
        if 'description' in data:
            trip.description = data['description'].strip() if data['description'] else None
        
        if 'budget' in data:
            trip.budget = data['budget']
        
        if 'status' in data:
            trip.status = data['status']
        
        if 'itinerary' in data:
            # Validate JSON if provided
            try:
                if data['itinerary']:
                    json.loads(data['itinerary']) if isinstance(data['itinerary'], str) else data['itinerary']
                trip.itinerary = data['itinerary']
            except json.JSONDecodeError:
                return jsonify({
                    'error': 'Invalid itinerary format',
                    'message': 'Itinerary must be valid JSON'
                }), 400
        
        trip.save()
        
        return jsonify({
            'message': 'Trip updated successfully',
            'trip': trip.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Trip update error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update trip',
            'message': 'An unexpected error occurred'
        }), 500

@trips_bp.route('/<int:trip_id>', methods=['DELETE'])
@AuthMiddleware.require_auth
def delete_trip(trip_id):
    """Delete a specific trip"""
    try:
        user = get_current_user()
        
        trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': 'Trip does not exist or you do not have permission to delete it'
            }), 404
        
        trip.delete()
        
        return jsonify({
            'message': 'Trip deleted successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Trip deletion error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete trip',
            'message': 'An unexpected error occurred'
        }), 500

@trips_bp.route('/stats', methods=['GET'])
@AuthMiddleware.require_auth
def get_trip_stats():
    """Get trip statistics for the authenticated user"""
    try:
        user = get_current_user()
        
        total_trips = Trip.query.filter_by(user_id=user.id).count()
        planned_trips = Trip.query.filter_by(user_id=user.id, status='planned').count()
        active_trips = Trip.query.filter_by(user_id=user.id, status='active').count()
        completed_trips = Trip.query.filter_by(user_id=user.id, status='completed').count()
        cancelled_trips = Trip.query.filter_by(user_id=user.id, status='cancelled').count()
        
        # Get upcoming trips
        today = date.today()
        upcoming_trips = Trip.query.filter(
            Trip.user_id == user.id,
            Trip.start_date > today,
            Trip.status.in_(['planned', 'active'])
        ).count()
        
        return jsonify({
            'stats': {
                'total_trips': total_trips,
                'planned_trips': planned_trips,
                'active_trips': active_trips,
                'completed_trips': completed_trips,
                'cancelled_trips': cancelled_trips,
                'upcoming_trips': upcoming_trips
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Trip stats error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve trip statistics'
        }), 500

@trips_bp.route('/<int:trip_id>/itinerary', methods=['GET'])
@AuthMiddleware.require_auth
def get_trip_itinerary(trip_id):
    """Get detailed itinerary for a specific trip"""
    try:
        user = get_current_user()
        
        trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': 'Trip does not exist or you do not have permission to view it'
            }), 404
        
        itinerary = ItineraryTemplate.parse_itinerary_from_storage(trip.itinerary)
        summary = ItineraryTemplate.get_itinerary_summary(itinerary)
        
        return jsonify({
            'trip_id': trip_id,
            'destination': trip.destination,
            'itinerary': itinerary,
            'summary': summary
        }), 200
        
    except Exception as e:
        logging.error(f"Get trip itinerary error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve trip itinerary'
        }), 500

@trips_bp.route('/<int:trip_id>/itinerary/generate', methods=['POST'])
@AuthMiddleware.require_auth
def generate_trip_itinerary(trip_id):
    """
    Generate or regenerate itinerary for an existing trip
    
    Expected JSON:
    {
        "destination_type": "city",
        "trip_style": "balanced",
        "replace_existing": true
    }
    """
    try:
        user = get_current_user()
        data = request.get_json() or {}
        
        trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': 'Trip does not exist or you do not have permission to modify it'
            }), 404
        
        # Check if itinerary already exists and replace_existing is False
        if trip.itinerary and not data.get('replace_existing', False):
            return jsonify({
                'error': 'Itinerary already exists',
                'message': 'Trip already has an itinerary. Set replace_existing to true to regenerate.'
            }), 409
        
        # Generate new itinerary
        destination_type = data.get('destination_type')
        default_itinerary = ItineraryTemplate.generate_default_itinerary(
            trip.destination, 
            trip.start_date, 
            trip.end_date, 
            destination_type
        )
        
        trip.itinerary = ItineraryTemplate.format_itinerary_for_storage(default_itinerary)
        trip.save()
        
        summary = ItineraryTemplate.get_itinerary_summary(default_itinerary)
        
        return jsonify({
            'message': 'Itinerary generated successfully',
            'trip_id': trip_id,
            'itinerary': default_itinerary,
            'summary': summary
        }), 200
        
    except Exception as e:
        logging.error(f"Generate trip itinerary error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to generate itinerary',
            'message': 'An unexpected error occurred'
        }), 500

@trips_bp.route('/itinerary/templates', methods=['GET'])
@AuthMiddleware.require_auth
def get_itinerary_templates():
    """Get available itinerary templates and destination types"""
    try:
        destination_types = list(ItineraryTemplate.DESTINATION_TYPES.keys())
        
        templates = {}
        for style in ['relaxed', 'balanced', 'adventurous', 'cultural']:
            templates[style] = ItineraryTemplate.generate_custom_itinerary_template(style)
        
        return jsonify({
            'destination_types': destination_types,
            'trip_styles': templates,
            'description': {
                'destination_types': 'Available destination types for itinerary generation',
                'trip_styles': 'Available trip styles with their characteristics'
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Get itinerary templates error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve itinerary templates'
        }), 500

# Error handlers for the trips blueprint
@trips_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'message': 'The request could not be understood'
    }), 400

@trips_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested trip was not found'
    }), 404

@trips_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
