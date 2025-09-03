from functools import wraps
from flask import request, jsonify, g
from utils.jwt_auth import JWTManager
from models import User
import logging

class AuthMiddleware:
    """Authentication middleware for route protection"""
    
    @staticmethod
    def require_auth(f):
        """
        Middleware decorator to require authentication for routes
        
        Usage:
            @app.route('/protected')
            @AuthMiddleware.require_auth
            def protected_route():
                user = g.current_user
                return jsonify({'user_id': user.id})
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get token from Authorization header
                auth_header = request.headers.get('Authorization')
                token = JWTManager.extract_token_from_header(auth_header)
                
                if not token:
                    return jsonify({
                        'error': 'Authentication required',
                        'message': 'Missing or invalid authorization header'
                    }), 401
                
                # Decode and validate token
                payload = JWTManager.decode_token(token, token_type='access')
                
                if not payload:
                    return jsonify({
                        'error': 'Authentication failed',
                        'message': 'Invalid or expired token'
                    }), 401
                
                # Get user from database
                user = User.query.get(payload['user_id'])
                if not user:
                    return jsonify({
                        'error': 'Authentication failed',
                        'message': 'User not found'
                    }), 401
                
                # Check if account is locked
                if user.is_account_locked():
                    return jsonify({
                        'error': 'Account locked',
                        'message': 'Account is temporarily locked'
                    }), 423
                
                # Set user in Flask's g object for easy access
                g.current_user = user
                g.token_payload = payload
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logging.error(f"Authentication middleware error: {str(e)}")
                return jsonify({
                    'error': 'Authentication failed',
                    'message': 'An error occurred during authentication'
                }), 500
        
        return decorated_function
    
    @staticmethod
    def optional_auth(f):
        """
        Middleware decorator for optional authentication
        Sets g.current_user if valid token is provided, otherwise None
        
        Usage:
            @app.route('/public-or-private')
            @AuthMiddleware.optional_auth
            def flexible_route():
                if g.current_user:
                    return jsonify({'message': f'Hello {g.current_user.email}'})
                return jsonify({'message': 'Hello anonymous user'})
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Initialize as None
                g.current_user = None
                g.token_payload = None
                
                # Get token from Authorization header
                auth_header = request.headers.get('Authorization')
                token = JWTManager.extract_token_from_header(auth_header)
                
                if token:
                    # Try to decode and validate token
                    payload = JWTManager.decode_token(token, token_type='access')
                    
                    if payload:
                        # Get user from database
                        user = User.query.get(payload['user_id'])
                        if user and not user.is_account_locked():
                            g.current_user = user
                            g.token_payload = payload
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logging.error(f"Optional auth middleware error: {str(e)}")
                # Don't fail on optional auth errors, just proceed without auth
                g.current_user = None
                g.token_payload = None
                return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def require_roles(*roles):
        """
        Middleware decorator to require specific user roles
        (Future enhancement - requires role system in User model)
        
        Usage:
            @app.route('/admin-only')
            @AuthMiddleware.require_auth
            @AuthMiddleware.require_roles('admin')
            def admin_route():
                return jsonify({'message': 'Admin access granted'})
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # This assumes g.current_user is already set by require_auth
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({
                        'error': 'Authentication required',
                        'message': 'User not authenticated'
                    }), 401
                
                # Check if user has required roles (placeholder for future implementation)
                user_roles = getattr(g.current_user, 'roles', [])
                if not any(role in user_roles for role in roles):
                    return jsonify({
                        'error': 'Access denied',
                        'message': 'Insufficient permissions'
                    }), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    @staticmethod
    def rate_limit(max_requests=100, per_minutes=60):
        """
        Simple rate limiting middleware (basic implementation)
        
        Usage:
            @app.route('/api/endpoint')
            @AuthMiddleware.rate_limit(max_requests=50, per_minutes=15)
            def limited_route():
                return jsonify({'data': 'response'})
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Basic rate limiting logic (you might want to use Redis for production)
                client_ip = request.remote_addr
                
                # For now, just log the request (implement actual rate limiting as needed)
                logging.info(f"Rate limit check for {client_ip} on {request.endpoint}")
                
                # TODO: Implement actual rate limiting with Redis or similar
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

# Convenience functions for common patterns
def get_current_user():
    """Get the current authenticated user from Flask's g object"""
    return getattr(g, 'current_user', None)

def get_current_user_id():
    """Get the current authenticated user's ID"""
    user = get_current_user()
    return user.id if user else None

def is_authenticated():
    """Check if current request is authenticated"""
    return get_current_user() is not None

def require_auth_json():
    """Return JSON error response for authentication requirement"""
    return jsonify({
        'error': 'Authentication required',
        'message': 'This endpoint requires authentication'
    }), 401
