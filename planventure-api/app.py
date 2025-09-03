from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Basic Flask configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///planventure.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Configuration
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '900'))  # 15 minutes
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '2592000'))  # 30 days

# Initialize extensions
from models.base import db
db.init_app(app)

# Import models after db initialization
from models import User, Trip

# Import middleware utilities
from utils.middleware import AuthMiddleware, get_current_user, is_authenticated

# Import and register blueprints
from routes import auth_bp, trips_bp
app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)

# Enhanced CORS Configuration for React Frontend
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS(app, 
    origins=cors_origins,
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allow_headers=[
        'Content-Type', 
        'Authorization', 
        'Access-Control-Allow-Credentials',
        'X-Requested-With',
        'Accept',
        'Origin'
    ],
    supports_credentials=True,
    expose_headers=['Content-Range', 'X-Content-Range'],
    max_age=3600
)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "database": "connected"})

# Example protected route using new middleware
@app.route('/protected')
@AuthMiddleware.require_auth
def protected_route():
    user = get_current_user()
    return jsonify({
        "message": "Access granted to protected route",
        "user": {
            "id": user.id,
            "email": user.email
        }
    })

@app.route('/public-or-private')
@AuthMiddleware.optional_auth
def flexible_route():
    if is_authenticated():
        user = get_current_user()
        return jsonify({
            "message": f"Hello {user.email}",
            "authenticated": True
        })
    else:
        return jsonify({
            "message": "Hello anonymous user",
            "authenticated": False
        })

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
    app.run(debug=True)
