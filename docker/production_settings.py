# Production settings for Docker deployment
import os
import socket
from smart_mcq.settings import *

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'docker-default-key-change-in-production-12345')

# Hosts configuration - Your domain + Open access for any IP
def get_allowed_hosts():
    hosts = [
        # Production domain (hardcoded)
        'smartmcq.meikuraledutech.in',
        
        # Local development and testing
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        
        # Allow ANY IP address - flexible for all network scenarios
        '*',
    ]
    return hosts

ALLOWED_HOSTS = get_allowed_hosts()

# CSRF trusted origins - More permissive for flexibility
def get_csrf_trusted_origins():
    origins = [
        # Production domain
        'https://smartmcq.meikuraledutech.in',
        'http://smartmcq.meikuraledutech.in',
        
        # Local development
        'http://localhost:8080',
        'http://127.0.0.1:8080',
        'http://localhost',
        'http://127.0.0.1',
    ]
    
    return origins

CSRF_TRUSTED_ORIGINS = get_csrf_trusted_origins()

# Disable CSRF for maximum flexibility in local/testing scenarios
# Production will be secured via domain restrictions
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = False

# Additional CSRF settings for flexibility
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Database configuration for Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'smart_mcq_db'),
        'USER': os.environ.get('DB_USER', 'mcq_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'mcq_secure_password_2024'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 300,
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cloudflare SSL settings
USE_TLS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

# Session settings - Enable for HTTPS via Cloudflare
SESSION_COOKIE_SECURE = True   # HTTPS required
CSRF_COOKIE_SECURE = True      # HTTPS required
SESSION_COOKIE_AGE = 3600      # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache (optional - can be enabled with Redis later)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'smart-mcq-cache',
    }
}

# Time zone
USE_TZ = True
TIME_ZONE = 'Asia/Kolkata'

# Email configuration (for future use)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Console for now

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB