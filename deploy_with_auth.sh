#!/bin/bash
# Deploy authentication update to Contabo VPS

echo "🔐 Deploying authentication update to Dream Analytics Dashboard"
echo "============================================================="

# Create .env file on VPS with secure password
echo "📝 Creating secure .env file on VPS..."
cat << 'ENV_FILE' > /tmp/temp_env
# Dream Analytics Dashboard Authentication
# IMPORTANT: Change this password immediately!

ADMIN_USERNAME=admin
ADMIN_PASSWORD=DreemzSecure2024!

# Port configuration
PORT=5001
ENV_FILE

echo "📦 Instructions for deploying to Contabo VPS:"
echo ""
echo "1. Push changes to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add authentication to dashboard'"
echo "   git push origin github-clean"
echo ""
echo "2. On your Contabo VPS, run these commands:"
echo ""
echo "cd /opt/dreemz-analytics"
echo ""
echo "# Pull latest changes"
echo "git pull origin github-clean"
echo ""
echo "# Create .env file (if not exists)"
echo "cat > .env << 'EOF'"
echo "ADMIN_USERNAME=admin"
echo "ADMIN_PASSWORD=YourSecurePassword123!"
echo "PORT=5001"
echo "EOF"
echo ""
echo "# Install new dependencies"
echo "source .venv/bin/activate"
echo "pip install Flask-HTTPAuth python-dotenv flask-cors"
echo ""
echo "# Rebuild frontend with auth support"
echo "cd frontend"
echo "npm install"
echo "npm run build"
echo "cd .."
echo ""
echo "# Restart service"
echo "sudo systemctl restart dreemz-analytics"
echo "sudo systemctl status dreemz-analytics"
echo ""
echo "✅ Dashboard will be protected with basic authentication!"
echo "📱 Access at: http://185.185.82.220"
echo "🔑 Default: admin / YourSecurePassword123!"
echo ""
echo "⚠️  IMPORTANT: Change the password in .env file immediately!"