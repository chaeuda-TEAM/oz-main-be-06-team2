from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
SERVER_BASE_URL = "http://localhost:8000"


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
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

FILE_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024  # 3MB limit
