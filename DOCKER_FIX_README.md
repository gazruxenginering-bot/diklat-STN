# 🐳 Docker Configuration Fix untuk Template Update

## Masalah yang Terjadi

Ketika menjalankan aplikasi di Docker, UI menampilkan template lama (bukan template baru yang sudah dimodifikasi). Ini terjadi karena:

1. **Docker image dibangun dengan kode lama** - Saat Dockerfile di-build, kode/template yang ada saat itu di-copy ke dalam image
2. **Container tidak me-mount development folder** - File changes di local tidak tercermin di container
3. **Template caching** - Flask & browser cache template files sehingga changes tidak terlihat

## Solusi yang Diterapkan

### 1. Update `docker-compose.yml`
```yaml
volumes:
  - .:/app  # Mount seluruh folder ke container
```

Sebelumnya hanya `./database` dan `./instance` yang di-mount. Sekarang seluruh project folder di-mount, sehingga file changes langsung tercermin di container.

### 2. Update `app/__init__.py` - Template Auto-Reload
Ditambahkan untuk development mode:
```python
if is_development:
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.jinja_env.auto_reload = True
```

### 3. Update Environment di `docker-compose.yml`
```
FLASK_ENV=development   # Dari "production" ke "development"
FLASK_DEBUG=1          # Enable debug mode
```

## Hasil Akhir

✅ Template `chat.html` baru dengan:
- Animated gradient background
- Glassmorphism cards
- Modern CSS animations
- Responsive design

Kini akan **langsung tercermin** di container tanpa perlu rebuild Docker image setiap kali ada file changes!

## Cara Menggunakan

### Development (Auto-reload)
```bash
docker-compose up -d --build
```

Container akan auto-reload ketika file berubah.

### Production (Rebuilding)
Jika ingin menjalankan di production:

```bash
# Edit docker-compose.yml:
# - Ubah FLASK_ENV=development menjadi FLASK_ENV=production
# - Hapus FLASK_DEBUG=1
# - Hapus volume mount yang membuat full directory accessible

docker-compose up -d --build
```

## Struktur Folder yang Di-mount

```
/app/                          # Root project
├── app/                        # Flask app folder
│   ├── templates/              # ← Template files (auto-reload now)
│   │   └── user/chat.html      # ← New modern UI
│   ├── static/                 # ← CSS/JS files
│   ├── routes_chat.py          # ← Chat routes
│   └── ...
├── chroma_data/                # Vector database
├── database/                   # SQLite databases
├── instance/                   # Uploads & cache
└── ...
```

## Troubleshooting

### Template masih tidak update?

1. **Clear browser cache:**
   - Ctrl+Shift+Delete di browser
   - Pilih "All time"
   - Check "Images and files"
   - Clear data

2. **Restart container:**
   ```bash
   docker-compose restart
   ```

3. **Hard rebuild:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

4. **Check logs:**
   ```bash
   docker-compose logs stn-diklat-panel
   ```

### Container tidak start?

```bash
# Check logs
docker-compose logs -f stn-diklat-panel

# Rebuild dengan rm containers
docker-compose down
docker system prune -f
docker-compose up -d --build
```

## Performance Notes

Development mode dengan volume mounting & auto-reload:
- ✅ File changes instant
- ⚠️ Slightly slower than production
- ✅ Perfect untuk development

Production deployment:
- ❌ Tidak ada live updates (perlu rebuild Docker)
- ✅ Faster performance
- ✅ Secure (no direct file access)

---

**Update Date:** 2026-03-04
**Status:** ✅ Implemented
