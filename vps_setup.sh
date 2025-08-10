#!/bin/bash
# Setup script for VPS (run this on the VPS after transfer)

set -e

echo "🖥️  Dream Analytics VPS Setup"
echo "============================="

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "🔧 Installing dependencies..."
apt install -y python3 python3-pip python3-venv nginx ufw

# Setup firewall
echo "🔐 Configuring firewall..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 5001
ufw --force enable

# Navigate to project directory
cd ~/dreemz-stats-categories

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service for auto-start
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/dreemz-analytics.service << EOF
[Unit]
Description=Dream Analytics Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/.venv/bin
Environment=PORT=5001
ExecStart=$(pwd)/.venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable dreemz-analytics
systemctl start dreemz-analytics

echo "🌐 Setting up Nginx reverse proxy..."
cat > /etc/nginx/sites-available/dreemz-analytics << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/dreemz-analytics /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo "🔗 Dashboard URL: http://YOUR_VPS_IP"
echo "🖥️  Service status: systemctl status dreemz-analytics"
echo "📊 Database size: $(du -h dreams_complete.db | cut -f1)"
echo "🔍 FAISS vectors: $(wc -l dreams_faiss_metadata.json | cut -d' ' -f1) entries"
echo ""
echo "🛠️  Management commands:"
echo "   • Start:   systemctl start dreemz-analytics"
echo "   • Stop:    systemctl stop dreemz-analytics"
echo "   • Restart: systemctl restart dreemz-analytics"
echo "   • Logs:    journalctl -u dreemz-analytics -f"