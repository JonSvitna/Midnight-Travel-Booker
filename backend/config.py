import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///midnight_travel.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    STRIPE_PRICE_BASIC = os.getenv('STRIPE_PRICE_BASIC')
    STRIPE_PRICE_STANDARD = os.getenv('STRIPE_PRICE_STANDARD')
    STRIPE_PRICE_PREMIUM = os.getenv('STRIPE_PRICE_PREMIUM')
    
    # SendGrid
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@midnighttravel.com')
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # Application
    APP_URL = os.getenv('APP_URL', 'http://localhost:3000')
    API_URL = os.getenv('API_URL', 'http://localhost:5000')
    
    # Booking
    TARGET_TRAVEL_SITE_URL = os.getenv('TARGET_TRAVEL_SITE_URL')
    BOOKING_TIME = os.getenv('BOOKING_TIME', '00:00:00')
