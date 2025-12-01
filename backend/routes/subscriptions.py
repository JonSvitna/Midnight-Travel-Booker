from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Subscription, SubscriptionStatus
import stripe
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('/', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get current user's subscription"""
    try:
        current_user_id = get_jwt_identity()
        subscription = Subscription.query.filter_by(user_id=current_user_id).first()
        
        if not subscription:
            return jsonify({'subscription': None}), 200
        
        return jsonify({'subscription': subscription.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        tier = data.get('tier', 'basic')
        
        # Map tier to Stripe price ID
        price_map = {
            'basic': Config.STRIPE_PRICE_BASIC,
            'standard': Config.STRIPE_PRICE_STANDARD,
            'premium': Config.STRIPE_PRICE_PREMIUM
        }
        
        price_id = price_map.get(tier)
        if not price_id:
            return jsonify({'error': 'Invalid subscription tier'}), 400
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=data.get('email'),
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{Config.APP_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{Config.APP_URL}/pricing",
            metadata={
                'user_id': current_user_id,
                'tier': tier
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
    
    elif event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']
        handle_subscription_updated(subscription_data)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object']
        handle_subscription_deleted(subscription_data)
    
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return jsonify({'status': 'success'}), 200

def handle_checkout_completed(session):
    """Handle successful checkout completion"""
    try:
        user_id = session['metadata']['user_id']
        tier = session['metadata']['tier']
        
        # Get Stripe subscription
        stripe_subscription = stripe.Subscription.retrieve(session['subscription'])
        
        # Create or update subscription in database
        subscription = Subscription.query.filter_by(user_id=user_id).first()
        
        if subscription:
            subscription.tier = tier
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.stripe_customer_id = session['customer']
            subscription.stripe_subscription_id = session['subscription']
            subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
            subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
        else:
            subscription = Subscription(
                user_id=user_id,
                tier=tier,
                status=SubscriptionStatus.ACTIVE,
                stripe_customer_id=session['customer'],
                stripe_subscription_id=session['subscription'],
                current_period_start=datetime.fromtimestamp(stripe_subscription['current_period_start']),
                current_period_end=datetime.fromtimestamp(stripe_subscription['current_period_end'])
            )
            db.session.add(subscription)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error handling checkout completion: {e}")

def handle_subscription_updated(subscription_data):
    """Handle subscription update"""
    try:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE if subscription_data['status'] == 'active' else SubscriptionStatus.INACTIVE
            subscription.current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
            subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        print(f"Error handling subscription update: {e}")

def handle_subscription_deleted(subscription_data):
    """Handle subscription cancellation"""
    try:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELED
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        print(f"Error handling subscription deletion: {e}")

def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        subscription = Subscription.query.filter_by(
            stripe_customer_id=invoice['customer']
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        print(f"Error handling payment failure: {e}")

from datetime import datetime
