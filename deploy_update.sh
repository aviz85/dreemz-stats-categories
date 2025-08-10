#!/bin/bash

# Contabo Server Update Script
# Run this script on the Contabo server to pull latest changes and restart services

set -e  # Exit on any error

echo "🚀 Starting Contabo server update..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

print_step "Current directory: $(pwd)"

# Step 1: Stop the current Flask service (if it exists)
print_step "Stopping Flask service..."
if sudo systemctl is-active --quiet dreemz-analytics 2>/dev/null; then
    sudo systemctl stop dreemz-analytics
    print_success "Flask service stopped"
else
    print_step "Flask service not running or doesn't exist yet"
fi

# Step 2: Git pull latest changes
print_step "Pulling latest changes from GitHub..."
git pull origin github-clean || {
    print_error "Failed to pull from GitHub"
    exit 1
}
print_success "Git pull completed"

# Step 3: Update Python dependencies
print_step "Updating Python dependencies..."
if [ -d ".venv" ]; then
    print_step "Using existing virtual environment"
    source .venv/bin/activate
else
    print_step "Creating new virtual environment"
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Fix Python 3.12+ distutils issue first
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
print_success "Python dependencies updated"

# Step 4: Create/update FAISS index if needed
print_step "Checking FAISS index files..."
if [ ! -f "dreams_faiss_index.faiss" ] || [ ! -f "dreams_faiss_metadata.json" ]; then
    print_step "Creating FAISS index files..."
    if [ -f "create_faiss_index.py" ]; then
        python3 create_faiss_index.py
        python3 create_metadata.py
        print_success "FAISS index created"
    else
        print_error "FAISS creation scripts not found"
    fi
else
    print_success "FAISS index files already exist"
fi

# Step 5: Check .env file
print_step "Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_step "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_step "⚠️  Please update .env file with your credentials"
    else
        echo "ADMIN_USERNAME=admin" > .env
        echo "ADMIN_PASSWORD=changeme123" >> .env
        print_step "⚠️  Default credentials created - please change them!"
    fi
fi
print_success "Environment configuration ready"

# Step 6: Frontend build
print_step "Building frontend..."
cd frontend

# Install/update Node.js dependencies
print_step "Installing/updating npm dependencies..."
npm install
print_success "NPM dependencies updated"

# Build production bundle
print_step "Building production bundle..."
npm run build
print_success "Frontend build completed"

cd ..

# Step 7: Update systemd service file if needed
print_step "Checking systemd service..."
SERVICE_FILE="/etc/systemd/system/dreemz-analytics.service"
if [ ! -f "$SERVICE_FILE" ]; then
    print_step "Creating systemd service file..."
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Flask Dreemz Analytics Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/.venv/bin
ExecStart=$(pwd)/.venv/bin/python3 $(pwd)/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable dreemz-analytics
    print_success "Systemd service created and enabled"
else
    print_success "Systemd service already exists"
fi

# Step 8: Start the Flask service
print_step "Starting Flask service..."
sudo systemctl start dreemz-analytics
sleep 3

# Step 9: Check service status
print_step "Checking service status..."
if sudo systemctl is-active --quiet dreemz-analytics; then
    print_success "Flask service is running!"
else
    print_error "Flask service failed to start"
    print_step "Checking logs..."
    sudo journalctl -u dreemz-analytics --no-pager -n 20
    exit 1
fi

# Step 10: Test the API
print_step "Testing API endpoint..."
sleep 2
if curl -f -s -u admin:changeme123 http://localhost:5000/api/status > /dev/null; then
    print_success "API is responding correctly!"
else
    print_error "API test failed"
    print_step "Service logs:"
    sudo journalctl -u dreemz-analytics --no-pager -n 10
fi

# Step 11: Display status
print_step "Final status check..."
echo "=================================="
echo "🎉 Deployment completed successfully!"
echo "=================================="
echo "📍 Service Status: $(sudo systemctl is-active dreemz-analytics)"
echo "📍 API Endpoint: http://localhost:5000"
echo "📍 Frontend files: Built and ready"
echo "📍 Database: $(ls -la dreams_complete.db 2>/dev/null | awk '{print $5}' | numfmt --to=iec-i --suffix=B || echo 'Not found')"
echo "📍 FAISS Index: $(ls -la dreams_faiss_index.faiss 2>/dev/null | awk '{print $5}' | numfmt --to=iec-i --suffix=B || echo 'Not found')"
echo ""
echo "🔗 View logs: sudo journalctl -u dreemz-analytics -f"
echo "🔄 Restart: sudo systemctl restart dreemz-analytics"
echo "🛑 Stop: sudo systemctl stop dreemz-analytics"
echo ""
print_success "Update completed! 🚀"