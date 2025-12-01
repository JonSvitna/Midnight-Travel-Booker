# Midnight Travel Booker - Setup Guide

## Prerequisites

- Docker and Docker Compose
- Git
- Stripe account (for payments)
- SendGrid account (for emails)

---

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/Midnight-Travel-Booker.git
cd Midnight-Travel-Booker
```

### 2. Configure Environment Variables

#### Backend Configuration

Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set the following:

```env
# Flask
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database (leave as is for Docker)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/midnight_travel

# Stripe (get from https://stripe.com/docs/keys)
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_BASIC=price_basic_id
STRIPE_PRICE_STANDARD=price_standard_id
STRIPE_PRICE_PREMIUM=price_premium_id

# SendGrid (get from https://sendgrid.com/docs/ui/account-and-settings/api-keys/)
SENDGRID_API_KEY=SG.your_api_key_here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-generated-encryption-key

# Application URLs
APP_URL=http://localhost:3000
API_URL=http://localhost:5000
```

#### Frontend Configuration

Copy the example environment file:
```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:
```env
VITE_API_URL=http://localhost:5000/api
```

### 3. Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and paste it as the `ENCRYPTION_KEY` value in `backend/.env`.

### 4. Set Up Stripe Products

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Create three subscription products:
   - Basic: $9.99/month
   - Standard: $19.99/month
   - Premium: $39.99/month
3. Copy the Price IDs and add them to `backend/.env`

### 5. Configure Stripe Webhook

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Forward webhooks to local:
   ```bash
   stripe listen --forward-to localhost:5000/api/subscriptions/webhook
   ```
3. Copy the webhook signing secret to `backend/.env`

### 6. Start the Application

```bash
docker-compose up --build
```

The services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **PostgreSQL**: localhost:5432

### 7. Create Admin User

Once the containers are running, create an admin user:

```bash
docker-compose exec backend python -c "
from app import create_app
from models import db, User
from utils.security import hash_password

app = create_app()
with app.app_context():
    admin = User(
        email='admin@example.com',
        password_hash=hash_password('admin123'),
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin@example.com / admin123')
"
```

---

## Manual Setup (Without Docker)

### Backend Setup

1. **Install Python 3.11+**

2. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Set up PostgreSQL:**
   ```bash
   createdb midnight_travel
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install Node.js 18+**

2. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with API URL
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```

---

## Testing the Application

### 1. Sign Up

1. Navigate to http://localhost:3000
2. Click "Get Started" or "Sign Up"
3. Fill in the registration form
4. You'll be redirected to the subscription page

### 2. Subscribe

1. Choose a subscription plan
2. Complete Stripe checkout (use test card: 4242 4242 4242 4242)
3. Return to the dashboard

### 3. Save Travel Credentials

1. Go to Profile
2. Enter your travel site credentials
3. Credentials are encrypted and stored securely

### 4. Create a Booking

1. Go to Bookings
2. Click "New Booking"
3. Fill in travel details
4. Booking will be scheduled for midnight in your timezone

### 5. Monitor Bookings

- Dashboard shows booking statistics
- Bookings page shows all your requests
- Email notifications sent on completion

---

## Production Deployment

### Deploy to Render (Recommended)

Render offers free tier and seamless deployment with Blueprint.

**Quick Start:**
1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. New → Blueprint
4. Connect repository (Render detects `render.yaml`)
5. Configure environment variables
6. Deploy!

See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for complete guide.

**Blueprint includes:**
- PostgreSQL database (free tier)
- Backend web service with Playwright
- Static frontend site
- Auto-configured connections

---

### Deploy to Heroku

1. Install Heroku CLI
2. Create new app:
   ```bash
   heroku create your-app-name
   ```

3. Add PostgreSQL addon:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=xxx
   heroku config:set JWT_SECRET_KEY=xxx
   # ... set all other environment variables
   ```

5. Deploy:
   ```bash
   git push heroku main
   ```

### Deploy to AWS Lightsail

1. Create a Lightsail container service
2. Push Docker images:
   ```bash
   docker build -t midnight-backend ./backend
   docker build -t midnight-frontend ./frontend
   ```
3. Follow Lightsail deployment guide

### Deploy to Vercel (Frontend) + Railway (Backend)

**Frontend on Vercel:**
1. Connect GitHub repo to Vercel
2. Set root directory to `frontend`
3. Deploy

**Backend on Railway:**
1. Connect GitHub repo to Railway
2. Add PostgreSQL service
3. Set environment variables
4. Deploy

---

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres
```

### Backend Not Starting

```bash
# Check backend logs
docker-compose logs backend

# Rebuild
docker-compose up --build backend
```

### Frontend Build Errors

```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Playwright Issues

```bash
# Reinstall Playwright browsers
playwright install chromium
playwright install-deps
```

---

## Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use strong SECRET_KEY and JWT_SECRET_KEY**
3. **Rotate encryption keys periodically**
4. **Enable HTTPS in production**
5. **Set up proper firewall rules**
6. **Regular security audits**
7. **Keep dependencies updated**

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check API documentation: `API_DOCUMENTATION.md`
- Review error logs: `docker-compose logs`

---

## License

MIT License - See LICENSE file for details
