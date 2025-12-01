# Render Deployment Guide

This guide covers deploying Midnight Travel Booker to Render.com.

## Prerequisites

- Render.com account (free tier available)
- GitHub account
- Stripe account (test mode)
- SendGrid account (free tier)

---

## Deployment Options

### Option 1: Blueprint (Recommended - One-Click Deploy)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and create all services

3. **Configure Environment Variables**
   
   Go to each service and set the following:

   **Backend Service:**
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret
   - `STRIPE_PRICE_BASIC`: Stripe price ID for basic tier
   - `STRIPE_PRICE_STANDARD`: Stripe price ID for standard tier
   - `STRIPE_PRICE_PREMIUM`: Stripe price ID for premium tier
   - `SENDGRID_API_KEY`: Your SendGrid API key
   - `SENDGRID_FROM_EMAIL`: Your sender email
   - `ENCRYPTION_KEY`: Generate with command below

   Generate encryption key:
   ```bash
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

4. **Update Frontend Environment**
   - In the frontend service settings, update `VITE_API_URL` to your backend URL:
     ```
     https://midnight-travel-backend.onrender.com/api
     ```

5. **Configure Stripe Webhook**
   - Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
   - Add endpoint: `https://midnight-travel-backend.onrender.com/api/subscriptions/webhook`
   - Select events:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_failed`
   - Copy the signing secret and add to backend environment variables

---

### Option 2: Manual Deploy

#### Step 1: Deploy Database

1. Go to Render Dashboard → "New" → "PostgreSQL"
2. Name: `midnight-travel-db`
3. Database: `midnight_travel`
4. User: `midnight_user`
5. Region: Choose closest to you
6. Plan: Free
7. Click "Create Database"
8. Copy the "Internal Database URL"

#### Step 2: Deploy Backend

1. Go to Render Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `midnight-travel-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - **Start Command**:
     ```bash
     gunicorn --bind 0.0.0.0:$PORT --workers 2 'app:create_app()'
     ```
   - **Plan**: Free

4. Add Environment Variables:
   ```
   PYTHON_VERSION=3.11.0
   DATABASE_URL=<paste internal database URL>
   FLASK_ENV=production
   SECRET_KEY=<generate random string>
   JWT_SECRET_KEY=<generate random string>
   STRIPE_SECRET_KEY=<your stripe key>
   STRIPE_WEBHOOK_SECRET=<your webhook secret>
   STRIPE_PRICE_BASIC=<price ID>
   STRIPE_PRICE_STANDARD=<price ID>
   STRIPE_PRICE_PREMIUM=<price ID>
   SENDGRID_API_KEY=<your sendgrid key>
   SENDGRID_FROM_EMAIL=<your email>
   ENCRYPTION_KEY=<generated fernet key>
   APP_URL=<frontend URL - will update later>
   API_URL=<this backend URL>
   ```

5. Click "Create Web Service"

#### Step 3: Deploy Frontend

1. Go to Render Dashboard → "New" → "Static Site"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `midnight-travel-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. Add Environment Variable:
   ```
   VITE_API_URL=https://midnight-travel-backend.onrender.com/api
   ```

5. Click "Create Static Site"

#### Step 4: Update Backend APP_URL

1. Go to backend service settings
2. Update `APP_URL` environment variable with your frontend URL:
   ```
   APP_URL=https://midnight-travel-frontend.onrender.com
   ```
3. Restart the backend service

---

## Post-Deployment Setup

### 1. Create Admin User

Using Render Shell (in backend service):

```python
from app import create_app
from models import db, User
from utils.security import hash_password

app = create_app()
with app.app_context():
    admin = User(
        email='admin@example.com',
        password_hash=hash_password('ChangeThisPassword123!'),
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
```

Or use the Shell button in Render dashboard and run the above code.

### 3. Verify Backend is Running

Test these endpoints:

```bash
# Health check (should return {"status": "healthy"})
curl https://midnight-travel-backend.onrender.com/health

# API root (should return API info)
curl https://midnight-travel-backend.onrender.com/

# Test signup endpoint
curl -X POST https://midnight-travel-backend.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","first_name":"Test","last_name":"User"}'
```

### 4. Test the Application

1. Visit your frontend URL
2. Sign up for a new account
3. Test subscription flow (use Stripe test card: 4242 4242 4242 4242)
4. Save travel credentials
5. Create a test booking

### 3. Monitor Services

- **Logs**: Check each service's logs in Render dashboard
- **Health**: Backend has `/health` endpoint for monitoring
- **Metrics**: View CPU, memory, and bandwidth in Render dashboard

---

## Environment Variables Reference

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-populated by Render |
| `SECRET_KEY` | Flask secret key | Random 32+ character string |
| `JWT_SECRET_KEY` | JWT signing key | Random 32+ character string |
| `ENCRYPTION_KEY` | Fernet encryption key | Generated via cryptography.fernet |
| `STRIPE_SECRET_KEY` | Stripe API secret | `sk_test_...` or `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` |
| `STRIPE_PRICE_BASIC` | Basic tier price ID | `price_...` |
| `STRIPE_PRICE_STANDARD` | Standard tier price ID | `price_...` |
| `STRIPE_PRICE_PREMIUM` | Premium tier price ID | `price_...` |
| `SENDGRID_API_KEY` | SendGrid API key | `SG....` |
| `SENDGRID_FROM_EMAIL` | Verified sender email | `noreply@yourdomain.com` |
| `APP_URL` | Frontend URL | `https://midnight-travel-frontend.onrender.com` |
| `API_URL` | Backend URL | `https://midnight-travel-backend.onrender.com` |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://midnight-travel-backend.onrender.com/api` |

---

## Troubleshooting

### Build Failures

**Playwright Installation Issues:**
```bash
# If playwright fails, try adding to build command:
apt-get update && apt-get install -y wget gnupg && playwright install-deps
```

**Python Version Issues:**
- Ensure `PYTHON_VERSION=3.11.0` is set in environment variables

### Database Connection Issues

**Error: "could not connect to server"**
- Check that `DATABASE_URL` is set correctly
- Verify database is in the same region as backend
- Use "Internal Database URL" from Render, not external

### Frontend Not Loading API Data

**CORS Errors:**
- Backend should allow your frontend origin
- Check Flask-CORS configuration in `app.py`

**API URL Wrong:**
- Verify `VITE_API_URL` points to backend with `/api` suffix
- Check browser console for failed requests

### 404 Errors on Backend

**Root path (/) returns 404:**
- This is expected - backend serves API at `/api/*` endpoints
- Test with: `https://your-backend.onrender.com/health` (should return 200)
- Test with: `https://your-backend.onrender.com/api/auth/login`

**All endpoints return 404:**
- Check backend logs for startup errors
- Verify build completed successfully
- Ensure Flask app is running on correct port ($PORT)
- Check `startCommand` in render.yaml

### Stripe Webhook Not Working

**Events Not Received:**
- Verify webhook URL is set to: `https://your-backend.onrender.com/api/subscriptions/webhook`
- Check webhook signing secret matches environment variable
- View webhook attempts in Stripe dashboard

### Playwright/Browser Issues

**Chromium Not Found:**
```bash
# Add to build command:
playwright install chromium && playwright install-deps chromium
```

**Insufficient Memory:**
- Upgrade to paid tier (free tier has 512MB RAM)
- Or reduce concurrent Playwright instances

---

## Render Free Tier Limitations

- **Web Services**: 750 hours/month, spin down after 15 min inactivity
- **Databases**: 90 days expiry, 1GB storage
- **Static Sites**: 100GB bandwidth/month

**Important**: Free web services sleep after inactivity. First request after sleep takes 30-60s to wake up.

**Solutions:**
- Upgrade to paid tier ($7/month per service)
- Use external cron service to ping `/health` every 14 minutes
- Accept the cold start delay

---

## Upgrading to Production

1. **Upgrade Services**
   - Backend: Starter ($7/mo) - 512MB RAM, no sleep
   - Database: Starter ($7/mo) - No expiry, 1GB storage
   - Frontend: Can stay free

2. **Enable HTTPS** (automatic on Render)

3. **Custom Domain**
   - Add domain in Render dashboard
   - Update DNS CNAME records
   - SSL certificates provisioned automatically

4. **Environment Security**
   - Use production Stripe keys
   - Rotate all secrets
   - Enable 2FA on Render account

5. **Monitoring**
   - Set up Render alerts
   - Enable error tracking (Sentry, etc.)
   - Monitor logs regularly

---

## Maintenance

### Viewing Logs

```bash
# Real-time logs in Render dashboard
# Or use Render CLI:
render logs -s midnight-travel-backend
```

### Database Backups

Free tier doesn't include backups. For production:
- Upgrade to paid tier (daily backups)
- Or use `pg_dump` manually

### Updates & Deployments

Auto-deploy enabled by default:
- Push to GitHub → Automatic deploy
- Manual deploy: Click "Deploy latest commit" in dashboard

---

## Support

- **Render Docs**: https://render.com/docs
- **Community**: https://community.render.com
- **Status**: https://status.render.com

---

## Cost Estimate

**Free Tier (Development):**
- Backend: Free
- Frontend: Free
- Database: Free
- **Total: $0/month**

**Production (Recommended):**
- Backend: $7/month (Starter)
- Database: $7/month (Starter)
- Frontend: Free
- **Total: $14/month**

---

## Next Steps

1. ✅ Deploy services
2. ✅ Configure environment variables
3. ✅ Set up Stripe webhook
4. ✅ Create admin user
5. ✅ Test application
6. 📧 Configure SendGrid sender authentication
7. 🔒 Review security settings
8. 📊 Set up monitoring

**Your app is now live! 🎉**
