import os
from flask_cors import CORS

class CORSConfig:
    """CORS configuration utility for React frontend integration"""
    
    @staticmethod
    def get_cors_origins():
        """
        Get CORS origins from environment variables
        
        Returns:
            list: List of allowed origins
        """
        origins_env = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
        
        # Parse origins from comma-separated string
        origins = [origin.strip() for origin in origins_env.split(',') if origin.strip()]
        
        # Add default development origins if not present
        default_origins = [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3001'
        ]
        
        for origin in default_origins:
            if origin not in origins:
                origins.append(origin)
        
        return origins
    
    @staticmethod
    def get_cors_config():
        """
        Get complete CORS configuration
        
        Returns:
            dict: CORS configuration options
        """
        return {
            'origins': CORSConfig.get_cors_origins(),
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
            'allow_headers': [
                'Content-Type',
                'Authorization', 
                'Access-Control-Allow-Credentials',
                'X-Requested-With',
                'Accept',
                'Origin',
                'X-API-Key',
                'Cache-Control'
            ],
            'expose_headers': [
                'Content-Range', 
                'X-Content-Range',
                'X-Total-Count',
                'X-Page-Count'
            ],
            'supports_credentials': True,
            'max_age': 3600
        }
    
    @staticmethod
    def configure_cors(app):
        """
        Configure CORS for Flask app
        
        Args:
            app: Flask application instance
        """
        config = CORSConfig.get_cors_config()
        CORS(app, **config)
        
        # Add CORS headers to all responses
        @app.after_request
        def after_request(response):
            origin = request.headers.get('Origin')
            if origin in config['origins']:
                response.headers.add('Access-Control-Allow-Origin', origin)
                response.headers.add('Access-Control-Allow-Credentials', 'true')
                response.headers.add('Access-Control-Allow-Methods', ', '.join(config['methods']))
                response.headers.add('Access-Control-Allow-Headers', ', '.join(config['allow_headers']))
            
            return response
    
    @staticmethod
    def is_origin_allowed(origin):
        """
        Check if an origin is allowed
        
        Args:
            origin (str): Origin to check
            
        Returns:
            bool: True if origin is allowed
        """
        allowed_origins = CORSConfig.get_cors_origins()
        return origin in allowed_origins
    
    @staticmethod
    def get_development_config():
        """
        Get CORS configuration for development environment
        
        Returns:
            dict: Development CORS configuration
        """
        return {
            'origins': ['*'],  # Allow all origins in development
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
            'allow_headers': ['*'],
            'supports_credentials': True,
            'max_age': 86400
        }
    
    @staticmethod
    def get_production_config():
        """
        Get CORS configuration for production environment
        
        Returns:
            dict: Production CORS configuration
        """
        return {
            'origins': CORSConfig.get_cors_origins(),
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': [
                'Content-Type',
                'Authorization',
                'X-Requested-With',
                'Accept',
                'Origin'
            ],
            'expose_headers': ['Content-Range', 'X-Content-Range'],
            'supports_credentials': True,
            'max_age': 3600
        }
