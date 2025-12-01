# Backend Email Notification Flow Schema

## Overview
The email notification system uses SendGrid to send transactional emails for user onboarding and booking results.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Email Flow Architecture                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Trigger    │────────▶│   Service    │────────▶│   SendGrid   │
│   Events     │         │   Layer      │         │     API      │
└──────────────┘         └──────────────┘         └──────────────┘
                                │
                                │ Uses
                                ▼
                         ┌──────────────┐
                         │   Config &   │
                         │  Templates   │
                         └──────────────┘
```

---

## Flow 1: Welcome Email (New User Signup)

```
┌─────────────┐
│   User      │
│  Signup     │
│  (POST)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  routes/auth.py::signup()               │
│  ├─ Validate user data                  │
│  ├─ Hash password with bcrypt           │
│  ├─ Create user in database             │
│  └─ Commit to database                  │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  NotificationService.send_welcome_email │
│  ├─ Check if SendGrid configured        │
│  ├─ Generate HTML email template        │
│  │   └─ Welcome message                 │
│  │   └─ Next steps (subscribe, etc)     │
│  ├─ Create Mail object                  │
│  └─ Send via SendGrid API               │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           SendGrid API                  │
│  ├─ Validates API key                   │
│  ├─ Validates sender email              │
│  ├─ Queues email for delivery           │
│  └─ Returns response (202 = success)    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           User's Inbox                  │
│  Welcome to Midnight Travel Booker!     │
└─────────────────────────────────────────┘
```

### Code Flow:
```python
# 1. User hits signup endpoint
POST /api/auth/signup
{
  "email": "user@example.com",
  "password": "secure123",
  "first_name": "John"
}

# 2. In routes/auth.py
@auth_bp.route('/signup', methods=['POST'])
def signup():
    # ... validation & user creation ...
    db.session.commit()
    
    # Trigger welcome email
    notif_service = NotificationService(current_app)
    notif_service.send_welcome_email(
        user.email, 
        user.first_name
    )
    
    return response

# 3. In services/notification.py
def send_welcome_email(self, user_email, user_name):
    if not self.sg:
        return  # Skip if not configured
    
    message = Mail(
        from_email=Config.SENDGRID_FROM_EMAIL,
        to_emails=user_email,
        subject="Welcome to Midnight Travel Booker!",
        html_content=html_template
    )
    
    self.sg.send(message)  # ← SendGrid API call
```

---

## Flow 2: Booking Result Email (Success/Failure)

```
┌──────────────┐
│   Midnight   │
│   (00:00)    │  ← APScheduler Cron Job
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  services/scheduler.py                  │
│  check_and_execute_bookings()           │
│  ├─ Query pending bookings              │
│  │   WHERE scheduled_time <= now        │
│  ├─ For each booking:                   │
│  │   └─ Execute automation              │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  services/booking_automation.py         │
│  BookingAutomation.execute()            │
│  ├─ Launch headless browser             │
│  ├─ Login to travel site                │
│  ├─ Search for travel options           │
│  ├─ Find lowest price                   │
│  ├─ Check if price <= max_price         │
│  └─ Complete booking (or fail)          │
└──────┬──────────────────────────────────┘
       │
       ▼ (Returns: success=True/False)
       │
┌─────────────────────────────────────────┐
│  services/scheduler.py (continued)      │
│  ├─ Update booking status in DB         │
│  │   └─ 'success' or 'failed'           │
│  │   └─ Save booking_reference          │
│  │   └─ Save result_message             │
│  └─ Trigger notification                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  NotificationService.send_booking_result│
│  ├─ Check if SendGrid configured        │
│  ├─ Fetch user from database            │
│  ├─ Generate HTML template              │
│  │   ├─ Success: Green header, details  │
│  │   └─ Failure: Red header, error msg  │
│  ├─ Include booking details:            │
│  │   ├─ Route (origin → destination)    │
│  │   ├─ Dates (departure, return)       │
│  │   ├─ Passengers count                │
│  │   ├─ Booking reference (if success)  │
│  │   └─ Result message                  │
│  └─ Send via SendGrid API               │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           SendGrid API                  │
│  ├─ Validates and queues email          │
│  └─ Returns 202 Accepted                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           User's Inbox                  │
│  Booking Successful ✓ (or Failed ✗)     │
└─────────────────────────────────────────┘
```

### Code Flow:
```python
# 1. Scheduler runs every minute
@scheduler.scheduled_job('interval', minutes=1)
def check_and_execute_bookings():
    pending_bookings = BookingRequest.query.filter(
        BookingRequest.status == 'pending',
        BookingRequest.scheduled_time <= datetime.now()
    ).all()
    
    for booking in pending_bookings:
        # 2. Execute automation
        automation = BookingAutomation(booking)
        success, message, reference = automation.execute()
        
        # 3. Update database
        booking.status = 'success' if success else 'failed'
        booking.result_message = message
        booking.booking_reference = reference
        db.session.commit()
        
        # 4. Send notification
        notif_service = NotificationService(current_app)
        notif_service.send_booking_result(booking, success)

# 5. In services/notification.py
def send_booking_result(self, booking, success):
    if not self.sg:
        return
    
    user = User.query.get(booking.user_id)
    subject = "Booking Successful ✓" if success else "Booking Failed ✗"
    
    message = Mail(
        from_email=Config.SENDGRID_FROM_EMAIL,
        to_emails=user.email,
        subject=subject,
        html_content=self._get_booking_result_template(...)
    )
    
    self.sg.send(message)
```

---

## Data Models Involved

```python
# User Model
class User:
    id: int
    email: str              # ← Email recipient
    first_name: str         # ← Personalization
    password_hash: str
    created_at: datetime

# BookingRequest Model
class BookingRequest:
    id: int
    user_id: int           # ← Links to User
    origin: str            # ← Email details
    destination: str       # ← Email details
    departure_date: date   # ← Email details
    return_date: date      # ← Email details (optional)
    passengers: int        # ← Email details
    max_price: float
    status: str            # ← pending/success/failed
    result_message: str    # ← Shown in email
    booking_reference: str # ← Shown in email (if success)
    scheduled_time: datetime
```

---

## Configuration Required

```python
# config.py
class Config:
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    # Example: 'SG.abc123...'
    
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
    # Example: 'noreply@midnighttravel.com'
    # Must be verified in SendGrid
    
    APP_URL = os.getenv('APP_URL')
    # Example: 'https://midnight-travel-frontend.onrender.com'
    # Used for "View Dashboard" link in emails
```

---

## Email Templates

### Welcome Email Template
```html
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: #2563eb;">Welcome to Midnight Travel Booker!</h2>
    <p>Hi {user_name},</p>
    <p>Thank you for joining!</p>
    <h3>Next Steps:</h3>
    <ol>
      <li>Subscribe to a plan</li>
      <li>Save travel credentials</li>
      <li>Create booking request</li>
    </ol>
  </body>
</html>
```

### Booking Success Email Template
```html
<html>
  <body>
    <div style="background-color: #10b981; color: white; padding: 20px;">
      <h1>Booking ✓</h1>
      <p>Successfully Completed</p>
    </div>
    
    <div style="padding: 20px;">
      <h2>Hi {user.first_name},</h2>
      <p>Your booking was completed successfully!</p>
      
      <table>
        <tr><td>Route:</td><td>{origin} → {destination}</td></tr>
        <tr><td>Departure:</td><td>{departure_date}</td></tr>
        <tr><td>Passengers:</td><td>{passengers}</td></tr>
        <tr><td>Booking Ref:</td><td>{booking_reference}</td></tr>
      </table>
      
      <a href="{APP_URL}/dashboard">View Dashboard</a>
    </div>
  </body>
</html>
```

### Booking Failure Email Template
```html
<html>
  <body>
    <div style="background-color: #ef4444; color: white; padding: 20px;">
      <h1>Booking ✗</h1>
      <p>Failed</p>
    </div>
    
    <div style="padding: 20px;">
      <h2>Hi {user.first_name},</h2>
      <p>Your booking failed.</p>
      
      <table>
        <tr><td>Route:</td><td>{origin} → {destination}</td></tr>
        <tr><td>Error:</td><td>{result_message}</td></tr>
      </table>
      
      <a href="{APP_URL}/dashboard">View Dashboard</a>
    </div>
  </body>
</html>
```

---

## Error Handling

```python
def send_booking_result(self, booking, success):
    try:
        if not self.sg:
            print("SendGrid not configured, skipping email")
            return
        
        user = User.query.get(booking.user_id)
        if not user:
            print(f"User {booking.user_id} not found")
            return
        
        message = Mail(...)
        response = self.sg.send(message)
        print(f"Email sent: {response.status_code}")
        
    except Exception as e:
        print(f"Error sending email: {e}")
        # Don't crash - email failure shouldn't break booking
```

**Error Cases:**
- ❌ SendGrid not configured → Skip silently
- ❌ Invalid API key → Log error, continue
- ❌ User not found → Log error, continue
- ❌ Network error → Log error, continue
- ✅ All errors logged but don't break core functionality

---

## Timing & Triggers

```
┌─────────────────────────────────────────────────────────────┐
│                    Event Timeline                            │
└─────────────────────────────────────────────────────────────┘

T=0: User signs up
     └─▶ Welcome email sent immediately

T=1: User creates booking for midnight
     └─▶ BookingRequest saved with scheduled_time=00:00

T=2: Scheduler checks every minute
     └─▶ Finds no pending bookings yet

...

T=1440min (00:00 midnight):
     └─▶ Scheduler finds booking
         └─▶ Execute browser automation (2-5 min)
             ├─ Success → Update DB → Send success email
             └─ Failure → Update DB → Send failure email

T=1445min (00:05):
     └─▶ User checks email inbox
         └─▶ Receives booking result notification
```

---

## Testing Locally

```bash
# 1. Set up SendGrid credentials
cd backend
echo "SENDGRID_API_KEY=SG.your_key" >> .env
echo "SENDGRID_FROM_EMAIL=your@email.com" >> .env

# 2. Test welcome email
python -c "
from app import create_app
from services.notification import NotificationService

app = create_app()
notif = NotificationService(app)
notif.send_welcome_email('test@example.com', 'Test User')
print('Check your inbox!')
"

# 3. Test booking result email
python -c "
from app import create_app
from services.notification import NotificationService
from models import BookingRequest, User

app = create_app()
with app.app_context():
    booking = BookingRequest.query.first()
    notif = NotificationService(app)
    notif.send_booking_result(booking, success=True)
"
```

---

## Production Checklist

- [ ] Sign up for SendGrid (free tier: 100 emails/day)
- [ ] Create API key with "Mail Send" permission
- [ ] Verify sender email in SendGrid dashboard
- [ ] Add `SENDGRID_API_KEY` to Render environment
- [ ] Add `SENDGRID_FROM_EMAIL` to Render environment
- [ ] Test welcome email on signup
- [ ] Test booking success email
- [ ] Test booking failure email
- [ ] Monitor SendGrid dashboard for delivery stats

---

## Monitoring & Logs

```python
# Console output examples:

# Success:
"Email sent to user@example.com: 202"

# Not configured:
"SendGrid not configured, skipping email notification"

# Error:
"Error sending email: Invalid API key"
"User 123 not found"
```

**Where to check:**
1. Render logs: Backend service → Logs tab
2. SendGrid dashboard: Activity → Email Activity
3. Database: `audit_log` table tracks all actions

---

## API Response Flow

```
User Action          Backend Process           Email Sent
───────────         ─────────────────         ──────────

POST /signup   →    Create user       →       Welcome email
                    Commit DB
                    Return JWT

Midnight       →    Scheduler runs    →       Result email
(Cron job)          Execute booking
                    Update DB
                    
Admin action   →    User updated      →       (No email)
                    Audit logged
```

---

## File Structure

```
backend/
├── services/
│   ├── notification.py          ← Email logic
│   ├── scheduler.py              ← Triggers booking emails
│   └── booking_automation.py     ← Executes bookings
├── routes/
│   └── auth.py                   ← Triggers welcome email
├── config.py                     ← SendGrid credentials
└── models.py                     ← User & BookingRequest models
```

---

## Summary

**Trigger Points:**
1. User signup → Welcome email (immediate)
2. Booking execution → Result email (at midnight)

**Key Components:**
- `NotificationService` - Handles all email sending
- `scheduler.py` - Triggers booking result emails
- `auth.py` - Triggers welcome emails
- SendGrid API - Delivers emails

**Configuration:**
- `SENDGRID_API_KEY` - Required for sending
- `SENDGRID_FROM_EMAIL` - Must be verified sender
- `APP_URL` - For dashboard links in emails

**Error Handling:**
- Graceful degradation (logs errors, doesn't crash)
- All failures logged for debugging
- Core functionality continues even if email fails
