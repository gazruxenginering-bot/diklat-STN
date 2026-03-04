#!/bin/bash
# Chroma Setup & Deployment Script

set -e

echo "🚀 Chroma Vector Database Setup Script"
echo "========================================"

# Step 1: Install dependencies
echo ""
echo "📦 Step 1: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 2: Database migration
echo ""
echo "🗄️  Step 2: Running database migrations..."
if [ ! -d "app/migrations" ]; then
    echo "Creating migrations folder..."
    flask db init
fi

echo "Creating migration for Chroma models..."
flask db migrate -m "Add Chroma and chat models"

echo "Applying migration..."
flask db upgrade

# Step 3: Create chroma data directory
echo ""
echo "📁 Step 3: Creating Chroma data directory..."
mkdir -p chroma_data
chmod 755 chroma_data

# Step 4: Verify setup
echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Start application:"
echo "   python run.py"
echo ""
echo "2. Index documents (after app is running):"
echo "   curl -X POST 'http://localhost:8000/api/admin/chroma/index-all' \\"
echo "     -H 'X-Admin-Key: <your-admin-key>'"
echo ""
echo "3. Check stats:"
echo "   curl 'http://localhost:8000/api/chat/stats'"
echo ""
echo "4. Read documentation:"
echo "   cat CHROMA_SETUP.md"
echo ""
echo "💡 Tips:"
echo "- First search might be slow (downloading embedding model)"
echo "- Chroma data persisted at: chroma_data/"
echo "- Database at: database/users.db"
echo ""
