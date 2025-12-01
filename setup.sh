#!/bin/bash

# Midnight Travel Booker - Development Setup Script

echo "🌙 Midnight Travel Booker Setup"
echo "================================"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"

# Setup backend environment
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file..."
    cp backend/.env.example backend/.env
    
    # Generate encryption key
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")
    
    if [ -n "$ENCRYPTION_KEY" ]; then
        sed -i.bak "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|" backend/.env
        echo "✅ Generated encryption key"
    else
        echo "⚠️  Could not generate encryption key automatically. Please set it manually."
    fi
    
    echo "⚠️  Please update backend/.env with your Stripe and SendGrid credentials"
else
    echo "✅ Backend .env already exists"
fi

# Setup frontend environment
if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cp frontend/.env.example frontend/.env
    echo "✅ Frontend .env created"
else
    echo "✅ Frontend .env already exists"
fi

# Build and start services
echo ""
echo "🚀 Building and starting services..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running"
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "📍 Services:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:5000"
    echo "   - Database: localhost:5432"
    echo ""
    echo "📚 Next steps:"
    echo "   1. Update backend/.env with your API keys"
    echo "   2. Restart services: docker-compose restart"
    echo "   3. Create admin user (see SETUP_GUIDE.md)"
    echo "   4. Visit http://localhost:3000"
    echo ""
    echo "📖 Documentation:"
    echo "   - Setup Guide: SETUP_GUIDE.md"
    echo "   - API Docs: API_DOCUMENTATION.md"
    echo ""
else
    echo "❌ Services failed to start. Check logs:"
    echo "   docker-compose logs"
fi
