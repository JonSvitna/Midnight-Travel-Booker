from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import enum

db = SQLAlchemy()

class SubscriptionTier(enum.Enum):
    BASIC = 'basic'
    STANDARD = 'standard'
    PREMIUM = 'premium'

class SubscriptionStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CANCELED = 'canceled'
    PAST_DUE = 'past_due'

class BookingStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILED = 'failed'
    CANCELED = 'canceled'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = db.relationship('Subscription', backref='user', uselist=False, cascade='all, delete-orphan')
    booking_requests = db.relationship('BookingRequest', backref='user', cascade='all, delete-orphan')
    travel_credentials = db.relationship('TravelCredential', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'timezone': self.timezone,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    tier = db.Column(Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.BASIC)
    status = db.Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.INACTIVE)
    stripe_customer_id = db.Column(db.String(100), unique=True)
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tier': self.tier.value,
            'status': self.status.value,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TravelCredential(db.Model):
    __tablename__ = 'travel_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    travel_site_username = db.Column(db.LargeBinary, nullable=False)  # Encrypted
    travel_site_password = db.Column(db.LargeBinary, nullable=False)  # Encrypted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BookingRequest(db.Model):
    __tablename__ = 'booking_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    
    # Travel details
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    passengers = db.Column(db.Integer, default=1)
    
    # Booking preferences
    primary_option = db.Column(db.Text)  # JSON stored as text
    backup_option = db.Column(db.Text)   # JSON stored as text
    max_price = db.Column(db.Numeric(10, 2))
    
    # Execution details
    scheduled_time = db.Column(db.DateTime, nullable=False)
    executed_at = db.Column(db.DateTime)
    result_message = db.Column(db.Text)
    booking_reference = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status.value,
            'origin': self.origin,
            'destination': self.destination,
            'departure_date': self.departure_date.isoformat(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'passengers': self.passengers,
            'max_price': float(self.max_price) if self.max_price else None,
            'scheduled_time': self.scheduled_time.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'result_message': self.result_message,
            'booking_reference': self.booking_reference,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }
