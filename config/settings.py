"""
Django settings for minimal transcription starter.

No database, no migrations, no Django admin - just API endpoints.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'daphne',  # Must be first for Channels
    'django.contrib.staticfiles',
    'corsheaders',
    'starter',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    # CORS must be before CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# No database needed for API proxy
DATABASES = {}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/assets/'
STATIC_ROOT = BASE_DIR / 'frontend' / 'dist' / 'assets'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'dist']

# Media files
MEDIA_URL = '/media/'

# CORS settings - allow all origins for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ['*']
CORS_ALLOW_METHODS = ['*']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
