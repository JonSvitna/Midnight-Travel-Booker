from playwright.sync_api import sync_playwright
from models import db, BookingRequest, BookingStatus, TravelCredential, User
from utils.security import decrypt_data
from datetime import datetime
import json

class BookingAutomation:
    """Handles automated booking through browser simulation"""
    
    def __init__(self, booking_request: BookingRequest, app_context):
        self.booking = booking_request
        self.app_context = app_context
        self.user = None
        self.credentials = None
        
    def execute(self):
        """Execute the automated booking"""
        with self.app_context:
            try:
                # Load user and credentials
                self.user = User.query.get(self.booking.user_id)
                self.credentials = TravelCredential.query.filter_by(user_id=self.booking.user_id).first()
                
                if not self.credentials:
                    self._update_booking_status(
                        BookingStatus.FAILED,
                        "No travel site credentials found"
                    )
                    return False
                
                # Update status to processing
                self._update_booking_status(BookingStatus.PROCESSING, "Starting booking automation")
                
                # Run browser automation
                result = self._run_browser_automation()
                
                if result['success']:
                    self._update_booking_status(
                        BookingStatus.SUCCESS,
                        result['message'],
                        result.get('booking_reference')
                    )
                    return True
                else:
                    self._update_booking_status(
                        BookingStatus.FAILED,
                        result['message']
                    )
                    return False
                    
            except Exception as e:
                self._update_booking_status(
                    BookingStatus.FAILED,
                    f"Error during automation: {str(e)}"
                )
                return False
    
    def _run_browser_automation(self):
        """Run the actual browser automation using Playwright"""
        try:
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Decrypt credentials
                username = decrypt_data(self.credentials.travel_site_username)
                password = decrypt_data(self.credentials.travel_site_password)
                
                # Navigate to travel site
                # NOTE: This is a placeholder implementation
                # In production, replace with actual travel site selectors and logic
                
                page.goto('https://example-travel-site.com')
                page.wait_for_load_state('networkidle')
                
                # Login
                page.fill('input[name="username"]', username)
                page.fill('input[name="password"]', password)
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')
                
                # Check if login was successful
                if page.url.find('dashboard') == -1:
                    browser.close()
                    return {
                        'success': False,
                        'message': 'Login failed - invalid credentials or site structure changed'
                    }
                
                # Navigate to booking page
                page.goto('https://example-travel-site.com/book')
                page.wait_for_load_state('networkidle')
                
                # Fill in search details
                page.fill('input[name="origin"]', self.booking.origin)
                page.fill('input[name="destination"]', self.booking.destination)
                page.fill('input[name="departure_date"]', self.booking.departure_date.isoformat())
                
                if self.booking.return_date:
                    page.fill('input[name="return_date"]', self.booking.return_date.isoformat())
                
                page.fill('input[name="passengers"]', str(self.booking.passengers))
                
                # Submit search
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')
                
                # Wait for results to load
                page.wait_for_selector('.booking-results', timeout=30000)
                
                # Try to find and book the lowest price option
                # This is a simplified example - actual implementation would need
                # more sophisticated logic to handle various scenarios
                
                lowest_price_option = page.query_selector('.booking-option:first-child')
                
                if not lowest_price_option:
                    browser.close()
                    return {
                        'success': False,
                        'message': 'No booking options available'
                    }
                
                # Check price if max_price is set
                if self.booking.max_price:
                    price_element = lowest_price_option.query_selector('.price')
                    if price_element:
                        price_text = price_element.inner_text().replace('$', '').replace(',', '')
                        try:
                            price = float(price_text)
                            if price > float(self.booking.max_price):
                                browser.close()
                                return {
                                    'success': False,
                                    'message': f'Lowest price ${price} exceeds max price ${self.booking.max_price}'
                                }
                        except ValueError:
                            pass
                
                # Click book button
                lowest_price_option.query_selector('.book-button').click()
                page.wait_for_load_state('networkidle')
                
                # Confirm booking
                page.click('button.confirm-booking')
                page.wait_for_load_state('networkidle')
                
                # Try to extract booking reference
                booking_ref = None
                try:
                    ref_element = page.query_selector('.booking-reference')
                    if ref_element:
                        booking_ref = ref_element.inner_text()
                except:
                    pass
                
                browser.close()
                
                return {
                    'success': True,
                    'message': 'Booking completed successfully',
                    'booking_reference': booking_ref
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Browser automation error: {str(e)}'
            }
    
    def _update_booking_status(self, status: BookingStatus, message: str, booking_ref: str = None):
        """Update booking status in database"""
        self.booking.status = status
        self.booking.result_message = message
        self.booking.executed_at = datetime.utcnow()
        
        if booking_ref:
            self.booking.booking_reference = booking_ref
        
        db.session.commit()
