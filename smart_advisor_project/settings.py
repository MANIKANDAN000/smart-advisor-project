import os
from pathlib import Path
import logging.config

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv is not installed. Environment variables may not be loaded from .env file.")
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / '.env'

if load_dotenv and DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)
elif load_dotenv:
    print(f"Warning: .env file not found at {DOTENV_PATH}. Using environment variables if set, or defaults.")
else:
    print("Warning: load_dotenv function not available. Ensure python-dotenv is installed.")

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("CRITICAL: No SECRET_KEY set. Please set it in your .env file or environment variables.")

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
if not DEBUG:
    # ALLOWED_HOSTS.append('your_production_domain.com')
    pass

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'advisor_app.apps.AdvisorAppConfig', # Using explicit AppConfig
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smart_advisor_project.urls' # Points to your project's main urls.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # For global templates like registration/
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

WSGI_APPLICATION = 'smart_advisor_project.wsgi.application'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'staticfiles']
STATIC_ROOT = BASE_DIR / 'collected_static' # For production

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = 'login'  # The name of your login URL pattern
LOGIN_REDIRECT_URL = 'home' # This tells Django where to redirect after successful login.
                            # It MUST be a valid URL name.
LOGOUT_REDIRECT_URL = 'login' # Where to redirect after logout.

# API Keys
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
EVENTBRITE_API_KEY = os.getenv('EVENTBRITE_API_KEY')

GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Logging Configuration (from previous response, ensure it's suitable)
LOGGING_CONFIG = None
LOGLEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO').upper()
logging.config.dictConfig({
    'version': 1, 'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {asctime} {module}: {message}', 'style': '{'},
    },
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'}},
    'root': {'handlers': ['console'], 'level': LOGLEVEL},
    'loggers': {
        'django': {'handlers': ['console'], 'level': LOGLEVEL, 'propagate': False},
        'django.db.backends': {'handlers': ['console'], 'level': 'DEBUG' if DEBUG else 'INFO', 'propagate': False},
        'advisor_app': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'googleapiclient': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False}
    },
})