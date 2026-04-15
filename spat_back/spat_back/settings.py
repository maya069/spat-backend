from pathlib import Path
from datetime import timedelta
from decouple import config
from corsheaders.defaults import default_headers
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# SÉCURITÉ
# ─────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='change-moi-en-production')
DEBUG = config('DEBUG', default=False, cast=bool)  # ✅ Correction : False par défaut en production

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'spat-app.vercel.app',
]

# ─────────────────────────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Packages
    'rest_framework',
    'rest_framework_simplejwt',  # ✅ Correction : ajout de simplejwt

    # Apps
    'accounts',
    'logements',
    'logi',
    'employes',
]

# ─────────────────────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # TOUJOURS en premier
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://spat-app.vercel.app",
]

# ✅ Correction : suppression de CORS_ALLOW_ALL_ORIGINS = True
# Cela rendait CORS_ALLOWED_ORIGINS inutile et ouvrait l'API à tous les domaines

CORS_ALLOW_HEADERS = list(default_headers) + [
    'Authorization',
]

CORS_ALLOW_CREDENTIALS = True  # ✅ Ajout : nécessaire pour les cookies/tokens

# ─────────────────────────────────────────────────────────────
# DRF + JWT
# ─────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ─────────────────────────────────────────────────────────────
# URLS / WSGI
# ─────────────────────────────────────────────────────────────
ROOT_URLCONF = 'spat_back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'spat_back.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL and DATABASE_URL.startswith('postgres'):
    # En production (Render) : utiliser PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # En local : utiliser SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }



AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────────────────────
# INTERNATIONALISATION
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Indian/Antananarivo'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────
# STATIC FILES (Render + WhiteNoise)
# ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ✅ Correction : utilisation de STORAGES au lieu de STATICFILES_STORAGE (déprécié Django 5.x)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ─────────────────────────────────────────────────────────────
# MEDIA FILES (avatars, uploads)
# ─────────────────────────────────────────────────────────────
# ✅ Correction : ajout de MEDIA_URL et MEDIA_ROOT (manquants, causait un crash)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────────────────────────────────────
# DIVERS
# ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'