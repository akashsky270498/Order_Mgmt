"""
Test settings for Django - overrides default settings for pytest
"""
from .settings import *
import tempfile
import os

# Remove problematic apps for testing
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ['daphne', 'channels']]

# Override CHANNEL_LAYERS to use in-memory backend for testing
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Use SQLite for faster testing with a temporary file
TEMP_DB_DIR = tempfile.gettempdir()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEMP_DB_DIR, 'test_db.sqlite3'),
    }
}

# Disable Celery for tests - use eager mode
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Simplify middleware for tests
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Disable logging during tests to reduce noise
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
        },
    },
}

# Set SWAGGER_SETTINGS to avoid deprecation warning
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "Type 'Bearer ' followed by your JWT token"
        }
    },
    'USE_SESSION_AUTH': False,
    'SWAGGER_USE_COMPACT_RENDERERS': True,
}



