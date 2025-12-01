#!/usr/bin/env bash
# Simple build script - minimal dependencies
set -o errexit

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed!"
