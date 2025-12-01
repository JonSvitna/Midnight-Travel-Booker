# Quick Render Deployment Checklist

## Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] Stripe account created (test mode)
- [ ] SendGrid account created
- [ ] Generate encryption key: `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

## Render Setup
- [ ] Go to https://dashboard.render.com/
- [ ] Click "New" → "Blueprint"
- [ ] Connect GitHub repository
- [ ] Wait for services to be created (3 services)

## Backend Environment Variables
Navigate to backend service → Environment:

- [ ] `STRIPE_SECRET_KEY` = `sk_test_...` (from Stripe dashboard)
- [ ] `STRIPE_WEBHOOK_SECRET` = `whsec_...` (from Stripe webhook)
- [ ] `STRIPE_PRICE_BASIC` = `price_...` (Stripe price ID)
- [ ] `STRIPE_PRICE_STANDARD` = `price_...` (Stripe price ID)
- [ ] `STRIPE_PRICE_PREMIUM` = `price_...` (Stripe price ID)
- [ ] `SENDGRID_API_KEY` = `SG....` (from SendGrid)
- [ ] `SENDGRID_FROM_EMAIL` = `verified@yourdomain.com`
- [ ] `ENCRYPTION_KEY` = (generated Fernet key)

## Frontend Environment Variables
Navigate to frontend service → Environment:

- [ ] `VITE_API_URL` = `https://midnight-travel-backend.onrender.com/api`

## Update Backend APP_URL
After frontend deploys:

- [ ] Go to backend service → Environment
- [ ] Update `APP_URL` = `https://midnight-travel-frontend.onrender.com`
- [ ] Click "Save Changes"
- [ ] Backend will auto-redeploy

## Stripe Webhook Setup
- [ ] Go to https://dashboard.stripe.com/webhooks
- [ ] Click "Add endpoint"
- [ ] URL: `https://midnight-travel-backend.onrender.com/api/subscriptions/webhook`
- [ ] Select events:
  - [ ] `checkout.session.completed`
  - [ ] `customer.subscription.updated`
  - [ ] `customer.subscription.deleted`
  - [ ] `invoice.payment_failed`
- [ ] Copy signing secret
- [ ] Add to backend `STRIPE_WEBHOOK_SECRET`

## Test Backend
```bash
# Should return {"status": "healthy"}
curl https://midnight-travel-backend.onrender.com/health

# Should return API info
curl https://midnight-travel-backend.onrender.com/
```

## Create Admin User
In backend service shell:

```python
from app import create_app
from models import db, User
from utils.security import hash_password

app = create_app()
with app.app_context():
    admin = User(
        email='admin@yourdomain.com',
        password_hash=hash_password('SecurePassword123!'),
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin created!')
```

## Test Application
- [ ] Visit frontend URL
- [ ] Sign up works
- [ ] Login works
- [ ] Stripe checkout loads
- [ ] Test payment (card: 4242 4242 4242 4242)
- [ ] Dashboard displays
- [ ] Profile updates work
- [ ] Booking creation works

## Common Issues

### Backend 404 Error
- Root path (/) may show 404 - this is OK
- Test `/health` endpoint instead
- API is at `/api/*` paths

### CORS Errors
- Verify `APP_URL` in backend matches frontend URL
- Check browser console for specific error

### Stripe Checkout Doesn't Load
- Verify all `STRIPE_PRICE_*` variables are set
- Check Stripe test mode is active
- View backend logs for errors

### Email Not Sending
- Verify SendGrid sender email is verified
- Check `SENDGRID_FROM_EMAIL` matches verified sender
- View backend logs for SendGrid errors

### Frontend Shows "Network Error"
- Verify `VITE_API_URL` points to backend
- Check backend is running (green status in Render)
- Test API endpoints with curl

## URLs to Save
- Frontend: `https://midnight-travel-frontend.onrender.com`
- Backend: `https://midnight-travel-backend.onrender.com`
- Database: (Internal URL in Render)

## Done! 🎉

Your app is live and ready to use.

**Free Tier Notes:**
- Services sleep after 15 min inactivity
- First request after sleep takes ~30s
- Upgrade to $7/mo per service to prevent sleeping
