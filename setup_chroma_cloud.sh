#!/bin/bash
# Setup Script untuk Chroma Cloud Integration

set -e

echo "🚀 Chroma Cloud Setup Script"
echo "============================="
echo ""

# Check environment variables
echo "📋 Checking Chroma Cloud credentials..."

if [ -z "$CHROMA_API_KEY" ]; then
    echo "❌ CHROMA_API_KEY not found in .env"
    exit 1
fi

if [ -z "$CHROMA_TENANT" ]; then
    echo "❌ CHROMA_TENANT not found in .env"
    exit 1
fi

if [ -z "$CHROMA_DATABASE" ]; then
    echo "❌ CHROMA_DATABASE not found in .env"
    exit 1
fi

echo "✅ All Chroma Cloud credentials found"
echo ""

# Step 1: Install dependencies
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

# Step 3: Test Chroma Cloud connection
echo ""
echo "🔗 Step 3: Testing Chroma Cloud connection..."

python -c "
from app import create_app
from app.chroma_integration import get_vector_store

app = create_app()
with app.app_context():
    store = get_vector_store()
    if store.is_healthy():
        stats = store.get_collection_stats()
        print('✅ Chroma Cloud connection successful!')
        print(f'   Server: {stats.get(\"server\", \"unknown\")}')
        print(f'   Database: {stats.get(\"collection_name\", \"unknown\")}')
        print(f'   Total chunks: {stats.get(\"total_chunks\", 0)}')
        print(f'   Total documents: {stats.get(\"total_documents\", 0)}')
    else:
        print('❌ Failed to connect to Chroma Cloud')
        exit(1)
"

# Step 4: List root folders
echo ""
echo "📁 Step 4: Checking Google Drive root folders..."

python -c "
from app.documents_handler import ROOT_FOLDERS, DISPLAY_NAMES

print('Configured Google Drive folders:')
for key, folder_id in ROOT_FOLDERS.items():
    display_name = DISPLAY_NAMES.get(key, key)
    print(f'  • {display_name}: {folder_id}')
"

# Step 5: Next steps
echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start application:"
echo "   python run.py"
echo ""
echo "2. (Optional) Index documents to Chroma Cloud:"
echo "   curl -X POST 'http://localhost:8000/api/admin/chroma/index-all' \\"
echo "     -H 'X-Admin-Key: <your-admin-key>'"
echo ""
echo "3. Check stats:"
echo "   curl 'http://localhost:8000/api/chat/stats'"
echo ""
echo "4. Test chat:"
echo "   curl -X POST 'http://localhost:8000/api/chat/ask' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'Cookie: session=<your-session>' \\"
echo "     -d '{\"question\":\"Bagaimana cara service?\"}'"
echo ""
echo "💡 Tips:"
echo "- First request might take longer (downloading embedding model ~400MB)"
echo "- Chroma data persisted in Chroma Cloud"
echo "- Chat history stored in database/users.db"
echo "- See CHROMA_SETUP.md for detailed documentation"
echo ""
