#!/bin/bash

# Quick Update Script for Contabo
# For when you just need to pull changes and restart

set -e

echo "⚡ Quick update starting..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Stop service (if it exists)
print_step "Stopping service..."
if sudo systemctl is-active --quiet dreemz-analytics 2>/dev/null; then
    sudo systemctl stop dreemz-analytics
    print_success "Service stopped"
else
    print_step "Service not running or doesn't exist yet"
fi

# Pull changes
print_step "Pulling latest code..."
git pull origin github-clean

# Quick frontend build if needed
if [ -f "frontend/package.json" ]; then
    print_step "Quick frontend build..."
    cd frontend
    npm run build
    cd ..
fi

# Activate venv and update if requirements changed
if [ -f "requirements.txt" ]; then
    print_step "Checking Python dependencies..."
    source .venv/bin/activate
    
    # Fix Python 3.12+ distutils issue
    pip install --upgrade pip setuptools wheel --quiet
    pip install -r requirements.txt --quiet
fi

# Start service
print_step "Starting service..."
sudo systemctl start dreemz-analytics

# Wait and test
sleep 3
if sudo systemctl is-active --quiet dreemz-analytics; then
    print_success "Service restarted successfully! 🚀"
    print_step "Testing API..."
    if curl -f -s -u admin:changeme123 http://localhost:5000/api/status > /dev/null; then
        print_success "API is responding! ✨"
    else
        echo "⚠️  API test failed - check logs"
    fi
else
    echo "❌ Service failed to start"
    sudo journalctl -u dreemz-analytics --no-pager -n 10
fi