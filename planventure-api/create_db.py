#!/usr/bin/env python3
"""
Database creation script for PlanVenture API
Run this script to create all database tables.

Prerequisites:
    pip install -r requirements.txt

Usage:
    python create_db.py
    python create_db.py drop  # to drop all tables
    python create_db.py reset  # to drop and recreate all tables
"""

import os
import sys

# Check if required packages are installed
try:
    from flask import Flask
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Required package not installed - {e}")
    print("\nPlease install the required dependencies:")
    print("pip install -r requirements.txt")
    print("\nOr install individually:")
    print("pip install flask flask-sqlalchemy python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    
    # Configure Flask app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///planventure.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    try:
        # Initialize database
        from models.base import db
        db.init_app(app)
        
        # Import all models to ensure they're registered
        from models import User, Trip
        
        return app, db
    except ImportError as e:
        print(f"Error importing models: {e}")
        print("Make sure the models directory and files exist.")
        sys.exit(1)

def create_tables():
    """Create all database tables"""
    try:
        app, db = create_app()
        
        with app.app_context():
            print("Creating database tables...")
            
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Verify tables were created
            try:
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                if tables:
                    print(f"✓ Created tables: {', '.join(tables)}")
                else:
                    print("⚠ No tables found after creation")
            except Exception as e:
                print(f"✓ Tables created, but couldn't verify: {e}")
                
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)

def drop_tables():
    """Drop all database tables"""
    try:
        app, db = create_app()
        
        with app.app_context():
            print("Dropping all database tables...")
            db.drop_all()
            print("✓ All tables dropped successfully!")
            
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        sys.exit(1)

def reset_database():
    """Drop and recreate all tables"""
    print("Resetting database...")
    drop_tables()
    create_tables()

def show_help():
    """Show usage instructions"""
    print(__doc__)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'drop':
            drop_tables()
        elif command == 'reset':
            reset_database()
        elif command in ['help', '-h', '--help']:
            show_help()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: drop, reset, help")
            print("Or run without arguments to create tables.")
    else:
        create_tables()
