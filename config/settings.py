import os
from pathlib import Path
from dotenv import load_dotenv

# ==============================================
# BASE DIRECTORY SETUP
# ==============================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==============================================
# SECURITY CONFIGURATION
# ==============================================
# Production settings hardcoded
SECRET_KEY = "django-insecure-#your-production-secret-key-here-replace-with-secure-random-key"

# Set to True for local development, False for production
DEBUG = True

# Production environment flag (cPanel/Hahu hosting)
# Set to True for production, False for local development
IS_HAHU = False

ALLOWED_HOSTS = [
    "studio.corelink.et",
    "www.studio.corelink.et",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://studio.corelink.et",
    "https://www.studio.corelink.et",
]

# Trust Cloudflare forwarded headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==============================================
# APPLICATION DEFINITIONS
# ==============================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "whitenoise",
    "core",
    "studio",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "studio" / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

# ==============================================
# SITE ID FOR SITEMAPS
# ==============================================
SITE_ID = 1

# ==============================================
# DATABASE CONFIGURATION
# ==============================================
# Using the same database as main project
# Admin can hardcode values here directly, or use environment variables
# ==============================================
# 4. DATABASE CONFIGURATION (POSTGRESQL)
# ==============================================
if IS_HAHU:
    # PRODUCTION: Using the PostgreSQL database created in cPanel
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'corelink_studio_db',
            'USER': 'corelink_studioadmin',
            'PASSWORD': 'studioadmin7744$$@@*',
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }
else:
    # LOCAL: Using SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==============================================
# AUTHENTICATION
# ==============================================
AUTH_PASSWORD_VALIDATORS = []
# Using default Django User model for studio
# AUTH_USER_MODEL = "accounts.CustomUser"

# ==============================================
# INTERNATIONALIZATION
# ==============================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ==============================================
# STATIC AND MEDIA FILES
# ==============================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
# Media path - local for development, production for deployment
if DEBUG:
    MEDIA_ROOT = BASE_DIR / "media"
else:
    MEDIA_ROOT = "/home/corelink/corelink_studio-/media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# ==============================================
# SECURITY SETTINGS
# ==============================================
SECURE_SSL_REDIRECT = True if not DEBUG else False
SESSION_COOKIE_SECURE = True if not DEBUG else False
CSRF_COOKIE_SECURE = True if not DEBUG else False

# ==============================================
# DEFAULT AUTO FIELD
# ==============================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
