from flask import Flask
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Environment detection
    is_codespaces = 'GITHUB_CODESPACES_PORT' in os.environ
    is_production = os.getenv('FLASK_ENV') == 'production' and not is_codespaces
    is_development = not is_production

    print(f"Environment: {'Development' if is_development else 'Codespaces' if is_codespaces else 'Production'}")

    # SECRET_KEY configuration - Using a static key for development to ensure session stability.
    secret_key = os.getenv('SECRET_KEY', 'a-stable-development-secret-key')
    if 'dev-secret' in secret_key and is_production:
        raise ValueError("Cannot use development secret key in production!")
    
    app.config['SECRET_KEY'] = secret_key

    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 2 hours
    app.config['SESSION_COOKIE_SECURE'] = is_production  # Secure cookie only in production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Database configuration
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Upload configuration
    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'instance', 'uploads')
    upload_folder = os.path.abspath(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB

    # API Keys Configuration (for offline/API access without CSRF)
    api_keys = os.getenv('API_KEYS', 'offline-dev-key-123').split(',')
    app.config['VALID_API_KEYS'] = [key.strip() for key in api_keys]
    app.config['IP_WHITELIST'] = [ip.strip() for ip in os.getenv('IP_WHITELIST', '127.0.0.1,localhost').split(',')]

    # CSRF Protection - can be disabled with WTF_CSRF_ENABLED=False
    csrf_enabled = os.getenv('WTF_CSRF_ENABLED', 'True').lower() != 'false'
    app.config['WTF_CSRF_ENABLED'] = csrf_enabled
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF tokens tidak kadaluarsa
    
    if csrf_enabled:
        print("✅ CSRF Protection: ENABLED")
    else:
        print("⚠️  CSRF Protection: DISABLED (Development/Testing only)")

    csrf = CSRFProtect(app)

    # Rate limiting
    from .security import init_limiter
    init_limiter(app)

    # Database initialization
    from .models import db
    db.init_app(app)

    with app.app_context():
        # Ensure upload folder exists
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create upload folder: {e}")

        db.create_all()

    # CSP Configuration based on environment
    @app.after_request
    def add_security_headers(response):
        # Use a unified CSP that allows 'unsafe-eval' for development compatibility.
        csp = "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; frame-src https://docs.google.com https://drive.google.com; connect-src 'self' https:;"
        response.headers['Content-Security-Policy'] = csp

        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        return response

    from .routes import main
    app.register_blueprint(main)

    # Error handler untuk CSRF errors
    @app.errorhandler(400)
    def handle_csrf_error(e):
        # Cek apakah error dari CSRF
        if 'CSRF' in str(e):
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error CSRF</title></head>
            <body style="font-family:Arial; padding:20px;">
                <h2>❌ CSRF Token Error</h2>
                <p>Kemungkinan:</p>
                <ul>
                    <li>Session sudah kadaluarsa, coba reload halaman</li>
                    <li>Cookies tidak aktif di browser Anda</li>
                    <li>Buka di private/incognito window</li>
                </ul>
                <a href="/admin">← Kembali ke Login</a>
            </body>
            </html>
            """, 400
        return str(e), 400

    # Setup scheduler untuk auto-sync Google Drive
    try:
        from .drive_sync import setup_scheduler
        scheduler = setup_scheduler()
        scheduler.start()
        print("✅ Google Drive Auto-Sync: SCHEDULED (setiap Minggu pukul 02:00)")
    except Exception as e:
        print(f"⚠️  Could not setup scheduler: {e}")

    return app