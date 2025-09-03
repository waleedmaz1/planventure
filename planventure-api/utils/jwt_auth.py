import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
import secrets

class JWTManager:
    """JWT token management utility class"""
    
    @staticmethod
    def generate_tokens(user_id, email):
        """
        Generate access and refresh tokens for a user
        
        Args:
            user_id (int): User ID
            email (str): User email
            
        Returns:
            dict: Dictionary containing access_token and refresh_token
        """
        now = datetime.utcnow()
        
        # Access token payload (short-lived: 15 minutes)
        access_payload = {
            'user_id': user_id,
            'email': email,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(minutes=15),
            'jti': secrets.token_hex(16)  # JWT ID for token blacklisting
        }
        
        # Refresh token payload (long-lived: 30 days)
        refresh_payload = {
            'user_id': user_id,
            'email': email,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=30),
            'jti': secrets.token_hex(16)
        }
        
        secret_key = current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        access_token = jwt.encode(access_payload, secret_key, algorithm=algorithm)
        refresh_token = jwt.encode(refresh_payload, secret_key, algorithm=algorithm)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 900,  # 15 minutes in seconds
            'expires_at': access_payload['exp'].isoformat()
        }
    
    @staticmethod
    def decode_token(token, token_type='access'):
        """
        Decode and validate a JWT token
        
        Args:
            token (str): JWT token to decode
            token_type (str): Expected token type ('access' or 'refresh')
            
        Returns:
            dict: Decoded token payload or None if invalid
        """
        try:
            secret_key = current_app.config['SECRET_KEY']
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            
            # Verify token type
            if payload.get('type') != token_type:
                return None
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Generate a new access token using a valid refresh token
        
        Args:
            refresh_token (str): Valid refresh token
            
        Returns:
            dict: New token data or None if refresh token is invalid
        """
        payload = JWTManager.decode_token(refresh_token, token_type='refresh')
        
        if not payload:
            return None
        
        # Generate new access token
        return JWTManager.generate_tokens(payload['user_id'], payload['email'])
    
    @staticmethod
    def extract_token_from_header(authorization_header):
        """
        Extract JWT token from Authorization header
        
        Args:
            authorization_header (str): Authorization header value
            
        Returns:
            str: JWT token or None if not found
        """
        if not authorization_header:
            return None
        
        try:
            scheme, token = authorization_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                return None
            return token
        except ValueError:
            return None
    
    @staticmethod
    def generate_password_reset_token(user_id, email):
        """
        Generate a password reset token
        
        Args:
            user_id (int): User ID
            email (str): User email
            
        Returns:
            str: Password reset token
        """
        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'password_reset',
            'iat': now,
            'exp': now + timedelta(hours=1),  # Reset token expires in 1 hour
            'jti': secrets.token_hex(16)
        }
        
        secret_key = current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        return jwt.encode(payload, secret_key, algorithm=algorithm)
    
    @staticmethod
    def verify_password_reset_token(token):
        """
        Verify a password reset token
        
        Args:
            token (str): Password reset token
            
        Returns:
            dict: Token payload or None if invalid
        """
        return JWTManager.decode_token(token, token_type='password_reset')

def jwt_required(f):
    """
    Decorator to require valid JWT token for route access
    
    Usage:
        @app.route('/protected')
        @jwt_required
        def protected_route():
            return jsonify({'message': 'Access granted'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        token = JWTManager.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        # Decode and validate token
        payload = JWTManager.decode_token(token, token_type='access')
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        request.current_user = {
            'user_id': payload['user_id'],
            'email': payload['email']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def jwt_optional(f):
    """
    Decorator to optionally validate JWT token for route access
    If token is provided and valid, user info is added to request context
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        token = JWTManager.extract_token_from_header(auth_header)
        
        request.current_user = None
        
        if token:
            payload = JWTManager.decode_token(token, token_type='access')
            if payload:
                request.current_user = {
                    'user_id': payload['user_id'],
                    'email': payload['email']
                }
        
        return f(*args, **kwargs)
    
    return decorated_function
