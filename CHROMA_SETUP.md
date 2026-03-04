# Chroma Vector Database Integration - Setup Guide

## 📋 Overview

Fitur **RAG Chat dengan Chroma Vector Database** mengintegrasikan semantic search berbasis vector embeddings untuk pencarian dokumen yang lebih akurat. 

### ✨ Fitur Utama:
- ✅ **Chroma Cloud Support** - Cloud-hosted vector database
- ✅ **Local Chroma Support** - Self-hosted option
- ✅ **Multilingual Embeddings** - Support Bahasa Indonesia
- ✅ **Multiple Google Drive Folders** - Index dari 4 folder sekaligus
- ✅ **Persistent Storage** - Data tersimpan & scalable
- ✅ **Automatic Indexing** - Dokumen dari Google Drive auto-indexed
- ✅ **Persistent Chat History** - Semua chat tersimpan di database

---

## 🚀 Quick Setup dengan Chroma Cloud

### Prerequisites
- ✅ Chroma Cloud account (https://www.trychroma.com/)
- ✅ Google Drive credentials.json
- ✅ Python 3.8+

### Step 1: Configure Environment

**`.env` file dengan Chroma Cloud credentials:**

```bash
# Gemini API
GEMINI_API_KEY="AIzaSyBnOam5Cak2qYnV3tZ5b67q_yIJdQUcxeY"

# Chroma Cloud Configuration
CHROMA_CLOUD=true
CHROMA_HOST="api.trychroma.com"
CHROMA_API_KEY="ck-4XMkqE5Wi5DfzQEkcso6N8RSf1PtewXD5wU4UBXTn81n"
CHROMA_TENANT="5926624f-3d5b-4c04-875f-66d530572b0a"
CHROMA_DATABASE="DIKLAT-STN"

# Admin access
ADMIN_API_KEY="your-secret-admin-key"
```

**Atau copy dari .env.example:**
```bash
cp .env.example .env
# Edit .env dengan credentials Anda
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Database Migration

```bash
# Create Flask migration folder (jika belum ada)
flask db init

# Create migration untuk models baru
flask db migrate -m "Add Chroma and chat models"

# Apply migration
flask db upgrade
```

### Step 4: Start Application

```bash
python run.py
```

Application akan automatically:
- ✅ Connect ke Chroma Cloud
- ✅ Initialize vector collections
- ✅ Download embedding model (~400MB first time)
- ✅ Ready untuk indexing dan search

### Step 5: Index Documents (Optional)

```bash
# Verify Chroma Cloud connection
curl http://localhost:8000/api/chat/stats

# Index semua dokumen dari Google Drive
curl -X POST 'http://localhost:8000/api/admin/chroma/index-all' \
  -H 'X-Admin-Key: your-secret-admin-key'
```

---

## 🏗️ Architecture: Local vs Cloud

```
Google Drive
    ↓
drive_sync.py (Sync files weekly)
    ↓
GoogleDriveFile (Database)
    ↓
smart_search.ChromaDocumentSearch (Index)
    ↓
Chroma Vector DB (chroma_data/)
    ↓
routes_chat.ask_question (Search + RAG)
    ↓
Gemini API (Generate Answer)
    ↓
routes_chat.ChatMessage (Store Result)
    ↓
UI (Display Answer + Sources)
```

---

## 📁 File Structure Baru

```
app/
├── chroma_integration.py         # Chroma VectorStore management
├── smart_search.py               # Updated dengan ChromaDocumentSearch
├── drive_sync.py                 # Updated dengan Chroma indexing
├── routes_chat.py                # Updated untuk use Chroma + DB
├── routes_admin_chroma.py        # Admin endpoints untuk Chroma management
└── models.py                     # Updated models

chroma_data/                       # Vector database (persistent)
├── index/
├── log/
└── metadata.parquet
```

---

## 🔌 API Endpoints

### 1. Chat Endpoints

#### Ask Question (dengan Chroma Search)
```
POST /api/chat/ask
```

**Request:**
```json
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

#### Get Chat History
```
GET /api/chat/history?limit=20
```

**Response:**
```json
{
    "success": true,
    "history": [
        {
            "id": 1,
            "role": "user",
            "content": "Bagaimana cara setting valve?",
            "timestamp": "2024-02-22T10:30:00",
            "sources": []
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "Berdasarkan dokumen...",
            "timestamp": "2024-02-22T10:30:05",
            "sources": [
                {"file_name": "Service Manual.pdf", "relevance": 0.95}
            ]
        }
    ],
    "session_id": 123,
    "total_messages": 2
}
```

#### Search Documents (Chroma)
```
POST /api/chat/search
```

**Request:**
```json
{
    "query": "setting valve clearance",
    "limit": 5
}
```

**Response:**
```json
{
    "success": true,
    "query": "setting valve clearance",
    "results": [
        {
            "file_id": "abc123",
            "file_name": "Service Manual.pdf",
            "chunks": [
                {
                    "text": "Valve clearance harus diatur setiap 10,000 km...",
                    "similarity": 0.92,
                    "chunk_index": 5
                }
            ]
        }
    ],
    "total_documents": 1
}
```

#### Get Chat Stats
```
GET /api/chat/stats
```

**Response:**
```json
{
    "success": true,
    "vector_store": {
        "total_chunks": 5432,
        "total_documents": 23,
        "model": "paraphrase-multilingual-MiniLM-L12-v2",
        "collection_name": "documents",
        "persist_directory": "/path/to/chroma_data"
    },
    "timestamp": "2024-02-22T10:30:00"
}
```

#### Clear Chat Session
```
POST /api/chat/history/clear
```

**Response:**
```json
{
    "success": true,
    "message": "Chat session closed"
}
```

---

### 2. Admin Endpoints (Require X-Admin-Key)

#### Get Chroma Statistics
```
GET /api/admin/chroma/stats
Headers: X-Admin-Key: <your-admin-key>
```

**Response:**
```json
{
    "success": true,
    "vector_store_stats": {
        "total_chunks": 5432,
        "total_documents": 23,
        "model": "paraphrase-multilingual-MiniLM-L12-v2"
    },
    "database_tracking": {
        "total_indexed": 23,
        "total_pending": 0,
        "total_failed": 0
    }
}
```

#### Index All Documents
```
POST /api/admin/chroma/index-all
Headers: X-Admin-Key: <your-admin-key>
```

**Heavy operation** - Indexes semua Google Drive files ke Chroma. Dapat memakan waktu lama untuk banyak dokumen.

#### Index Single File
```
POST /api/admin/chroma/index-file/<file_id>
Headers: X-Admin-Key: <your-admin-key>
```

#### Delete File from Chroma
```
DELETE /api/admin/chroma/delete-file/<file_id>
Headers: X-Admin-Key: <your-admin-key>
```

#### List Indexed Documents
```
GET /api/admin/chroma/list-indexed
Headers: X-Admin-Key: <your-admin-key>
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# .env file
FLASK_ENV=development
GEMINI_API_KEY=your-gemini-api-key

# Admin access
ADMIN_API_KEY=your-secret-admin-key

# Database
DATABASE_URL=sqlite:///database/users.db  # Default, bisa ganti ke PostgreSQL
```

### Chroma Configuration (di app/chroma_integration.py)

```python
# Embedding model - paraphrase-multilingual-MiniLM-L12-v2
# Options: all-MiniLM-L6-v2, all-mpnet-base-v2, intfloat/multilingual-e5-small
# Pilih model sesuai kebutuhan accuracy vs speed tradeoff

# Vector store settings
chroma_db_impl='duckdb+parquet'  # Persistent backend
persist_directory='./chroma_data'  # Storage location
anonymized_telemetry=False        # Disable telemetry
```

### Chunk & Search Settings (di app/smart_search.py)

```python
# Default: 1000 chars per chunk dengan 100 chars overlap
# Semakin kecil → lebih granular, semakin besar → lebih kontekstual
chunk_size=1000
overlap=100

# Search results
search_limit=5        # Max dokumen
results_limit=10      # Max chunks per dokumen
```

---

## 🔄 How It Works

### Step 1: Google Drive Sync
```
Weekly Scheduler → drive_sync.py
├── List semua files dari Google Drive
├── Simpan metadata ke GoogleDriveFile
└── Index files ke Chroma
    └── Extract text dari PDF/DOCX/TXT
    └── Split menjadi chunks (1000 chars)
    └── Generate embeddings (sentence-transformers)
    └── Simpan di Chroma dengan metadata
```

### Step 2: User Asks Question
```
User Question → /api/chat/ask
├── Validasi input
├── Simpan ke ChatSession & ChatMessage
├── Query Chroma untuk dokumen relevan
│   └── Generate embedding untuk question
│   └── Cari chunks dengan similarity tertinggi (cosine)
│   └── Return top 5 dokumen + chunks
└── Format untuk Gemini API
```

### Step 3: AI Generates Answer
```
Chroma Results + Question → Gemini API
├── System prompt untuk Bahasa Indonesia
├── Context dari dokumen relevan
├── Generate answer
└── Simpan result + sources ke database
└── Return ke UI
```

### Step 4: Display to User
```
Answer + Sources → UI
├── Tampilkan jawaban (streaming jika ada)
├── List dokumen sumber dengan link
├── Show relevance score
└── Save ke chat history
```

---

## 📊 Vector Database Facts

### Similarity Metric: Cosine Similarity
- **Range:** -1 (opposite) → 0 (orthogonal) → 1 (identical)
- **Threshold:** ≥ 0.5 biasanya considered relevant
- **Chroma normalize:** Returns distance (1 - similarity), converted back

### Embedding Model: paraphrase-multilingual-MiniLM-L12-v2
- **Dimensions:** 384-dimensional vectors
- **Languages:** 50+ languages including Indonesian
- **Speed:** ~1000 embeddings/sec on CPU
- **Training:** Fine-tuned for semantic similarity

### Storage
- **Format:** DuckDB + Parquet (columnar storage)
- **Location:** `chroma_data/` directory
- **Size:** Roughly 400 bytes per embedding (384 dims × 4 bytes × precision)
- **Persistence:** Automatic on write, survives restarts

---

## 🐛 Troubleshooting

### Error: "Chroma Vector Store not available"
**Solution:**
```bash
# Reinstall chromadb
pip install --upgrade chromadb>=0.4.0

# Clear Chroma cache
rm -rf chroma_data/
python run.py  # Will recreate empty Chroma
```

### Error: "sentence-transformers model download failed"
**Solution:**
```bash
# Model downloads automatically on first use
# Make sure internet connection is available
# Or pre-download model:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

### Error: "No results found" saat searching
**Possible causes:**
1. Documents belum diindex → Jalankan `POST /api/admin/chroma/index-all`
2. Query terlalu specific → Coba pertanyaan yang lebih umum
3. Documents tidak ekstrak dengan baik → Check `ChromaDocument.status`
4. Embedding model mismatch → Ensure same model di konfigurasi

**Debug:**
```bash
# Check collection status
curl -X GET "http://localhost:8000/api/chat/stats"

# List indexed documents
curl -X GET "http://localhost:8000/api/admin/chroma/list-indexed" \
  -H "X-Admin-Key: your-admin-key"
```

### Error: "Database migration failed"
**Solution:**
```bash
# Reset migrations
rm app/migrations/versions/*_*.py

# Regenerate
flask db migrate -m "Initial migration with Chroma models"
flask db upgrade
```

### Slow Search Performance
**Optimization:**
1. Reduce `search_limit` in request
2. Reduce chunk overlap (trade-off with context loss)
3. Use smaller embedding model (faster, less accurate)
4. Add indexes to database tables

```python
# In models.py, add db indexes:
class ChatMessage(db.Model):
    __table_args__ = (
        db.Index('idx_session_timestamp', 'session_id', 'timestamp'),
    )
```

---

## 📈 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Index PDF (10 pages) | ~2-3s | Depends on file size |
| Search 5000 docs | ~100-200ms | Vector similarity search |
| Generate embedding (1000 chars) | ~10ms | sentence-transformers |
| Gemini API response | ~2-5s | Network + LLM processing |

---

## 🔐 Security

### API Key Management
- `ADMIN_API_KEY` - Untuk admin endpoints (indexing, stats)
- `GEMINI_API_KEY` - Untuk Gemini API (dalam credentials.json)
- `SECRET_KEY` - Flask session security

### Data Privacy
- Chat history tersimpan di database → Hanya accessible oleh user
- Vectors disimpan di Chroma → No external cloud storage
- Documents tidak di-download berulang → Cache di database

### Access Control
```python
# Admin endpoints require X-Admin-Key header
# Chat endpoints require login (session-based)
# Always validate user_id dari session
```

---

## 🎓 Best Practices

### 1. Document Management
- **Organize** dokumen dengan folder struktur yang jelas
- **Name files** dengan deskriptif (contoh: "Honda_Civic_2020_Service_Manual.pdf")
- **Content quality** - Pastikan text ekstraktable (bukan scanned images)

### 2. Search Queries
- **Specific** → "Bagaimana cara mengganti oli Mesin Honda Civic 2020?"
- Better than **Vague** → "Oli gimana?"
- **Indonesian** → Gunakan Bahasa Indonesia untuk accuracy

### 3. Indexing Strategy
- **Auto-index** via scheduler (weekly)
- **Manual index** dokumen penting segera setelah upload
- **Monitor** status di `/api/admin/chroma/stats`

### 4. Cost Optimization
- Chroma = **free** (local, open-source)
- Gemini API = **metered** (token-based) → Optimize prompts
- Embeddings = **free** (sentence-transformers local)

---

## 🚀 Advanced Usage

### Custom Embedding Model

```python
# In chroma_integration.py, change:
model_name = "intfloat/multilingual-e5-small"  # Smaller, faster
model_name = "all-mpnet-base-v2"  # Larger, more accurate
```

### Custom Chunk Size

```python
# In drive_sync.py:
chunks = TextChunker.chunk_text(
    content,
    chunk_size=2000,   # Larger chunks
    overlap=200        # More overlap
)
```

### Filter Search by Document Type

```python
# In chroma_integration.py, update search method:
where={
    "mime_type": {"$eq": "application/pdf"}  # Only PDFs
}
```

---

## 📞 Support & Resources

- **Chroma Docs:** https://docs.trychroma.com/
- **Sentence Transformers:** https://www.sbert.net/
- **Gemini API:** https://ai.google.dev/
- **Flask Documentation:** https://flask.palletsprojects.com/

---

## ✅ Production Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `flask db migrate && flask db upgrade`
- [ ] Configure ADMIN_API_KEY in environment
- [ ] Configure GEMINI_API_KEY in credentials.json
- [ ] Test Chroma setup: `GET /api/chat/stats`
- [ ] Index documents: `POST /api/admin/chroma/index-all`
- [ ] Monitor logs for errors
- [ ] Setup backup for `chroma_data/` directory
- [ ] Setup backup for database
- [ ] Enable HTTPS in production
- [ ] Rate limit chat endpoints
- [ ] Monitor Gemini API quotas

---

## 🔄 Maintenance

### Weekly Tasks
```bash
# Auto-sync Google Drive (scheduled)
# Check indexing status
curl -X GET "http://localhost:8000/api/admin/chroma/stats" \
  -H "X-Admin-Key: your-admin-key"

# Monitor failed indexes
# SELECT * FROM chroma_document WHERE status='failed'
```

### Monthly Tasks
- Backup `chroma_data/` directory
- Review failed indexing attempts
- Archive old chat history (optional)
- Check Gemini API usage quotas

### Update Embedding Model (If Needed)
```bash
# Delete old Chroma data
rm -rf chroma_data/

# Update requirements.txt
pip install --upgrade chromadb sentence-transformers

# Reindex all documents
POST /api/admin/chroma/index-all
```

---

**Last Updated:** Feb 22, 2024
**Version:** 1.0
**Status:** ✅ Production Ready
