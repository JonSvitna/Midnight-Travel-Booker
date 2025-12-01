# Render Deployment Fix Guide

## Problem
Your existing Render service `midnight-travel-booker-backend` is still configured for Node.js, but we've switched to Python/Flask.

## Solution Options

### Option 1: Delete Old Services and Redeploy (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Delete existing services**:
   - `midnight-travel-booker-backend` (the old Node.js service)
   - `midnight-travel-booker-frontend` (if exists)
3. **Deploy new Blueprint**:
   - Click "New" → "Blueprint"
   - Connect to your GitHub repository: `JonSvitna/Midnight-Travel-Booker`
   - Render will automatically detect `render.yaml` and create:
     - `midnight-travel-db` (PostgreSQL)
     - `midnight-travel-backend` (Python/Flask)
     - `midnight-travel-frontend` (Static React)

### Option 2: Manually Reconfigure Existing Service

1. **Go to your backend service**: https://dashboard.render.com/web/midnight-travel-booker-backend
2. **Update Settings**:
   - **Runtime**: Change from `Node` to `Python 3.11`
   - **Build Command**: `./render-build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 'app:create_app()'`
   - **Root Directory**: `backend`
3. **Add Database**:
   - Create new PostgreSQL database or connect existing one
4. **Environment Variables** (see below)
5. **Trigger Manual Deploy**

---

## Required Environment Variables

### Backend Service Environment Variables

```bash
# Python
PYTHON_VERSION=3.11.0

# Database (auto-generated if using Render PostgreSQL)
DATABASE_URL=<from-database>

# Flask
FLASK_ENV=production
SECRET_KEY=<generate-random-32-char-string>
JWT_SECRET_KEY=<generate-random-32-char-string>

# Stripe (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_BASIC=price_test_basic_id
STRIPE_PRICE_STANDARD=price_test_standard_id
STRIPE_PRICE_PREMIUM=price_test_premium_id

# SendGrid (get from https://app.sendgrid.com/settings/api_keys)
SENDGRID_API_KEY=SG.your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Security (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=<generate-fernet-key>

# URLs (update with your actual Render URLs)
APP_URL=https://midnight-travel-frontend.onrender.com
API_URL=https://midnight-travel-backend.onrender.com
TARGET_TRAVEL_SITE_URL=https://example-travel-site.com

# Booking
BOOKING_TIME=00:00:00
```

### Frontend Service Environment Variables

```bash
VITE_API_URL=https://midnight-travel-backend.onrender.com/api
```

---

## Step-by-Step: Option 1 (Recommended)

### Step 1: Delete Old Services

1. Go to https://dashboard.render.com/
2. Find `midnight-travel-booker-backend` service
3. Click on it → Settings → scroll to bottom → "Delete Web Service"
4. Confirm deletion
5. Repeat for `midnight-travel-booker-frontend` if it exists

### Step 2: Deploy from Blueprint

1. Click "New" button (top right)
2. Select "Blueprint"
3. Connect your GitHub repository: `JonSvitna/Midnight-Travel-Booker`
4. Render will detect `render.yaml` and show:
   - Database: `midnight-travel-db`
   - Web Service: `midnight-travel-backend`
   - Static Site: `midnight-travel-frontend`
5. Click "Apply" to create all services

### Step 3: Configure Environment Variables

After services are created, add the required environment variables:

#### For `midnight-travel-backend`:
1. Go to service → Environment
2. Add all variables from the list above
3. Click "Save Changes"

#### For `midnight-travel-frontend`:
1. Go to service → Environment
2. Add `VITE_API_URL`
3. Click "Save Changes"

### Step 4: Trigger Deploy

Services should auto-deploy after environment variables are set. If not:
1. Go to each service
2. Click "Manual Deploy" → "Deploy latest commit"

### Step 5: Verify Deployment

1. **Backend Health Check**:
   ```bash
   curl https://midnight-travel-backend.onrender.com/health
   # Should return: {"status":"healthy"}
   ```

2. **Backend Root**:
   ```bash
   curl https://midnight-travel-backend.onrender.com/
   # Should return API info JSON
   ```

3. **Frontend**: Visit `https://midnight-travel-frontend.onrender.com`

---

## Generate Required Keys

### Encryption Key (Fernet)
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Secret Keys
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Stripe Setup

1. Go to https://dashboard.stripe.com/test/products
2. Create 3 products:
   - **Basic Plan**: $9.99/month → Copy price ID
   - **Standard Plan**: $19.99/month → Copy price ID  
   - **Premium Plan**: $29.99/month → Copy price ID
3. Get API keys from https://dashboard.stripe.com/test/apikeys
4. Set up webhook:
   - URL: `https://midnight-travel-backend.onrender.com/api/subscriptions/webhook`
   - Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
   - Copy webhook secret

---

## SendGrid Setup

1. Go to https://app.sendgrid.com/settings/api_keys
2. Create new API key with "Mail Send" permissions
3. Verify sender email at https://app.sendgrid.com/settings/sender_auth

---

## Troubleshooting

### Build fails with "npm error"
- **Cause**: Old Node.js configuration still active
- **Fix**: Delete old service and redeploy from Blueprint (Option 1)

### "Cannot GET /" error
- **Cause**: Service not using Python/Flask app
- **Fix**: Verify runtime is Python, build/start commands are correct

### Database connection error
- **Cause**: DATABASE_URL not set or incorrect
- **Fix**: Ensure PostgreSQL database is created and linked

### "Module not found" errors
- **Cause**: Dependencies not installed
- **Fix**: Check build logs, ensure `render-build.sh` runs successfully

### Playwright errors
- **Cause**: System dependencies missing
- **Fix**: Ensure `playwright install-deps chromium` runs in build script

---

## Quick Commands

### Check if services exist on Render
```bash
# Install Render CLI (optional)
npm install -g @render-com/cli
render login
render list services
```

### Test backend locally
```bash
cd backend
pip install -r requirements.txt
python app.py
# Visit: http://localhost:5000
```

### Test frontend locally
```bash
cd frontend
npm install
npm run dev
# Visit: http://localhost:5173
```

---

## Current Status

✅ Code is ready for Python/Flask deployment
✅ render.yaml configured correctly
✅ Build script ready and executable
❌ Render service needs reconfiguration (currently set to Node.js)

**Next Action**: Go to Render Dashboard and follow Option 1 (Delete and Redeploy)
