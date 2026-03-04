# 🎯 Chroma Cloud Configuration - Quick Reference

## ✅ Your Setup

```
Gemini API
├── API Key: AIzaSyBnOam5Cak2qYnV3tZ5b67q_yIJdQUcxeY
└── Status: ✓ Ready

Google Drive Folders
├── EBOOKS: 12ffd7GqHAiy3J62Vu65LbVt6-ultog5Z
├── Pengetahuan: 1Y2SLCbyHoB53BaQTTwRta2T6dv_drRll
├── Service_Manual_1: 1CHz8UWZXfJtXlcjp9-FPAo-t_KkfTztW
└── Service_Manual_2: 1_SsZ7SkaZxvXUZ6RUAA_o7WR_GAtgEwT
   └── Status: ✓ Configured in app/documents_handler.py

Chroma Cloud
├── Host: api.trychroma.com
├── Database: DIKLAT-STN
├── Tenant: 5926624f-3d5b-4c04-875f-66d530572b0a
├── API Key: ck-4XMkqE5Wi5DfzQEkcso6N8RSf1PtewXD5wU4UBXTn81n
└── Dashboard: https://www.trychroma.com/gazruxenginering/aws-us-east-1/DIKLAT-STN/source
   └── Status: ✓ Cloud account active
```

---

## 🚀 Start Application

### Option 1: Quick Start

```bash
# Navigate to project
cd /workspaces/diklat-STN

# Install dependencies
pip install -r requirements.txt

# Run database migrations
flask db migrate -m "Add Chroma models"
flask db upgrade

# Start application
python run.py
```

### Option 2: Automated Setup Script

```bash
bash setup_chroma_cloud.sh
```

**This script will:**
1. ✓ Verify Chroma Cloud credentials
2. ✓ Install dependencies
3. ✓ Run database migrations
4. ✓ Test Chroma Cloud connection
5. ✓ List configured Google Drive folders

---

## 🔗 API Endpoints

### Chat Endpoints

```bash
# 1. Tanya pertanyaan dengan RAG
POST /api/chat/ask
Content-Type: application/json
Cookie: session=<your-session>

{
  "question": "Bagaimana cara setting valve clearance?",
  "use_documents": true,
  "search_limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Berdasarkan dokumen yang ditemukan...",
  "sources": [
    {
      "file_id": "abc123",
      "file_name": "Service Manual.pdf",
      "relevance": 0.95
    }
  ],
  "session_id": 123,
  "with_rag": true,
  "model": "gemini-1.5-flash",
  "generated_at": "2024-02-22T10:30:00"
}
```

### Get Chat History

```bash
GET /api/chat/history?limit=20
Cookie: session=<your-session>
```

### Get Chroma Stats

```bash
GET /api/chat/stats
```

**Response:**
```json
{
  "success": true,
  "vector_store": {
    "total_chunks": 5432,
    "total_documents": 23,
    "server": "Chroma Cloud",
    "host": "api.trychroma.com"
  }
}
```

---

## ⚙️ Admin Operations

### Index All Documents

```bash
# Index semua dokumen dari 4 Google Drive folders ke Chroma Cloud
curl -X POST 'http://localhost:8000/api/admin/chroma/index-all' \
  -H 'X-Admin-Key: your-admin-key'
```

### Check Indexed Documents

```bash
curl 'http://localhost:8000/api/admin/chroma/list-indexed' \
  -H 'X-Admin-Key: your-admin-key'
```

### Delete Document from Chroma

```bash
curl -X DELETE 'http://localhost:8000/api/admin/chroma/delete-file/123' \
  -H 'X-Admin-Key: your-admin-key'
```

---

## 📊 Environment Variables (.env)

```bash
# Flask
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=a-stable-secret-key-here

# Gemini API
GEMINI_API_KEY=AIzaSyBnOam5Cak2qYnV3tZ5b67q_yIJdQUcxeY

# Chroma Cloud
CHROMA_CLOUD=true
CHROMA_HOST=api.trychroma.com
CHROMA_API_KEY=ck-4XMkqE5Wi5DfzQEkcso6N8RSf1PtewXD5wU4UBXTn81n
CHROMA_TENANT=5926624f-3d5b-4c04-875f-66d530572b0a
CHROMA_DATABASE=DIKLAT-STN

# Admin
ADMIN_API_KEY=your-admin-key-here

# Database
DATABASE_URL=sqlite:///database/users.db
```

---

## ✅ Verification Checklist

### Before Starting App
- [ ] `.env` file created with Chroma Cloud credentials
- [ ] `credentials.json` exists (Google Drive API)
- [ ] Python packages installed: `pip install -r requirements.txt`

### After Starting App
- [ ] Test Chroma connection: `curl http://localhost:8000/api/chat/stats`
- [ ] Verify response shows: `"server": "Chroma Cloud"`

### For Chat to Work
- [ ] User logged in (session cookie)
- [ ] Documents indexed to Chroma Cloud
- [ ] Gemini API key valid
- [ ] No rate limit hits

---

## 🐛 Troubleshooting

### "Failed to connect to Chroma Cloud"
```bash
# Check credentials
echo $CHROMA_API_KEY
echo $CHROMA_TENANT

# Verify in .env file
cat .env | grep CHROMA

# Test connection
python -c "
from app import create_app
from app.chroma_integration import get_vector_store
app = create_app()
with app.app_context():
    store = get_vector_store()
    print('Healthy' if store.is_healthy() else 'Error')
"
```

### "No documents found"
```bash
# Index documents
curl -X POST 'http://localhost:8000/api/admin/chroma/index-all' \
  -H 'X-Admin-Key: admin-key-change-me'

# Check indexing status
curl http://localhost:8000/api/admin/chroma/list-indexed \
  -H 'X-Admin-Key: admin-key-change-me'
```

### "Embedding model download failed"
```bash
# Wait for first request (downloads ~400MB)
# Or pre-download:
python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

---

## 📈 Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| First request | 20-30s | Model download + embedding |
| Subsequent requests | 2-5s | Cached model |
| Chroma search | 100-200ms | Vector similarity |
| Gemini response | 2-5s | LLM generation |
| **Total user experience** | **5-10s** | From Q to A |

---

## 🔒 Security

### Credentials Storage
- ✅ `.env` file (local, never commit)
- ✅ Environment variables (production)
- ❌ Never hardcode in code
- ❌ Never commit credentials.json

### Add to .gitignore
```bash
.env
.env.local
.env.*.local
credentials.json
chroma_data/
__pycache__/
instance/
*.pyc
*.db
```

---

## 📚 Documentation Files

- **[CHROMA_SETUP.md](CHROMA_SETUP.md)** - Full setup guide (Local + Cloud)
- **[CHROMA_CLOUD.md](CHROMA_CLOUD.md)** - Detailed Chroma Cloud guide
- **[CHROMA_IMPLEMENTATION_SUMMARY.md](CHROMA_IMPLEMENTATION_SUMMARY.md)** - Architecture overview

---

## 🎓 Next Steps

1. **✓ Done:** Setup Chroma Cloud credentials
2. **Next:** Run `bash setup_chroma_cloud.sh`
3. **Then:** Test `/api/chat/stats` endpoint
4. **Finally:** Index documents with `/api/admin/chroma/index-all`

---

## 📞 Support Resources

- **Chroma Cloud Dashboard:** https://www.trychroma.com/gazruxenginering/aws-us-east-1/DIKLAT-STN/source
- **Chroma Docs:** https://docs.trychroma.com/
- **Gemini API Docs:** https://ai.google.dev/
- **Flask Docs:** https://flask.palletsprojects.com/

---

**Configuration Date:** Feb 22, 2024
**Chroma Cloud Status:** ✅ ACTIVE
**Google Drive Status:** ✅ 4 FOLDERS CONFIGURED
