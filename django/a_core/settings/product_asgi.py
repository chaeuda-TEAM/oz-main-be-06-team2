from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "chaeuda.shop",
    "www.chaeuda.shop",
    "api.chaeuda.shop",
    "localhost",
    "127.0.0.1",
    "54.180.104.88",  # EC2 IP
]

CORS_ALLOWED_ORIGINS = [
    "https://chaeuda.shop",
    "https://www.chaeuda.shop",
    "https://api.chaeuda.shop",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "ws://api.chaeuda.shop",  # WebSocket 보안 연결 추가
]

CSRF_TRUSTED_ORIGINS = [
    "https://chaeuda.shop",
    "https://www.chaeuda.shop",
    "https://api.chaeuda.shop",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]

# Redis 관련 설정
REDIS_HOST = os.getenv("AWS_ELASTICACHE_ENDPOINT")
REDIS_PORT = 6379

# 캐시 설정
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.HerdClient",
            "RETRY_ON_TIMEOUT": True,
            "MAX_CONNECTIONS": 100,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
                "socket_keepalive": True,
            },
        },
        "KEY_PREFIX": "prod",
    }
}

# 세션 설정
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600  # 2주
CACHE_TTL = 60 * 5  # 5분

# Channels 설정
ASGI_APPLICATION = "a_core.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
            ],
            "capacity": 1500,
            "expiry": 10,
            "prefix": "asgi:",
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}

# 보안 설정
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_DOMAIN = ".chaeuda.shop"
CSRF_COOKIE_DOMAIN = ".chaeuda.shop"
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Database 설정
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("AWS_RDS_NAME"),
        "USER": os.getenv("AWS_RDS_USER"),
        "PASSWORD": os.getenv("AWS_RDS_PASSWORD"),
        "HOST": os.getenv("AWS_RDS_HOST"),
        "PORT": os.getenv("AWS_RDS_PORT"),
    }
}

# 비동기 DB 연결을 위한 별도 설정
ASYNC_DB_CONFIG = {
    "user": os.getenv("AWS_RDS_USER"),
    "password": os.getenv("AWS_RDS_PASSWORD"),
    "database": os.getenv("AWS_RDS_NAME"),
    "host": os.getenv("AWS_RDS_HOST"),
    "port": os.getenv("AWS_RDS_PORT"),
}

# AWS S3 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_S3_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_CLOUDFRONT_DOMAIN", "")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

# 정적 파일 설정
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_DIRS = []

# 미디어 파일 설정
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIAFILES_LOCATION = "media"
AWS_LOCATION = MEDIAFILES_LOCATION
AWS_QUERYSTRING_AUTH = False

# S3 스토리지 설정
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}

# 파일 업로드 제한
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 로깅 설정
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": False,
            "level": "INFO",
        },
    },
}
