from .base import *

DEBUG = True

SERVER_BASE_URL = "http://localhost:3000"


ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
]

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


# SSL 설정 비활성화
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None  # SSL 프록시 헤더 비활성화

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB limit
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB limit


# Elasticache 설정
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'redis://{os.getenv("DEV_AWS_ELASTICACHE_ENDPOINT")}:6379/0',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_CLASS": "redis.ConnectionPool",
            "MAX_CONNECTIONS": 100,
            "RETRY_ON_TIMEOUT": True,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "dev",  # 개발 환경용 프리픽스
    }
}

# 세션 저장소 설정
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# 캐시 기본 만료 시간 설정 (선택사항)
CACHE_TTL = 60 * 5  # 5분

# Channels 설정
INSTALLED_APPS += [
    "channels",
]

ASGI_APPLICATION = "a_core.asgi.application"

# Channel Layers 설정 (Redis 백엔드 사용)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv("DEV_AWS_ELASTICACHE_ENDPOINT"), 6379)],
        },
    },
}
