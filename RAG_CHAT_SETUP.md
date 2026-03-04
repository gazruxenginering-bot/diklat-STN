# RAG Chat Feature - Setup Guide

## 📋 Overview

Fitur **Tanya Jawab Teknis (RAG Chat)** telah diimplementasikan untuk memungkinkan pengguna mekanik membuat pertanyaan tentang kendaraan dan mendapatkan jawaban berdasarkan dokumen dari Google Drive.

### Fitur Utama:
- ✅ Document search dari Google Drive
- ✅ Document processing (PDF, Word, Text)
- ✅ Semantic search untuk relevansi dokumen
- ✅ AI-powered answer generation menggunakan Gemini API
- ✅ Chat history per user
- ✅ Source attribution untuk setiap jawaban
- ✅ Multilingual support (Bahasa Indonesia)

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Packages yang ditambahkan:
- `google-generativeai>=0.3.0` - Gemini API
- `PyPDF2>=3.0.0` - PDF processing
- `python-docx>=0.8.11` - Word document processing
- `numpy>=1.24.0` - Vector operations

### 2. Configure Gemini API

#### ✅ Already Integrated!
Gemini API key sudah terintegrasi di `credentials.json`

**Option 1: Use Existing Key (Recommended)**
- API key sudah ada di `credentials.json` field: `gemini_api_key`
- Sistem otomatis membaca dari sana
- Tidak perlu konfigurasi tambahan ✅

**Option 2: Update dengan API Key Baru (If Needed)**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Create new API key
3. Update `credentials.json`:
```json
{
  "...existing fields...",
  "gemini_api_key": "your-new-api-key-here"
}
```

**Option 3: Use Environment Variable (Fallback)**
Jika perlu override credentials.json:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Priority Order:**
1. API key dari `credentials.json` (tertinggi)
2. Environment variable `GEMINI_API_KEY`
3. Parameter saat initialize (lowest)

---

## 📁 File Structure

```
app/
├── smart_search.py          # Document search & retrieval logic
├── gemini_integration.py    # Gemini API wrapper
├── routes_chat.py           # Chat API endpoints
└── templates/user/
    └── chat.html            # Chat UI template
```

---

## 🚀 API Endpoints

### Chat Endpoints

#### 1. Ask Question (Main Endpoint)
```
POST /api/chat/ask
```

**Request:**
```json
{
    "question": "Bagaimana cara ganti oli?",
    "use_documents": true,
    "search_limit": 5
}
```

**Response:**
```json
{
    "success": true,
    "answer": "Berdasarkan dokumen...",
    "sources": [
        {
            "name": "Service Manual.pdf",
            "link": "https://drive.google.com/...",
            "relevance": 0.85
        }
    ],
    "with_rag": true,
    "model": "gemini-1.5-flash",
    "generated_at": "2024-02-22T10:30:00"
}
```

#### 2. Get Chat History
```
GET /api/chat/history?limit=10
```

**Response:**
```json
{
    "success": true,
    "history": [
        {
            "role": "user",
            "content": "Bagaimana cara ganti oli?",
            "timestamp": "2024-02-22T10:30:00",
            "sources": []
        },
        {
            "role": "assistant",
            "content": "Berdasarkan dokumen...",
            "timestamp": "2024-02-22T10:30:05",
            "sources": [...]
        }
    ],
    "total_messages": 2
}
```

#### 3. Clear Chat History
```
POST /api/chat/history/clear
```

**Response:**
```json
{
    "success": true,
    "message": "Chat history cleared"
}
```

#### 4. Search Documents Only
```
POST /api/chat/search
```

**Request:**
```json
{
    "query": "service manual",
    "limit": 5,
    "chunk_size": 1000
}
```

#### 5. Get Suggested Questions
```
POST /api/chat/suggest-questions
```

**Response:**
```json
{
    "success": true,
    "suggestions": {
        "umum": [
            "Bagaimana cara perawatan berkala kendaraan?",
            "Berapa interval penggantian oli standar?"
        ],
        "teknis": [...]
    }
}
```

#### 6. Chat System Health
```
GET /api/chat/health
```

**Response:**
```json
{
    "status": "ok",
    "gemini_available": true,
    "search_available": true
}
```

---

## 🔐 Security & Authentication

### API Key Management
Gemini API key dikelola dengan prioritas:
1. **credentials.json** (field `gemini_api_key`) ← Primary source
2. **Environment variable** `GEMINI_API_KEY` ← Fallback
3. **Direct parameter** saat inisialisasi ← Lowest priority

### Endpoints Protection
Semua chat endpoints memerlukan user untuk login (session-based).
Decorator `@require_login` diterapkan pada semua routes.

### Input Validation
- Pertanyaan minimal 2 karakter
- Maksimal 1000 karakter
- Sanitasi HTML untuk mencegah XSS
- Rate limiting pada login (existing)

### credentials.json Security
- ✅ Keep `credentials.json` in `.gitignore` (sudah)
- ✅ Berisi private key Google + Gemini API key
- ⚠️ **JANGAN commit ke public repository**
- ✅ Safe untuk production dengan proper access control

### Environment Variable as Backup
Untuk flexibility, tetap support env variable:
```bash
# Jika diperlukan override credentials.json
export GEMINI_API_KEY="backup-key-here"
```

---

## 📊 How It Works (Flow Diagram)

```
User Question
     ↓
Session Check (Authentication)
     ↓
Search Google Drive for Relevant Documents
     ↓
Process & Chunk Documents (500-1000 tokens each)
     ↓
Calculate Semantic Similarity to Question
     ↓
Get Top 3 Most Relevant Chunks per Document
     ↓
Send Context + Question to Gemini API
     ↓
Generate Answer in Bahasa Indonesia
     ↓
Add Answer to Chat History
     ↓
Return Answer + Source Attribution
     ↓
Display in UI with Links to Source Documents
```

---

## 🎯 Usage Examples

### Example 1: Search & Get Answer
```javascript
const response = await fetch('/api/chat/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        question: "Bagaimana cara setting katup?",
        use_documents: true,
        search_limit: 5
    })
});
const data = await response.json();
console.log(data.answer);
// Output: "Berdasarkan Service Manual, langkah-langkah setting katup adalah..."
```

### Example 2: Access Chat Page
```
Browser: http://localhost:8000/api/chat/page
```

---

## ⚙️ Configuration Options

### In gemini_integration.py
```python
class GeminiChatManager:
    def __init__(self, api_key: str = None):
        self.model_name = "gemini-1.5-flash"  # Change model here
        # Options: "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"
```

### Temperature Setting
```python
generation_config=genai.types.GenerationConfig(
    temperature=0.7,  # 0.0 = deterministic, 1.0 = creative
    max_output_tokens=2048  # Max response length
)
```

### Search Limit
```python
# In routes_chat.py - ask_question()
search_results = search_engine.search_and_retrieve(
    question,
    search_limit=5,  # Documents to search
    chunk_size=1000,  # Characters per chunk
    top_chunks=3  # Chunks to return per document
)
```

---

## 🐛 Troubleshooting

### Error: "Gemini API tidak diinisialisasi"
**Solution:** 
- Check if `GEMINI_API_KEY` environment variable is set
- Verify API key is valid (test at [Google AI Studio](https://aistudio.google.com/))
- Restart Flask application

```bash
# Check environment variable
echo $GEMINI_API_KEY

# If empty, set it
export GEMINI_API_KEY="your-key-here"
```

### Error: "Search engine tidak tersedia"
**Solution:**
- Verify `credentials.json` exists in project root
- Check Google Drive API is enabled in Google Cloud Console
- Restart application

### Error: "Authentication required"
**Solution:**
- User must login first at `/login`
- Session timeout is 2 hours (configurable in `app/__init__.py`)
- Clear cookies if session persists after logout

### Slow Response Time
**Solution:**
- Reduce `search_limit` (default: 5)
- Reduce `top_chunks` (default: 3)
- Document cache is automatic - subsequent searches are faster
- Use `clear_cache()` only when needed

### Empty Answers / "Informasi tidak ditemukan"
**Solution:**
- Check documents in Google Drive folder are accessible
- Verify document format (PDF, DOCX, TXT supported)
- Try more specific search queries
- Check document content is actual text (not scanned images without OCR)

---

## 📈 Performance & Optimization

### Document Caching
Documents didownload 1x dan di-cache untuk queries berikutnya:
```python
# In smart_search.py
if file_id not in self.document_cache:
    content = self.drive_manager.get_file_content(file_id)
    self.document_cache[file_id] = content
```

Clear cache manually:
```python
search_engine.clear_cache()
```

### API Rate Limits
- Gemini API: Check quotas at [Google AI Studio](https://aistudio.google.com/app/apikeys)
- Google Drive API: 1000 requests/100 seconds per user
- Flask rate limiter: 5 login attempts/hour per IP (existing)

---

## 🎓 Best Practices

### 1. Question Quality
**Good Questions:**
- "Berapa interval penggantian oli untuk Honda Civic 2020?"
- "Bagaimana cara diagnosa trouble code P0300?"
- "Apa langkah-langkah setting timing engine Suzuki?"

**Poor Questions:**
- "Ini gimana?" (terlalu vague)
- "Mobil saya rusak" (tidak spesifik)

### 2. Document Management
- Organize documents logically in Google Drive
- Use clear filenames (e.g., "Honda_Service_Manual_2020.pdf")
- Ensure documents are in searchable format (not scanned images)

### 3. Admin Management
Monitor chat usage:
- Check logs at `app/routes_chat.py` - calls to `/api/chat/ask`
- Monitor Google Drive API quotas
- Archive old chat history periodically if needed

---

## 🔄 Update & Maintenance

### Update Gemini Model
```python
# In gemini_integration.py
self.model_name = "gemini-1.5-pro"  # New model when available
```

### Add New Question Suggestions
```python
# In routes_chat.py - suggest_questions()
'teknis': [
    'New suggestion 1',
    'New suggestion 2'
]
```

### Modify System Prompt
```python
# In gemini_integration.py - _build_system_prompt()
return """Your custom system prompt here..."""
```

---

## 📞 Support & Resources

- **Gemini API Docs:** https://ai.google.dev/docs/
- **Google Drive API:** https://developers.google.com/drive/api
- **Flask Documentation:** https://flask.palletsprojects.com/
- **PyPDF2:** https://pypdf.readthedocs.io/

---

## 🚢 Deployment Checklist

- [ ] GEMINI_API_KEY set in production environment
- [ ] credentials.json exists and accessible
- [ ] Google Drive API enabled in Cloud Console
- [ ] Flask SECRET_KEY configured
- [ ] Database migrations applied
- [ ] Error logging configured
- [ ] CORS headers set appropriately
- [ ] Rate limiting enabled
- [ ] Chat routes registered in __init__.py
- [ ] Dependencies installed (`pip install -r requirements.txt`)

---

**Last Updated:** February 22, 2024
**Version:** 1.0
**Status:** ✅ Production Ready
