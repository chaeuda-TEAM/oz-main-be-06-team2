from .base import *

DEBUG = True

SERVER_BASE_URL = "http://localhost:3000"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
    "ws://localhost:8000",
]

# Redis 관련 설정
DEV_REDIS_HOST = os.getenv("DEV_REDIS_HOST")
REDIS_PORT = 6379

# 캐시 설정
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{DEV_REDIS_HOST}:{REDIS_PORT}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_CLASS": "redis.ConnectionPool",
            "MAX_CONNECTIONS": 100,
            "RETRY_ON_TIMEOUT": True,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "dev",
    }
}

# 세션 설정
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
CACHE_TTL = 60 * 5  # 5분

# Channels 설정
ASGI_APPLICATION = "a_core.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(DEV_REDIS_HOST, REDIS_PORT)],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# 데이터베이스 설정
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DEV_AWS_RDS_NAME"),
        "USER": os.getenv("DEV_AWS_RDS_USER"),
        "PASSWORD": os.getenv("DEV_AWS_RDS_PASSWORD"),
        "HOST": os.getenv("DEV_AWS_RDS_HOST"),
        "PORT": os.getenv("DEV_AWS_RDS_PORT"),
    }
}

# 기본 설정
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# SSL 설정 비활성화 (개발 환경)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None
