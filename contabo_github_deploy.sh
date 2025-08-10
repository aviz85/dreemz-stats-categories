#!/bin/bash
# Complete GitHub deployment script for Contabo
# Run this on your Contabo VPS

set -e  # Exit on any error

echo "🚀 Starting GitHub deployment to Contabo..."

# Backup current deployment
echo "📦 Creating backup..."
sudo cp -r /opt/dreemz-analytics /opt/dreemz-analytics-backup 2>/dev/null || echo "No existing deployment to backup"

# Clone from GitHub
echo "📥 Cloning from GitHub..."
cd /opt
sudo rm -rf /opt/dreemz-analytics-github 2>/dev/null || true
sudo git clone -b github-clean https://github.com/aviz85/dreemz-stats-categories.git dreemz-analytics-github

# Set up Python environment
echo "🐍 Setting up Python environment..."
cd /opt/dreemz-analytics-github
sudo python3 -m venv .venv
sudo /opt/dreemz-analytics-github/.venv/bin/pip install -r requirements.txt
sudo /opt/dreemz-analytics-github/.venv/bin/pip install sentence-transformers

# Transfer large files if backup exists
echo "📂 Transferring large files..."
if [ -d "/opt/dreemz-analytics-backup" ]; then
    sudo cp /opt/dreemz-analytics-backup/dreams_complete.db /opt/dreemz-analytics-github/ 2>/dev/null || echo "Database not found in backup"
    sudo cp /opt/dreemz-analytics-backup/dreams_faiss_index.faiss /opt/dreemz-analytics-github/ 2>/dev/null || echo "FAISS index not found in backup"
    sudo cp /opt/dreemz-analytics-backup/dreams_faiss_mapping.json /opt/dreemz-analytics-github/ 2>/dev/null || echo "FAISS mapping not found in backup"
else
    echo "⚠️  No backup found - you'll need to upload the database and FAISS files manually"
fi

# Switch to GitHub deployment
echo "🔄 Switching to GitHub deployment..."
sudo systemctl stop dreemz-analytics 2>/dev/null || echo "Service not running"
sudo rm -rf /opt/dreemz-analytics 2>/dev/null || true
sudo ln -sf /opt/dreemz-analytics-github /opt/dreemz-analytics

# Start service
echo "🚀 Starting service..."
sudo systemctl start dreemz-analytics
sudo systemctl status dreemz-analytics --no-pager

echo ""
echo "✅ GitHub deployment complete!"
echo "📊 Dashboard should be accessible at: http://185.185.82.220"
echo ""
echo "🔄 For future updates, run:"
echo "   cd /opt/dreemz-analytics && sudo git pull origin github-clean && sudo systemctl restart dreemz-analytics"