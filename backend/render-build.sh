#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎭 Installing Playwright..."
playwright install chromium

echo "📚 Installing Playwright system dependencies..."
playwright install-deps chromium

echo "🗄️ Setting up database..."
python -c "
from app import create_app
from models import db

app = create_app()
with app.app_context():
    try:
        db.create_all()
        print('✅ Database tables created successfully')
    except Exception as e:
        print(f'⚠️ Database setup warning: {e}')
        print('Database may already be initialized')
"

echo "✅ Build completed successfully!"
