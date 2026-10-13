import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-production")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# ── Hosts permitidos ──────────────────────────────────────────────────────────
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
ALLOWED_HOSTS += [
    ".railway.app",
    ".pythonanywhere.com",
]
# Railway (si aplica)
RAILWAY_HOST = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
if RAILWAY_HOST and RAILWAY_HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_HOST)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "cloudinary",
    "tickets",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "support_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "support_system.wsgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
# Railway inyecta DATABASE_URL; en PythonAnywhere configúralo manualmente
# si no hay DATABASE_URL, cae a SQLite (funciona en PA gratuito)
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# ── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Solo agregar STATICFILES_DIRS si el directorio existe (evita W004)
_static_dir = BASE_DIR / "static"
if _static_dir.exists():
    STATICFILES_DIRS = [_static_dir]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Cloudinary ────────────────────────────────────────────────────────────────
_cloudinary_url = os.environ.get("CLOUDINARY_URL", "").strip()
if _cloudinary_url:
    import cloudinary
    cloudinary.config(cloudinary_url=_cloudinary_url)
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    CLOUDINARY_STORAGE = {
        "MEDIA_TAG": "support_tickets",
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Email ─────────────────────────────────────────────────────────────────────
# Emails via Resend API (HTTPS, no SMTP — funciona en Railway y PythonAnywhere)
RESEND_API_KEY             = os.environ.get("RESEND_API_KEY", "")
DEFAULT_FROM_EMAIL         = os.environ.get("DEFAULT_FROM_EMAIL", "soporte@perseustechnology.dev")
ADMIN_NOTIFICATION_EMAIL   = os.environ.get("ADMIN_NOTIFICATION_EMAIL", DEFAULT_FROM_EMAIL)
# El backend de Django no se usa realmente (el modelo llama Resend directo),
# pero console evita errores si RESEND_API_KEY no está configurada
EMAIL_BACKEND              = "django.core.mail.backends.console.EmailBackend"

SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")

# ── Auth ──────────────────────────────────────────────────────────────────────
LOGIN_URL           = "/accounts/login/"
LOGIN_REDIRECT_URL  = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ── CSRF y Security ───────────────────────────────────────────────────────────
# Siempre activo — cubre Railway, PythonAnywhere y dominios custom
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
    "https://support-tickets-production-61ff.up.railway.app",
    "https://*.pythonanywhere.com",
]
# Dominios adicionales via variable de entorno (ej: dominio propio)
extra_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if extra_csrf:
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in extra_csrf.split(",") if o.strip()]

# PythonAnywhere y Railway usan proxy HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "tickets": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
