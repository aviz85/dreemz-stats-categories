#!/bin/bash
# GitHub deployment script for Contabo VPS

echo "🚀 Deploying Dream Analytics from GitHub to Contabo"
echo "=================================================="

# Run this on your Contabo VPS to deploy from GitHub
cd /opt

# Remove old deployment if exists
sudo rm -rf /opt/dreemz-analytics-github

# Clone from GitHub
echo "📥 Cloning from GitHub..."
git clone -b github-clean https://github.com/aviz85/dreemz-stats-categories.git dreemz-analytics-github

cd dreemz-analytics-github

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install additional required packages
pip install sentence-transformers

echo "📋 You need to provide these files manually:"
echo "  1. dreams_complete.db (SQLite database)"
echo "  2. dreams_faiss_index.faiss (FAISS similarity index)"
echo "  3. dreams_faiss_mapping.json (FAISS ID mapping)"
echo ""
echo "💾 Transfer these files to /opt/dreemz-analytics-github/"
echo ""
echo "🔄 Then run:"
echo "   systemctl stop dreemz-analytics"
echo "   rm -rf /opt/dreemz-analytics"
echo "   ln -sf /opt/dreemz-analytics-github /opt/dreemz-analytics"
echo "   systemctl start dreemz-analytics"
echo ""
echo "✅ GitHub deployment ready!"

# Create simple transfer script
cat > transfer_large_files.sh << 'TRANSFER_EOF'
#!/bin/bash
echo "📦 Transfer large files from working deployment..."
cp /opt/dreemz-analytics-backup/dreams_complete.db .
cp /opt/dreemz-analytics-backup/dreams_faiss_index.faiss .
cp /opt/dreemz-analytics-backup/dreams_faiss_mapping.json .
echo "✅ Files transferred"
TRANSFER_EOF

chmod +x transfer_large_files.sh
echo "📦 Run ./transfer_large_files.sh to copy large files from backup"