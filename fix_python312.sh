#!/bin/bash

# Quick fix for Python 3.12 distutils issue
# Run this on Contabo if you're getting distutils errors

echo "🔧 Fixing Python 3.12 distutils issue..."

# Activate the virtual environment
source .venv/bin/activate

# Install setuptools which provides distutils replacement
echo "📦 Installing setuptools and wheel..."
pip install --upgrade pip setuptools wheel

# Now install requirements
echo "📋 Installing requirements..."
pip install -r requirements.txt

echo "✅ Python 3.12 distutils issue fixed!"
echo "Now run: sudo systemctl restart dreemz-analytics"