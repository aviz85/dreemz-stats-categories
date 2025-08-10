#!/bin/bash
# Transfer complete dream analytics project to VPS

set -e

echo "🚀 Dream Analytics VPS Transfer Script"
echo "======================================"

# Configuration
PROJECT_DIR="/Users/aviz/dreemz-stats-categories"
ARCHIVE_NAME="dreemz-analytics-complete.tar.gz"

# Check if VPS details are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <vps-user@vps-ip> <destination-path>"
    echo "Example: $0 root@192.168.1.100 /home/projects/"
    exit 1
fi

VPS_TARGET="$1"
DEST_PATH="$2"

echo "📦 Creating complete project archive..."
echo "   Source: $PROJECT_DIR"
echo "   Archive: $ARCHIVE_NAME"

# Create archive excluding unnecessary files
tar -czf "$ARCHIVE_NAME" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="node_modules" \
    --exclude=".git" \
    "$PROJECT_DIR"

ARCHIVE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
echo "   ✅ Archive created: $ARCHIVE_SIZE"

echo ""
echo "📤 Transferring to VPS..."
echo "   Target: $VPS_TARGET:$DEST_PATH"

# Transfer archive
scp "$ARCHIVE_NAME" "$VPS_TARGET:$DEST_PATH"

echo "   ✅ Transfer complete!"

echo ""
echo "🔧 Setting up on VPS..."

# Connect to VPS and setup
ssh "$VPS_TARGET" << EOF
cd "$DEST_PATH"
echo "📁 Extracting archive..."
tar -xzf "$ARCHIVE_NAME"

echo "🐍 Setting up Python environment..."
cd dreemz-stats-categories
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server:"
echo "   cd $DEST_PATH/dreemz-stats-categories"
echo "   source .venv/bin/activate"
echo "   PORT=5001 python3 app.py"
echo ""
echo "🌐 Access at: http://YOUR_VPS_IP:5001"
EOF

echo ""
echo "🧹 Cleaning up local archive..."
rm "$ARCHIVE_NAME"

echo ""
echo "✅ Complete! Your dream analytics dashboard is now on the VPS."
echo "🔗 SSH to continue: ssh $VPS_TARGET"