# 🚨 Security Incident Response Guide

## Incident Summary
API keys and credentials were exposed in the public GitHub repository:
- Gemini API key found in `QUICK_START_CHROMA_CLOUD.md`
- Chroma API key found in `QUICK_START_CHROMA_CLOUD.md`
- Google Drive folder IDs exposed

**Timeline:**
- ❌ Keys committed and pushed to GitHub (public)
- ⚠️ Google detected and sent warning
- ✅ Keys removed from documentation
- ⏳ PENDING: Revoke old keys and generate new ones

---

## 🔥 IMMEDIATE ACTIONS REQUIRED

### Step 1: Revoke Exposed API Keys

#### Google Gemini API
1. Go to: https://aistudio.google.com/app/apikey
2. Find the exposed key: `AIzaSyBnOam5Cak2qYnV3tZ5b67q_yIJdQUcxeY`
3. Click **"Delete"** or **"Revoke"** button
4. Confirm deletion

**Related Links:**
- Gemini API Console: https://aistudio.google.com/app/apikey
- Google AI Overview: https://ai.google.dev/

#### Chroma API Key
1. Go to: https://www.trychroma.com/
2. Sign in to dashboard
3. Find the exposed key: `ck-4XMkqE5Wi5DfzQEkcso6N8RSf1PtewXD5wU4UBXTn81n`
4. Delete or revoke it
5. Confirm deletion

**Warning:** Any attacker with this key can:
- Access your Chroma database
- Query your vector store
- Delete or modify documents
- Incur costs on your account

---

### Step 2: Generate NEW API Keys

#### Create New Gemini API Key
1. Go to: https://aistudio.google.com/app/apikey
2. Click **"Create API key"**
3. Select project (create new if needed)
4. Copy the new key
5. Keep it securely in `.env` file ONLY

#### Create New Chroma API Key
1. Go to: https://www.trychroma.com/
2. Sign in to dashboard
3. Select your database: `DIKLAT-STN`
4. Click **"Generate API Key"** or **"Settings"**
5. Create new key
6. Copy and save to `.env`

---

### Step 3: Update `.env` File Locally

1. **Edit `.env` file:**
```bash
cd /workspaces/diklat-STN
nano .env  # or use your editor
```

2. **Update with NEW keys:**
```bash
GEMINI_API_KEY=<YOUR_NEW_GEMINI_API_KEY>
CHROMA_API_KEY=<YOUR_NEW_CHROMA_API_KEY>
CHROMA_TENANT=<YOUR_TENANT_ID>
```

3. **Restart application:**
```bash
docker-compose restart
# or
python run.py
```

4. **Verify connection:**
```bash
curl http://localhost:8000/api/chat/health
# Should return: {"status": "ok", "gemini_available": true, "search_available": true}
```

---

### Step 4: Remove Old Keys from Git History

⚠️ **IMPORTANT:** Even though file is updated, old commits still contain exposed keys!

#### Option A: Using git-filter-repo (Recommended)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove the file from all history
cd /workspaces/diklat-STN
git filter-repo --invert-paths --path QUICK_START_CHROMA_CLOUD.md

# Force push (this rewrites history)
git push origin --force --all
```

#### Option B: Using BFG Repo-Cleaner

```bash
# Download and use BFG (larger files)
# See: https://rtyley.github.io/bfg-repo-cleaner/

# Remove file from history
bfg --delete-files QUICK_START_CHROMA_CLOUD.md

# Force push
git push origin --force --all
```

#### Option C: Manual History Rewrite

```bash
# Remove last 2 commits that had credentials
git reset --hard HEAD~2

# Force push
git push origin main --force  
```

---

## ✅ Verification Checklist

After completing steps above:

- [ ] Old Gemini API key revoked
- [ ] Old Chroma API key revoked
- [ ] New Gemini API key generated and stored in `.env`
- [ ] New Chroma API key generated and stored in `.env`
- [ ] Application restarted with new keys
- [ ] Health check passing: `curl http://localhost:8000/api/chat/health`
- [ ] Old commits removed from git history (force pushed)
- [ ] `.env` in `.gitignore` (check: `cat .gitignore | grep "\.env"`)

---

## 🛡️ Prevention for Future

### 1. Update .gitignore (Already Done)
```bash
# Verify .env is ignored
cat .gitignore | grep -A5 "^\.env"
```

Should show:
```
.env
.env.local
.env.production
credentials.json
```

### 2. Use `.env.example` for Documentation
```bash
# This file shows structure WITHOUT secrets
cat .env.example
```

### 3. Pre-commit Hook to Prevent Credential Leaks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Prevent committing files with credentials

if git diff --cached | grep -i "api.key\|api_key\|secret\|password"; then
    echo "❌ ERROR: Detected potential credentials in commit!"
    echo "Make sure to use .env files for secrets, not git!"
    exit 1
fi

git diff --cached --name-only | grep "\\.env" && {
    echo "❌ ERROR: Trying to commit .env file!"
    exit 1
}
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 4. Use Environment Variables in Production
- Never hardcode credentials
- Use CI/CD secrets (GitHub Actions, GitLab CI, etc.)
- Use infrastructure secrets management (AWS Secrets Manager, etc.)

---

## 📋 Documentation

Exposed credentials were in:
- `QUICK_START_CHROMA_CLOUD.md` ❌ **CLEANED**

Now using safe pattern:
- `.env` file (LOCAL, not in git) ✅
- `.env.example` (SAFE template in git) ✅
- `.gitignore` (prevents commits) ✅

---

## 🔗 References

- [Google Gemini API Security](https://ai.google.dev/security)
- [Managing API Keys Securely](https://cloud.google.com/docs/authentication)
- [Chroma Cloud Documentation](https://docs.trychroma.com/)
- [Git-filter-repo](https://github.com/newren/git-filter-repo)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## 📞 If You Need Help

1. **GitHub Security Portal**: https://github.com/settings/security
2. **View exposed credentials alerts**: https://github.com/gazruxenginering-bot/diklat-STN/security
3. **Revoke tokens**: Go to each API provider's dashboard

---

**Status:** 🔴 ACTIVE INCIDENT  
**Last Updated:** 2026-03-04  
**Required Action:** Revoke old keys and generate new ones IMMEDIATELY
