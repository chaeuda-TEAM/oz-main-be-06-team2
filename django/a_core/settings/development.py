from .base import *

DEBUG = True

INSTALLED_APPS += [
    "django_extensions",
]

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "api.chaeuda.shop"]
SERVER_BASE_URL = "http://localhost:3000"


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://api.chaeuda.shop",
    "https://chaeuda.shop",
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB limit
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB limit
# Shell Plus 설정
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_IMPORTS = [
    "from datetime import datetime, timedelta",
    "from django.conf import settings",
    "from django.core.cache import cache",
]
