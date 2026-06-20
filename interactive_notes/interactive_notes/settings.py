import os
from pathlib import Path

import dj_database_url
from decouple import config, UndefinedValueError
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY: Secret Key ---
try:
    SECRET_KEY = config('DJANGO_SECRET_KEY')
except UndefinedValueError:
    raise ImproperlyConfigured(
        "Отсутствует обязательная переменная окружения DJANGO_SECRET_KEY."
    )

# --- SECURITY: Debug & Hosts ---
DEBUG = config('DJANGO_DEBUG', default='False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split()
if not ALLOWED_HOSTS:
    if DEBUG:
        ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1']
    else:
        raise ImproperlyConfigured("В продакшене необходимо задать ALLOWED_HOSTS")

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173').split()
CSRF_TRUSTED_ORIGINS = [
                           'https://*.onrender.com',
                           'http://localhost:5173',
                       ] + CORS_ALLOWED_ORIGINS

# --- Application Definition ---
INSTALLED_APPS = [
    # Standard
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',

    # Local
    'users.apps.UsersConfig',
    'notes.apps.NotesConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'interactive_notes.urls'

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

WSGI_APPLICATION = 'interactive_notes.wsgi.application'

# --- Database ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASE_URL = os.environ.get('DATABASE_URL')
SSL_REQUIRE = os.environ.get('DJANGO_SSL_REQUIRE', '0') == '1'

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=SSL_REQUIRE,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- REST Framework & JWT ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- Static Files ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
