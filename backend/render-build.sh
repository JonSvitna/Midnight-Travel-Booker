#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎭 Installing Playwright..."
playwright install chromium || echo "⚠️ Playwright install had issues, continuing..."

echo "📚 Installing Playwright system dependencies..."
playwright install-deps chromium || echo "⚠️ Playwright deps install had issues, continuing..."

echo "✅ Build completed successfully!"
