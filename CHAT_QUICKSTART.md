# Quick Start - RAG Chat Feature

## ⚡ 5-Minute Setup

### 1️⃣ Update Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Gemini API Key
✅ **Sudah terintegrasi di credentials.json!**

Tidak perlu set environment variable. API key:
- ✅ Sudah ada di `credentials.json` dengan key `gemini_api_key`
- ✅ Sistem akan auto-load dari sana
- ✅ Fallback ke `GEMINI_API_KEY` env var jika tidak ada di credentials

### 3️⃣ Start Aplikasi
```bash
honcho start  # atau python run.py
```

Check untuk pesan ini:
```
✅ Gemini API key loaded from credentials.json
✅ Gemini API initialized with model: gemini-1.5-flash
✅ Chat system initialized
✅ Chat routes registered
```

### 4️⃣ Access Chat Feature
1. Login di `http://localhost:8000/login`
2. Dashboard → Click "💬 Tanya Jawab Teknis"
3. Mulai bertanya!

---

## 📝 Example Questions

```
"Bagaimana cara perawatan berkala kendaraan?"
"Berapa interval penggantian oli standar?"
"Apa tanda-tanda clutch yang perlu diganti?"
"Bagaimana cara membaca kode error OBD-II?"
"Cara setting timing valve untuk Honda?"
"Apa gejala alternator yang rusak?"
"Bagaimana diagnosis trouble code P0308?"
```

---

## 🔍 How It Works

1. **User Types Question** → "Bagaimana cara ganti oli?"
2. **System Searches Google Drive** → Finds relevant service manuals
3. **Extract Relevant Content** → Takes key parts about oil changes
4. **Send to Gemini AI** → "Based on these documents, answer the question..."
5. **Get Answer** → "Berdasarkan Service Manual, langkah-langkah ganti oli..."
6. **Show Source** → Links to the documents used

---

## 🐛 Quick Troubleshoot

| Issue | Solution |
|-------|----------|
| "Gemini API tidak diinisialisasi" | Check if GEMINI_API_KEY is set: `echo $GEMINI_API_KEY` |
| "Search engine tidak tersedia" | Verify `credentials.json` exists in root folder |
| Can't access chat | Login first, then go to dashboard |
| Slow responses | Check internet connection, reduce search_limit |
| Empty search results | Documents in Drive might not be text-searchable (try OCR) |

---

## 📂 Files Added/Modified

**New Files:**
- `app/smart_search.py` - Document search logic
- `app/gemini_integration.py` - AI integration
- `app/routes_chat.py` - Chat API endpoints
- `app/templates/user/chat.html` - Chat UI
- `RAG_CHAT_SETUP.md` - Detailed setup guide

**Modified Files:**
- `requirements.txt` - Added dependencies
- `app/__init__.py` - Registered chat routes
- `app/templates/user/dashboard.html` - Added chat button

---

## 📚 Full Documentation

See [RAG_CHAT_SETUP.md](./RAG_CHAT_SETUP.md) for:
- Complete API documentation
- Configuration options
- Performance optimization
- Deployment checklist
- Troubleshooting guide

---

## ✨ Features

✅ Search documents from Google Drive  
✅ Process PDF, Word, Text files  
✅ AI-powered answers in Bahasa Indonesia  
✅ Show source documents with relevance scores  
✅ Save chat history per user  
✅ Quick question suggestions  
✅ Semantic search for better relevance  
✅ Beautiful modern UI  

---

## 🚀 What's Next?

1. ✅ Install & setup (done!)
2. ✅ Configure Gemini API key
3. ✅ Test with some questions
4. 📈 Monitor performance
5. 🎯 Customize suggestions (optional)
6. 🚢 Deploy to production

---

**Ready to go!** 🎉
