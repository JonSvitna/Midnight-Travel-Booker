const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3001';

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'public')));

// API endpoint to get configuration
app.get('/api/config', (req, res) => {
  res.json({
    backendUrl: BACKEND_URL.startsWith('http') ? BACKEND_URL : `https://${BACKEND_URL}`
  });
});

// Handle all routes by serving index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend server is running on port ${PORT}`);
  console.log(`Backend URL configured as: ${BACKEND_URL}`);
});
