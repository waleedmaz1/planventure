from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model class with common fields and methods"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Save the current instance to the database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the current instance from the database"""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
