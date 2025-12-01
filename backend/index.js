const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Midnight Travel Booker API is running' });
});

// Sample bookings endpoint
app.get('/api/bookings', (req, res) => {
  res.json({
    bookings: [
      { id: 1, destination: 'Paris', date: '2025-12-15', status: 'confirmed' },
      { id: 2, destination: 'Tokyo', date: '2025-12-20', status: 'pending' }
    ]
  });
});

// Create booking endpoint
app.post('/api/bookings', (req, res) => {
  const { destination, date } = req.body;
  if (!destination || !date) {
    return res.status(400).json({ error: 'Destination and date are required' });
  }
  res.status(201).json({
    id: Date.now(),
    destination,
    date,
    status: 'pending'
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
