from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config
from models import BookingRequest, User

class NotificationService:
    """Handle email notifications using SendGrid"""
    
    def __init__(self, app):
        self.app = app
        self.sg = SendGridAPIClient(Config.SENDGRID_API_KEY) if Config.SENDGRID_API_KEY else None
    
    def send_booking_result(self, booking: BookingRequest, success: bool):
        """Send booking result notification to user"""
        if not self.sg:
            print("SendGrid not configured, skipping email notification")
            return
        
        with self.app.app_context():
            user = User.query.get(booking.user_id)
            
            if not user:
                print(f"User {booking.user_id} not found")
                return
            
            subject = "Booking Successful ✓" if success else "Booking Failed ✗"
            
            html_content = self._get_booking_result_template(booking, user, success)
            
            message = Mail(
                from_email=Config.SENDGRID_FROM_EMAIL,
                to_emails=user.email,
                subject=subject,
                html_content=html_content
            )
            
            try:
                response = self.sg.send(message)
                print(f"Email sent to {user.email}: {response.status_code}")
            except Exception as e:
                print(f"Error sending email: {e}")
    
    def send_welcome_email(self, user_email: str, user_name: str):
        """Send welcome email to new user"""
        if not self.sg:
            print("SendGrid not configured, skipping welcome email")
            return
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Welcome to Midnight Travel Booker!</h2>
                <p>Hi {user_name},</p>
                <p>Thank you for joining Midnight Travel Booker! We're excited to help you secure the best travel deals at midnight.</p>
                <h3>Next Steps:</h3>
                <ol>
                    <li>Subscribe to a plan to start booking</li>
                    <li>Save your travel site credentials securely</li>
                    <li>Create your first booking request</li>
                </ol>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>Happy travels!<br>The Midnight Travel Booker Team</p>
            </body>
        </html>
        """
        
        message = Mail(
            from_email=Config.SENDGRID_FROM_EMAIL,
            to_emails=user_email,
            subject="Welcome to Midnight Travel Booker!",
            html_content=html_content
        )
        
        try:
            response = self.sg.send(message)
            print(f"Welcome email sent to {user_email}: {response.status_code}")
        except Exception as e:
            print(f"Error sending welcome email: {e}")
    
    def _get_booking_result_template(self, booking: BookingRequest, user: User, success: bool):
        """Generate HTML template for booking result email"""
        status_color = "#10b981" if success else "#ef4444"
        status_icon = "✓" if success else "✗"
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: {status_color}; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">Booking {status_icon}</h1>
                    <p style="margin: 5px 0 0 0; font-size: 18px;">
                        {'Successfully Completed' if success else 'Failed'}
                    </p>
                </div>
                
                <div style="padding: 20px;">
                    <h2>Hi {user.first_name},</h2>
                    
                    <p>Your automated booking request has been {'completed successfully' if success else 'failed'}.</p>
                    
                    <h3>Booking Details:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;"><strong>Route:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{booking.origin} → {booking.destination}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;"><strong>Departure:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{booking.departure_date}</td>
                        </tr>
                        {f'<tr><td style="padding: 8px; border-bottom: 1px solid #e5e7eb;"><strong>Return:</strong></td><td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{booking.return_date}</td></tr>' if booking.return_date else ''}
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;"><strong>Passengers:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{booking.passengers}</td>
                        </tr>
                        {f'<tr><td style="padding: 8px; border-bottom: 1px solid #e5e7eb;"><strong>Booking Reference:</strong></td><td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{booking.booking_reference}</td></tr>' if booking.booking_reference else ''}
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;"><strong>Status:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{booking.result_message}</td>
                        </tr>
                    </table>
                    
                    <p style="margin-top: 20px;">
                        <a href="{Config.APP_URL}/dashboard" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            View Dashboard
                        </a>
                    </p>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        This is an automated message from Midnight Travel Booker. Please do not reply to this email.
                    </p>
                </div>
            </body>
        </html>
        """
