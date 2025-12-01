from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, BookingRequest, BookingStatus, Subscription, SubscriptionStatus
from datetime import datetime, time
import pytz
import json

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/', methods=['GET'])
@jwt_required()
def get_bookings():
    """Get all booking requests for current user"""
    try:
        current_user_id = get_jwt_identity()
        bookings = BookingRequest.query.filter_by(user_id=current_user_id).order_by(BookingRequest.created_at.desc()).all()
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get specific booking request"""
    try:
        current_user_id = get_jwt_identity()
        booking = BookingRequest.query.filter_by(id=booking_id, user_id=current_user_id).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        return jsonify({'booking': booking.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking request"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user has active subscription
        subscription = Subscription.query.filter_by(user_id=current_user_id).first()
        if not subscription or subscription.status != SubscriptionStatus.ACTIVE:
            return jsonify({'error': 'Active subscription required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['origin', 'destination', 'departure_date']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get user's timezone
        user = User.query.get(current_user_id)
        user_tz = pytz.timezone(user.timezone)
        
        # Parse departure date and create scheduled time (midnight in user's timezone)
        departure_date = datetime.fromisoformat(data['departure_date']).date()
        scheduled_datetime = datetime.combine(departure_date, time(0, 0, 0))
        scheduled_datetime = user_tz.localize(scheduled_datetime)
        
        # Create booking request
        booking = BookingRequest(
            user_id=current_user_id,
            origin=data['origin'],
            destination=data['destination'],
            departure_date=departure_date,
            return_date=datetime.fromisoformat(data['return_date']).date() if data.get('return_date') else None,
            passengers=data.get('passengers', 1),
            primary_option=json.dumps(data.get('primary_option', {})),
            backup_option=json.dumps(data.get('backup_option', {})),
            max_price=data.get('max_price'),
            scheduled_time=scheduled_datetime,
            status=BookingStatus.PENDING
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking request created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """Update a booking request (only if pending)"""
    try:
        current_user_id = get_jwt_identity()
        booking = BookingRequest.query.filter_by(id=booking_id, user_id=current_user_id).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking.status != BookingStatus.PENDING:
            return jsonify({'error': 'Can only update pending bookings'}), 400
        
        data = request.get_json()
        
        # Update allowed fields
        if 'origin' in data:
            booking.origin = data['origin']
        if 'destination' in data:
            booking.destination = data['destination']
        if 'departure_date' in data:
            booking.departure_date = datetime.fromisoformat(data['departure_date']).date()
        if 'return_date' in data:
            booking.return_date = datetime.fromisoformat(data['return_date']).date() if data['return_date'] else None
        if 'passengers' in data:
            booking.passengers = data['passengers']
        if 'primary_option' in data:
            booking.primary_option = json.dumps(data['primary_option'])
        if 'backup_option' in data:
            booking.backup_option = json.dumps(data['backup_option'])
        if 'max_price' in data:
            booking.max_price = data['max_price']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking updated successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking request"""
    try:
        current_user_id = get_jwt_identity()
        booking = BookingRequest.query.filter_by(id=booking_id, user_id=current_user_id).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking.status in [BookingStatus.SUCCESS, BookingStatus.PROCESSING]:
            return jsonify({'error': 'Cannot cancel completed or processing bookings'}), 400
        
        booking.status = BookingStatus.CANCELED
        db.session.commit()
        
        return jsonify({'message': 'Booking canceled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
