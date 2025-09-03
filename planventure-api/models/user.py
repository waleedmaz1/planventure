from .base import BaseModel, db
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseModel):
    __tablename__ = 'users'
    
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Password reset fields
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    
    # JWT token tracking (optional - for token blacklisting)
    last_token_jti = db.Column(db.String(255), nullable=True)
    
    # Relationship to trips
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password=None):
        self.email = email.lower().strip()
        self.failed_login_attempts = 0
        if password:
            # Simple password validation and hashing
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long")
            self.password_hash = generate_password_hash(password)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        if len(password) < 8:
            return {'valid': False, 'errors': ['Password must be at least 8 characters long']}
        
        self.password_hash = generate_password_hash(password)
        return {'valid': True, 'errors': []}
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user instance to dictionary (excluding password_hash)"""
        data = super().to_dict()
        data.pop('password_hash', None)  # Never expose password hash
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email address"""
        return cls.query.filter_by(email=email.lower().strip()).first()
    
    def get_trips(self, status=None):
        """Get user's trips, optionally filtered by status"""
        if status:
            return [trip for trip in self.trips if trip.status == status]
        return self.trips
    
    def get_trips_count(self):
        """Get count of user's trips"""
        return len(self.trips)
    
    def generate_jwt_tokens(self):
        """Generate JWT access and refresh tokens for the user"""
        from utils.jwt_auth import JWTManager
        return JWTManager.generate_tokens(self.id, self.email)
    
    def is_account_locked(self):
        """Check if the account is currently locked"""
        from datetime import datetime
        return (self.account_locked_until and 
                self.account_locked_until > datetime.utcnow())
    
    def lock_account(self, duration_minutes=30):
        """Lock the account for a specified duration"""
        from datetime import datetime, timedelta
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.save()
    
    def unlock_account(self):
        """Unlock the account and reset failed login attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save()
    
    def increment_failed_login(self, max_attempts=5):
        """Increment failed login attempts and lock account if threshold reached"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.lock_account()
        self.save()
    
    def reset_failed_login_attempts(self):
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0
        self.save()
        """Unlock the account and reset failed login attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save()
    
    def increment_failed_login(self, max_attempts=5):
        """
        Increment failed login attempts and lock account if threshold reached
        
        Args:
            max_attempts (int): Maximum failed attempts before locking
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.lock_account()
        self.save()
    
    def reset_failed_login_attempts(self):
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0
        self.save()
    
    def generate_password_reset_token(self):
        """Generate JWT-based password reset token"""
        from utils.jwt_auth import JWTManager
        return JWTManager.generate_password_reset_token(self.id, self.email)
    
    def verify_password_reset_token(self, token):
        """Verify JWT-based password reset token"""
        from utils.jwt_auth import JWTManager
        payload = JWTManager.verify_password_reset_token(token)
        return payload and payload.get('user_id') == self.id
    
    def get_trips(self, status=None):
        """Get user's trips, optionally filtered by status"""
        if status:
            return [trip for trip in self.trips if trip.status == status]
        return self.trips
    
    def get_trips_count(self):
        """Get count of user's trips"""
        return len(self.trips)
    
    def generate_password_reset_token(self):
        """Generate JWT-based password reset token"""
        from utils.jwt_auth import JWTManager
        return JWTManager.generate_password_reset_token(self.id, self.email)
    
    def verify_password_reset_token(self, token):
        """Verify JWT-based password reset token"""
        from utils.jwt_auth import JWTManager
        payload = JWTManager.verify_password_reset_token(token)
        return payload and payload.get('user_id') == self.id
