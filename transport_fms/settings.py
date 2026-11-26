"""
Django settings for transport_fms project.
Transport Fleet & Logistics Management System (FMS)
Chanakya University - School of Engineering - BCA V Sem (DAT501)
Student: Pranavraghavendra M R (Reg No: 24UG00220)
"""

from pathlib import Path
import os
import shutil
import dj_database_url

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-zc&)r@uj2_#8hymikhp@97wn+rlp)+t9k6h-@-gopn@jc#cmd^'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

# Allowed Hosts
ALLOWED_HOSTS = ['*']

# CSRF Trusted Origins for Vercel and Local Development
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
custom_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS')
if custom_csrf:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in custom_csrf.split(',') if origin.strip()])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Custom FMS Apps
    'accounts.apps.AccountsConfig',
    'fleet.apps.FleetConfig',
    'routing.apps.RoutingConfig',
    'maintenance.apps.MaintenanceConfig',
    'safety.apps.SafetyConfig',
    'fuel.apps.FuelConfig',
    'reports.apps.ReportsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'transport_fms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.user_role_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'transport_fms.wsgi.application'

# Database configuration
# Evaluates PostgreSQL via DATABASE_URL if provided; otherwise configures SQLite.
# On Vercel / serverless runtime with read-only root filesystems, SQLite is copied to and served from
# writable /tmp storage to support demo operations without throwing read-only database errors.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    IS_VERCEL = os.environ.get('VERCEL') == '1' or 'AWS_LAMBDA_FUNCTION_NAME' in os.environ or os.environ.get('VERCEL_ENV') is not None
    SOURCE_DB = BASE_DIR / 'db.sqlite3'
    TMP_DB = Path('/tmp') / 'db.sqlite3'

    if IS_VERCEL or (SOURCE_DB.exists() and not os.access(SOURCE_DB, os.W_OK)):
        try:
            Path('/tmp').mkdir(parents=True, exist_ok=True)
            if SOURCE_DB.exists():
                if not TMP_DB.exists() or TMP_DB.stat().st_size == 0:
                    shutil.copy2(SOURCE_DB, TMP_DB)
        except Exception:
            pass
        SQLITE_PATH = TMP_DB
    else:
        SQLITE_PATH = SOURCE_DB

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': SQLITE_PATH,
        }
    }

# Session Management:
# Uses signed-cookie sessions to eliminate database session writes on serverless environments
# and guarantee authenticated sessions persist reliably across all serverless lambda container instances.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24 hours

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage for efficient, compressed static file serving
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security & HTTPS headers for production behind reverse proxies (like Vercel)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
