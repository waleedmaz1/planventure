import re
from flask import request, jsonify
from functools import wraps

class ValidationUtils:
    """Utility class for input validation"""
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format
        
        Args:
            email (str): Email address to validate
            
        Returns:
            dict: Validation result
        """
        if not email:
            return {'valid': False, 'error': 'Email is required'}
        
        if len(email) > 254:
            return {'valid': False, 'error': 'Email is too long'}
        
        if not ValidationUtils.EMAIL_REGEX.match(email):
            return {'valid': False, 'error': 'Invalid email format'}
        
        # Check for common disposable email domains
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]
        
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return {'valid': False, 'error': 'Disposable email addresses are not allowed'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_registration_data(data):
        """
        Validate user registration data
        
        Args:
            data (dict): Registration data
            
        Returns:
            dict: Validation result with errors
        """
        errors = {}
        
        # Validate email
        email = data.get('email', '').strip()
        email_validation = ValidationUtils.validate_email(email)
        if not email_validation['valid']:
            errors['email'] = email_validation['error']
        
        # Validate password
        password = data.get('password', '')
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        
        # Validate password confirmation (only if provided)
        password_confirm = data.get('password_confirm')
        if password_confirm is not None and password != password_confirm:
            errors['password_confirm'] = 'Passwords do not match'
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

def validate_json(required_fields=None):
    """
    Decorator to validate JSON request data
    
    Args:
        required_fields (list): List of required field names
        
    Usage:
        @validate_json(['email', 'password'])
        def register():
            data = request.get_json()
            # data is guaranteed to have email and password fields
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or not data[field]:
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
