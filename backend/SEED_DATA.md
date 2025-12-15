# Seed Data Generation

This document describes how to populate the database with fake booking data for testing and demonstration purposes.

## Overview

The `seed_bookings.py` script generates realistic fake booking data to populate the application with sample bookings. This is useful for:
- Testing the UI with realistic data
- Demonstrating the application functionality
- Development and debugging

## Usage

### Basic Usage

Generate 20 fake bookings (default):
```bash
cd backend
python seed_bookings.py
```

### Custom Number of Bookings

Generate a specific number of bookings:
```bash
python seed_bookings.py 50
```

## What the Script Does

1. **Creates a demo user** (if it doesn't exist):
   - Email: `demo@example.com`
   - Password: `demo123`
   - Active premium subscription

2. **Generates fake bookings** with:
   - Random popular destinations (New York, Paris, Tokyo, etc.)
   - Varied booking statuses:
     - 30% Pending (future bookings)
     - 10% Processing (in progress)
     - 40% Success (completed bookings)
     - 10% Failed (failed attempts)
     - 10% Canceled (user canceled)
   - Realistic dates (past dates for completed bookings, future dates for pending)
   - Random number of passengers (1-4)
   - Optional max price constraints
   - Booking references for successful bookings
   - Result messages for failed bookings

## Booking Status Distribution

The script creates a realistic mix of booking statuses:
- **SUCCESS**: Bookings with confirmation codes and completion messages
- **PENDING**: Future bookings waiting to be processed
- **PROCESSING**: Bookings currently being handled by the system
- **FAILED**: Bookings that couldn't be completed (with failure reasons)
- **CANCELED**: User-canceled bookings

## Demo User Credentials

After running the script, you can log in with:
- **Email**: demo@example.com
- **Password**: demo123

The demo user will have:
- An active Premium subscription
- Multiple bookings in various states
- Full access to all features

## Notes

- The script is idempotent - running it multiple times will add more bookings
- All dates are generated relative to the current date
- Past bookings (SUCCESS/FAILED/CANCELED) use dates from the last 60 days
- Future bookings (PENDING/PROCESSING) use dates up to 90 days ahead
- The demo user's subscription is automatically set to active with Premium tier
