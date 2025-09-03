from .base import BaseModel, db
from datetime import datetime
from decimal import Decimal

class Trip(BaseModel):
    __tablename__ = 'trips'
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Trip details
    destination = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Coordinates for the destination
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Itinerary stored as JSON text
    itinerary = db.Column(db.Text, nullable=True)
    
    # Trip status
    status = db.Column(db.String(50), default='planned')  # planned, active, completed, cancelled
    
    # Trip description/notes
    description = db.Column(db.Text, nullable=True)
    
    # Budget information
    budget = db.Column(db.Numeric(10, 2), nullable=True)
    
    def __init__(self, user_id, destination, start_date, end_date, **kwargs):
        self.user_id = user_id
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        
        # Set optional fields
        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')
        self.itinerary = kwargs.get('itinerary')
        self.description = kwargs.get('description')
        self.budget = kwargs.get('budget')
        self.status = kwargs.get('status', 'planned')
    
    def to_dict(self):
        """Convert trip instance to dictionary"""
        data = super().to_dict()
        # Convert date objects to strings for JSON serialization
        if data.get('start_date'):
            data['start_date'] = data['start_date'].isoformat()
        if data.get('end_date'):
            data['end_date'] = data['end_date'].isoformat()
        # Convert decimal to float for JSON serialization
        if data.get('budget'):
            data['budget'] = float(data['budget'])
        return data
    
    @property
    def duration_days(self):
        """Calculate trip duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    @property
    def is_active(self):
        """Check if trip is currently active"""
        today = datetime.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'active'
    
    @property
    def is_upcoming(self):
        """Check if trip is upcoming"""
        today = datetime.now().date()
        return self.start_date > today and self.status == 'planned'
    
    @property
    def is_past(self):
        """Check if trip is in the past"""
        today = datetime.now().date()
        return self.end_date < today
    
    def __repr__(self):
        return f'<Trip {self.destination} ({self.start_date} to {self.end_date})>'
    
    @classmethod
    def get_user_trips(cls, user_id, status=None):
        """Get all trips for a specific user, optionally filtered by status"""
        query = cls.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.start_date.desc()).all()
    
    @classmethod
    def get_upcoming_trips(cls, user_id):
        """Get upcoming trips for a user"""
        today = datetime.now().date()
        return cls.query.filter(
            cls.user_id == user_id,
            cls.start_date > today,
            cls.status.in_(['planned', 'active'])
        ).order_by(cls.start_date.asc()).all()
