# Midnight Travel Booker - API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### POST /auth/signup
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "timezone": "America/New_York"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### POST /auth/login
Authenticate a user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### POST /auth/refresh
Refresh access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "access_token": "eyJ..."
}
```

### GET /auth/me
Get current authenticated user.

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "timezone": "America/New_York",
    "is_admin": false,
    "is_active": true
  }
}
```

---

## User Endpoints

### GET /users/profile
Get user profile.

**Response:**
```json
{
  "user": { ... }
}
```

### PUT /users/profile
Update user profile.

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "timezone": "America/Los_Angeles"
}
```

### POST /users/credentials
Save encrypted travel site credentials.

**Request Body:**
```json
{
  "username": "travel_username",
  "password": "travel_password"
}
```

### GET /users/credentials
Check if user has saved credentials.

**Response:**
```json
{
  "has_credentials": true
}
```

### DELETE /users/credentials
Delete saved credentials.

---

## Booking Endpoints

### GET /bookings
Get all bookings for current user.

**Response:**
```json
{
  "bookings": [
    {
      "id": 1,
      "origin": "New York",
      "destination": "Los Angeles",
      "departure_date": "2025-01-15",
      "return_date": null,
      "passengers": 1,
      "status": "pending",
      "scheduled_time": "2025-01-15T05:00:00Z",
      "created_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

### POST /bookings
Create a new booking request.

**Request Body:**
```json
{
  "origin": "New York",
  "destination": "Los Angeles",
  "departure_date": "2025-01-15",
  "return_date": "2025-01-20",
  "passengers": 2,
  "max_price": 500.00
}
```

### PUT /bookings/:id
Update a pending booking.

**Request Body:**
```json
{
  "passengers": 3,
  "max_price": 600.00
}
```

### DELETE /bookings/:id
Cancel a booking.

---

## Subscription Endpoints

### GET /subscriptions
Get current subscription.

**Response:**
```json
{
  "subscription": {
    "id": 1,
    "tier": "standard",
    "status": "active",
    "current_period_end": "2025-02-01T00:00:00Z"
  }
}
```

### POST /subscriptions/create-checkout-session
Create Stripe checkout session.

**Request Body:**
```json
{
  "tier": "standard",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_..."
}
```

### POST /subscriptions/webhook
Stripe webhook endpoint (handled by Stripe).

---

## Admin Endpoints (Admin Only)

### GET /admin/users
Get all users (paginated).

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20)

### GET /admin/users/:id
Get specific user details.

### PUT /admin/users/:id
Update user (admin operations).

**Request Body:**
```json
{
  "is_active": false,
  "is_admin": true
}
```

### GET /admin/bookings
Get all bookings (paginated).

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20)
- `status` (optional: pending, success, failed, etc.)

### GET /admin/audit-logs
Get audit logs (paginated).

### GET /admin/stats
Get system statistics.

**Response:**
```json
{
  "stats": {
    "total_users": 150,
    "active_users": 120,
    "total_bookings": 500,
    "pending_bookings": 45
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (e.g., email already exists)
- `500` - Internal Server Error
