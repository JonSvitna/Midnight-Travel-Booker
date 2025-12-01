from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
from models import db, BookingRequest, BookingStatus
from services.booking_automation import BookingAutomation
from services.notification import NotificationService

scheduler = BackgroundScheduler()

def check_and_execute_bookings(app):
    """Check for pending bookings and execute them if it's time"""
    with app.app_context():
        try:
            now = datetime.utcnow()
            
            # Find all pending bookings scheduled for execution within the next minute
            pending_bookings = BookingRequest.query.filter(
                BookingRequest.status == BookingStatus.PENDING,
                BookingRequest.scheduled_time <= now + timedelta(minutes=1),
                BookingRequest.scheduled_time > now - timedelta(minutes=5)
            ).all()
            
            for booking in pending_bookings:
                try:
                    # Execute booking automation
                    automation = BookingAutomation(booking, app.app_context())
                    success = automation.execute()
                    
                    # Send notification
                    notification_service = NotificationService(app)
                    notification_service.send_booking_result(booking, success)
                    
                except Exception as e:
                    print(f"Error executing booking {booking.id}: {e}")
                    booking.status = BookingStatus.FAILED
                    booking.result_message = f"Execution error: {str(e)}"
                    db.session.commit()
                    
        except Exception as e:
            print(f"Error in booking scheduler: {e}")

def start_scheduler(app):
    """Start the APScheduler for booking automation"""
    # Run check every minute
    scheduler.add_job(
        func=lambda: check_and_execute_bookings(app),
        trigger=CronTrigger(minute='*'),
        id='booking_checker',
        name='Check and execute pending bookings',
        replace_existing=True
    )
    
    scheduler.start()
    print("Booking scheduler started")

def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    print("Booking scheduler stopped")
