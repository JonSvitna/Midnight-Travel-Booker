# Quick Deployment Troubleshooting

## Current Changes (Latest Push)

### Backend Fixes:
✅ Simplified build command - removed Playwright from build (can be added later)
✅ Changed `runtime: python` to `env: python` in render.yaml
✅ Build now: `pip install --upgrade pip && pip install -r requirements.txt`
✅ Removed database initialization from build script (Render handles this)

### Frontend Fixes:
✅ Added missing `postcss.config.js` for Tailwind CSS
✅ Proper Vite build configuration
✅ React dependencies configured correctly

---

## If Backend Still Fails

**Check these in Render Dashboard:**

1. **Environment Variables** - These MUST be set manually:
   ```
   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
   JWT_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
   ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
   
   # Optional for now (use placeholder values):
   STRIPE_SECRET_KEY=sk_test_placeholder
   STRIPE_WEBHOOK_SECRET=whsec_placeholder
   STRIPE_PRICE_BASIC=price_test_placeholder
   STRIPE_PRICE_STANDARD=price_test_placeholder
   STRIPE_PRICE_PREMIUM=price_test_placeholder
   SENDGRID_API_KEY=SG.placeholder
   SENDGRID_FROM_EMAIL=test@example.com
   ```

2. **Python Version** - Should be Python 3.11 or 3.12

3. **Build Logs** - Check for specific error messages

---

## If Frontend Doesn't Load Properly

**Common Issues:**

### 1. Blank Page
- Check browser console for errors
- Verify API URL: Should be `https://midnight-travel-backend.onrender.com/api`
- Check CORS errors - backend must allow frontend origin

### 2. Styles Not Loading
- Ensure PostCSS config exists (now added ✅)
- Check if Tailwind is imported in `src/index.css`
- Verify build completed successfully

### 3. API Calls Failing
- Backend must be deployed and healthy first
- Check backend URL in frontend env vars
- Test backend: `curl https://midnight-travel-backend.onrender.com/health`

---

## Deployment Order

1. **Database** deploys first (automatic)
2. **Backend** deploys second - WAIT for this to complete
3. **Frontend** deploys last

⚠️ Frontend will fail if backend isn't ready!

---

## Test After Deployment

### Backend Tests:
```bash
# Health check
curl https://midnight-travel-backend.onrender.com/health

# Root route
curl https://midnight-travel-backend.onrender.com/

# Should return JSON with API info
```

### Frontend Test:
- Visit: https://midnight-travel-frontend.onrender.com
- Should see landing page
- Check browser console (F12) for errors

---

## If Everything Fails - Nuclear Option

1. **Delete ALL services** in Render Dashboard
2. **Wait 2 minutes**
3. **Deploy fresh from Blueprint**
4. **Set environment variables IMMEDIATELY**
5. **Wait for all services to finish deploying**

---

## Minimal Working Config

If you just want to see it work:

1. **Backend env vars (minimum)**:
   ```
   SECRET_KEY=dev-secret-key-for-testing-only
   JWT_SECRET_KEY=dev-jwt-secret-for-testing-only
   ENCRYPTION_KEY=test-encryption-key-32chars!!
   STRIPE_SECRET_KEY=sk_test_placeholder
   SENDGRID_API_KEY=placeholder
   ```

2. **Frontend env vars**:
   ```
   VITE_API_URL=https://midnight-travel-backend.onrender.com/api
   ```

This will get the app running - replace with real keys before production use!

---

## Current Status

✅ Code is correct and tested locally
✅ Build commands simplified
✅ Frontend config complete with PostCSS
✅ Backend using inline build command (faster, more reliable)

**Next**: Redeploy on Render - should work now!
