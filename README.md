# Midnight-Travel-Booker

Automates Travel Site Booking

## Screenshots

View the application screenshots in the [`screenshots/`](screenshots/) directory. These showcase the complete user interface including:
- Landing page with pricing tiers
- Authentication (login/signup)
- User dashboard with booking statistics
- Bookings management
- Subscription selection
- Profile and settings

See [screenshots/README.md](screenshots/README.md) for detailed descriptions of each screenshot.

## Project Structure

```
├── backend/          # Node.js Express API
│   ├── index.js      # API server
│   └── package.json  # Backend dependencies
├── frontend/         # Web frontend
│   ├── server.js     # Static file server
│   ├── public/       # Static assets
│   └── package.json  # Frontend dependencies
└── render.yaml       # Render deployment configuration
```

## Local Development

### Backend

```bash
cd backend
npm install
npm start
```

The API will be available at `http://localhost:3001`

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/bookings` - List all bookings
- `POST /api/bookings` - Create a new booking (requires `destination` and `date` in request body)

## Deploy to Render

1. Fork this repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub account and select this repository
5. Render will automatically detect the `render.yaml` and deploy both services

### Manual Deployment

Alternatively, you can deploy each service manually:

#### Backend
1. Create a new Web Service on Render
2. Connect your repository
3. Set the Root Directory to `backend`
4. Build Command: `npm install`
5. Start Command: `npm start`

#### Frontend
1. Create a new Web Service on Render
2. Connect your repository
3. Set the Root Directory to `frontend`
4. Build Command: `npm install`
5. Start Command: `npm start`
6. Add environment variable `BACKEND_URL` pointing to your backend URL

## License

MIT
