from flask import Blueprint, request, jsonify
from models import User
from models.base import db
from utils.validation import ValidationUtils, validate_json
from utils.jwt_auth import JWTManager
from utils.middleware import AuthMiddleware, get_current_user
import logging

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@validate_json(['email', 'password'])
def register():
    """
    User registration endpoint with email validation
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "securepassword123",
        "password_confirm": "securepassword123" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input data
        validation = ValidationUtils.validate_registration_data(data)
        if not validation['valid']:
            return jsonify({
                'error': 'Validation failed',
                'details': validation['errors']
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({
                'error': 'Registration failed',
                'message': 'An account with this email already exists'
            }), 409
        
        # Create new user
        try:
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.flush()  # Flush to get the ID without committing
            
            # Generate JWT tokens
            tokens = user.generate_jwt_tokens()
            
            # Commit the transaction
            db.session.commit()
            
            # Return success response
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'created_at': user.created_at.isoformat()
                },
                'tokens': tokens
            }), 201
            
        except ValueError as e:
            # Password validation error
            db.session.rollback()
            return jsonify({
                'error': 'Registration failed',
                'message': str(e)
            }), 400
        except Exception as e:
            # Database or other errors
            db.session.rollback()
            logging.error(f"User creation error: {str(e)}")
            return jsonify({
                'error': 'Registration failed',
                'message': 'Failed to create user account'
            }), 500
            
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'message': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/login', methods=['POST'])
@validate_json(['email', 'password'])
def login():
    """
    User login endpoint
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    """
    try:
        data = request.get_json()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.find_by_email(email)
        if not user:
            return jsonify({
                'error': 'Login failed',
                'message': 'Invalid email or password'
            }), 401
        
        # Check if account is locked
        if user.is_account_locked():
            return jsonify({
                'error': 'Account locked',
                'message': 'Account is temporarily locked due to too many failed login attempts'
            }), 423
        
        # Verify password
        if not user.check_password(password):
            user.increment_failed_login()
            return jsonify({
                'error': 'Login failed',
                'message': 'Invalid email or password'
            }), 401
        
        # Reset failed login attempts on successful login
        user.reset_failed_login_attempts()
        
        # Generate JWT tokens
        tokens = user.generate_jwt_tokens()
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            },
            'tokens': tokens
        }), 200
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Login failed',
            'message': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@validate_json(['refresh_token'])
def refresh_token():
    """
    Refresh access token using refresh token
    
    Expected JSON:
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    """
    try:
        data = request.get_json()
        refresh_token = data['refresh_token']
        
        # Generate new tokens
        new_tokens = JWTManager.refresh_access_token(refresh_token)
        
        if not new_tokens:
            return jsonify({
                'error': 'Token refresh failed',
                'message': 'Invalid or expired refresh token'
            }), 401
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'tokens': new_tokens
        }), 200
        
    except Exception as e:
        logging.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'Token refresh failed',
            'message': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/validate-email', methods=['POST'])
@validate_json(['email'])
def validate_email():
    """
    Validate email format and availability
    
    Expected JSON:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        email = data['email'].strip().lower()
        
        # Validate email format
        email_validation = ValidationUtils.validate_email(email)
        if not email_validation['valid']:
            return jsonify({
                'valid': False,
                'error': email_validation['error']
            }), 400
        
        # Check if email is already taken
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({
                'valid': False,
                'error': 'Email is already registered'
            }), 409
        
        return jsonify({
            'valid': True,
            'message': 'Email is available'
        }), 200
        
    except Exception as e:
        logging.error(f"Email validation error: {str(e)}")
        return jsonify({
            'error': 'Validation failed',
            'message': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@AuthMiddleware.require_auth
def get_current_user_info():
    """
    Get current user information (requires authentication)
    """
    try:
        user = get_current_user()
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'trips_count': user.get_trips_count()
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Get current user error: {str(e)}")
        return jsonify({
            'error': 'Failed to get user information'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@AuthMiddleware.require_auth
def update_profile():
    """
    Update user profile (requires authentication)
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Example: Update user email (with validation)
        if 'email' in data:
            new_email = data['email'].strip().lower()
            email_validation = ValidationUtils.validate_email(new_email)
            
            if not email_validation['valid']:
                return jsonify({
                    'error': 'Validation failed',
                    'message': email_validation['error']
                }), 400
            
            # Check if email is already taken by another user
            existing_user = User.find_by_email(new_email)
            if existing_user and existing_user.id != user.id:
                return jsonify({
                    'error': 'Email already in use',
                    'message': 'This email is already registered to another account'
                }), 409
            
            user.email = new_email
        
        user.save()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Profile update error: {str(e)}")
        return jsonify({
            'error': 'Failed to update profile'
        }), 500

# Error handlers for the auth blueprint
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'message': 'The request could not be understood'
    }), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401

@auth_bp.errorhandler(409)
def conflict(error):
    return jsonify({
        'error': 'Conflict',
        'message': 'Resource already exists'
    }), 409

@auth_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
