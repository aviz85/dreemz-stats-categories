# Contabo Deployment Guide

## Quick Update (Most Common)

For regular code updates, just run:

```bash
./quick_update.sh
```

This will:
- Stop the service
- Pull latest changes
- Build frontend 
- Restart service
- Test API

## Full Deployment Setup

For first-time setup or major changes:

```bash
./deploy_update.sh
```

This comprehensive script will:
- Stop existing service
- Pull latest code from GitHub
- Create/activate Python virtual environment
- Install/update Python dependencies
- Create FAISS index files if missing
- Install/update Node.js dependencies
- Build production frontend
- Create systemd service (if doesn't exist)
- Start and test the service

## Manual Steps

### 1. Initial Server Setup
```bash
# Clone the repository
git clone https://github.com/aviz85/dreemz-stats-categories.git
cd dreemz-stats-categories
git checkout github-clean

# Make scripts executable
chmod +x *.sh

# Run full deployment
./deploy_update.sh
```

### 2. Environment Configuration
```bash
# Edit credentials (important!)
nano .env
```

Update with your actual credentials:
```
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

### 3. Large Files Setup
Upload these files manually to the server:
- `dreams_complete.db` (SQLite database)
- `dreams_faiss_index.faiss` (if you have it)
- `dreams_faiss_metadata.json` (if you have it)

The script will create FAISS files automatically if missing.

## Service Management

```bash
# Check status
sudo systemctl status flask-dreemz

# View logs
sudo journalctl -u flask-dreemz -f

# Manual restart
sudo systemctl restart flask-dreemz

# Stop service
sudo systemctl stop flask-dreemz

# Start service
sudo systemctl start flask-dreemz
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u flask-dreemz --no-pager -n 20

# Check if port is in use
sudo netstat -tulpn | grep :5000

# Manual test
cd /path/to/dreemz-stats-categories
source .venv/bin/activate
python3 app.py
```

### Frontend not loading
```bash
# Rebuild frontend
cd frontend
npm install
npm run build
```

### Database issues
```bash
# Check database file
ls -la dreams_complete.db

# Test database connection
sqlite3 dreams_complete.db "SELECT COUNT(*) FROM dreams;"
```

## File Structure on Server

```
/root/dreemz-stats-categories/  (or your chosen path)
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (create this)
├── .venv/                     # Python virtual environment
├── dreams_complete.db         # SQLite database (upload manually)
├── dreams_faiss_index.faiss   # FAISS index (auto-generated)
├── dreams_faiss_metadata.json # FAISS metadata (auto-generated)
├── frontend/
│   ├── package.json           # Node.js dependencies
│   ├── node_modules/          # Installed dependencies
│   └── src/                   # React source code
├── static/
│   └── bundle.js              # Built frontend (generated)
├── templates/
│   └── dashboard_spa.html     # HTML template (generated)
└── deploy_update.sh           # This deployment script
```

## Nginx Configuration (Optional)

If using nginx as reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```