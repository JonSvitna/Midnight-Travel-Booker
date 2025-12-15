"""
Seed script to populate the database with fake booking data for testing.
Usage: python seed_bookings.py [num_bookings]
"""
import sys
import random
from datetime import datetime, timedelta
from faker import Faker
from app import create_app
from models import db, User, BookingRequest, BookingStatus, Subscription, SubscriptionStatus, SubscriptionTier
import bcrypt
import pytz

fake = Faker()

# Popular travel destinations
DESTINATIONS = [
    'New York', 'Los Angeles', 'Chicago', 'Miami', 'San Francisco',
    'Las Vegas', 'Seattle', 'Boston', 'Denver', 'Austin',
    'Orlando', 'Portland', 'Nashville', 'San Diego', 'Phoenix',
    'London', 'Paris', 'Tokyo', 'Dubai', 'Barcelona',
    'Rome', 'Amsterdam', 'Sydney', 'Singapore', 'Bangkok'
]

def create_demo_user(app):
    """Create or get a demo user for testing"""
    with app.app_context():
        user = User.query.filter_by(email='demo@example.com').first()
        
        if not user:
            password_hash = bcrypt.hashpw('demo123'.encode('utf-8'), bcrypt.gensalt())
            user = User(
                email='demo@example.com',
                password_hash=password_hash.decode('utf-8'),
                first_name='Demo',
                last_name='User',
                timezone='America/New_York',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            print(f"Created demo user: demo@example.com / demo123")
        
        # Ensure user has an active subscription
        subscription = Subscription.query.filter_by(user_id=user.id).first()
        if not subscription:
            subscription = Subscription(
                user_id=user.id,
                tier=SubscriptionTier.PREMIUM,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(subscription)
            db.session.commit()
            print(f"Created active subscription for demo user")
        elif subscription.status != SubscriptionStatus.ACTIVE:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.tier = SubscriptionTier.PREMIUM
            subscription.current_period_start = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            db.session.commit()
            print(f"Updated subscription to active for demo user")
        
        return user

def generate_fake_bookings(app, user_id, num_bookings=20):
    """Generate fake booking data"""
    with app.app_context():
        user = User.query.get(user_id)
        user_tz = pytz.timezone(user.timezone)
        
        bookings_created = 0
        statuses = [
            (BookingStatus.PENDING, 0.3),      # 30% pending
            (BookingStatus.PROCESSING, 0.1),    # 10% processing
            (BookingStatus.SUCCESS, 0.4),       # 40% success
            (BookingStatus.FAILED, 0.1),        # 10% failed
            (BookingStatus.CANCELED, 0.1)       # 10% canceled
        ]
        
        for i in range(num_bookings):
            # Random status based on weights
            status = random.choices(
                [s[0] for s in statuses],
                weights=[s[1] for s in statuses]
            )[0]
            
            # Generate random dates
            # Past bookings for completed/failed/canceled
            # Future bookings for pending/processing
            if status in [BookingStatus.SUCCESS, BookingStatus.FAILED, BookingStatus.CANCELED]:
                # Past bookings (last 60 days)
                days_ago = random.randint(1, 60)
                departure_date = datetime.now().date() - timedelta(days=days_ago)
            else:
                # Future bookings (next 90 days)
                days_ahead = random.randint(1, 90)
                departure_date = datetime.now().date() + timedelta(days=days_ahead)
            
            # Random return date (60% of bookings have return)
            return_date = None
            if random.random() < 0.6:
                return_date = departure_date + timedelta(days=random.randint(3, 14))
            
            # Select random origin and destination (ensure they're different)
            origin = random.choice(DESTINATIONS)
            destination = random.choice([d for d in DESTINATIONS if d != origin])
            
            # Schedule time at midnight on departure date
            scheduled_datetime = datetime.combine(departure_date, datetime.min.time())
            scheduled_datetime = user_tz.localize(scheduled_datetime)
            
            # Executed time for completed bookings
            executed_at = None
            result_message = None
            booking_reference = None
            
            if status == BookingStatus.SUCCESS:
                executed_at = scheduled_datetime + timedelta(minutes=random.randint(1, 10))
                result_message = "Booking completed successfully"
                booking_reference = fake.bothify(text='??######', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            elif status == BookingStatus.FAILED:
                executed_at = scheduled_datetime + timedelta(minutes=random.randint(1, 10))
                failures = [
                    "No available flights found within budget",
                    "Travel site authentication failed",
                    "Requested dates not available",
                    "Maximum price exceeded for available options",
                    "Unable to complete booking due to site error"
                ]
                result_message = random.choice(failures)
            elif status == BookingStatus.CANCELED:
                result_message = "Booking canceled by user"
            elif status == BookingStatus.PROCESSING:
                result_message = "Booking in progress..."
            
            # Random number of passengers
            passengers = random.choices([1, 2, 3, 4], weights=[0.4, 0.4, 0.15, 0.05])[0]
            
            # Random max price (if specified)
            max_price = None
            if random.random() < 0.7:  # 70% have max price
                max_price = random.choice([300, 400, 500, 600, 800, 1000, 1500])
            
            booking = BookingRequest(
                user_id=user_id,
                status=status,
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                passengers=passengers,
                max_price=max_price,
                scheduled_time=scheduled_datetime,
                executed_at=executed_at,
                result_message=result_message,
                booking_reference=booking_reference
            )
            
            db.session.add(booking)
            bookings_created += 1
        
        db.session.commit()
        print(f"Successfully created {bookings_created} fake bookings for user {user.email}")

def main():
    # Get number of bookings from command line (default: 20)
    num_bookings = 20
    if len(sys.argv) > 1:
        try:
            num_bookings = int(sys.argv[1])
        except ValueError:
            print("Invalid number of bookings. Using default: 20")
    
    app = create_app()
    
    print(f"Creating fake booking data...")
    print(f"Number of bookings to create: {num_bookings}")
    
    # Create or get demo user and get the user_id
    with app.app_context():
        user = User.query.filter_by(email='demo@example.com').first()
        if not user:
            user = create_demo_user(app)
            # Refresh to get the user after commit
            user = User.query.filter_by(email='demo@example.com').first()
        user_id = user.id
    
    # Generate fake bookings
    generate_fake_bookings(app, user_id, num_bookings)
    
    print("\nFake data seeding completed!")
    print("\nYou can now log in with:")
    print("  Email: demo@example.com")
    print("  Password: demo123")

if __name__ == '__main__':
    main()
