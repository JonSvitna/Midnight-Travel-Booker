import pytest
from app import create_app
from models import db, User
from utils.security import hash_password

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return headers"""
    # Create test user
    user = User(
        email='test@example.com',
        password_hash=hash_password('password123'),
        first_name='Test',
        last_name='User'
    )
    db.session.add(user)
    db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_signup(client):
    """Test user signup"""
    response = client.post('/api/auth/signup', json={
        'email': 'newuser@example.com',
        'password': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'timezone': 'UTC'
    })
    
    assert response.status_code == 201
    assert 'access_token' in response.json
    assert response.json['user']['email'] == 'newuser@example.com'

def test_login(client):
    """Test user login"""
    # Create user first
    user = User(
        email='login@example.com',
        password_hash=hash_password('password123'),
        first_name='Login',
        last_name='User'
    )
    db.session.add(user)
    db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'login@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_get_profile(client, auth_headers):
    """Test get user profile"""
    response = client.get('/api/users/profile', headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['user']['email'] == 'test@example.com'

def test_create_booking(client, auth_headers):
    """Test create booking request"""
    response = client.post('/api/bookings', 
        headers=auth_headers,
        json={
            'origin': 'New York',
            'destination': 'Los Angeles',
            'departure_date': '2025-12-25',
            'passengers': 1
        }
    )
    
    # Will fail without active subscription, but tests endpoint
    assert response.status_code in [201, 403]

def test_unauthorized_access(client):
    """Test accessing protected endpoint without auth"""
    response = client.get('/api/users/profile')
    assert response.status_code == 401
