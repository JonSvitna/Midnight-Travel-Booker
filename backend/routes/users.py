from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, TravelCredential
from utils.security import encrypt_data, decrypt_data

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'timezone' in data:
            user.timezone = data['timezone']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/credentials', methods=['POST'])
@jwt_required()
def save_travel_credentials():
    """Save encrypted travel site credentials"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        # Check if credentials already exist
        credential = TravelCredential.query.filter_by(user_id=current_user_id).first()
        
        if credential:
            # Update existing credentials
            credential.travel_site_username = encrypt_data(data['username'])
            credential.travel_site_password = encrypt_data(data['password'])
        else:
            # Create new credentials
            credential = TravelCredential(
                user_id=current_user_id,
                travel_site_username=encrypt_data(data['username']),
                travel_site_password=encrypt_data(data['password'])
            )
            db.session.add(credential)
        
        db.session.commit()
        
        return jsonify({'message': 'Credentials saved successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/credentials', methods=['GET'])
@jwt_required()
def check_credentials():
    """Check if user has saved travel credentials"""
    try:
        current_user_id = get_jwt_identity()
        credential = TravelCredential.query.filter_by(user_id=current_user_id).first()
        
        return jsonify({
            'has_credentials': credential is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/credentials', methods=['DELETE'])
@jwt_required()
def delete_credentials():
    """Delete travel site credentials"""
    try:
        current_user_id = get_jwt_identity()
        credential = TravelCredential.query.filter_by(user_id=current_user_id).first()
        
        if not credential:
            return jsonify({'error': 'No credentials found'}), 404
        
        db.session.delete(credential)
        db.session.commit()
        
        return jsonify({'message': 'Credentials deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
