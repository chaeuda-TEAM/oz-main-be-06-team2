import os

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
    "ws://api.chaeuda.shop",
]

CSRF_TRUSTED_ORIGINS = [
    "https://chaeuda.shop",
    "https://www.chaeuda.shop",
    "https://api.chaeuda.shop",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]

# ==============================================================================
# Redis (Cluster Mode) 설정
# ==============================================================================
REDIS_HOST = os.getenv("AWS_ELASTICACHE_ENDPOINT")
REDIS_PORT = 6379

# CACHES 설정 - 클러스터 모드 ON (샤드 1개라도 DefaultClusterClient 사용)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # LOCATION은 "redis-cluster" 또는 "rediscluster://..." 식 임의 문자열로 두면 됩니다.
        # (실제 연결은 STARTUP_NODES 통해 이루어집니다.)
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClusterClient",
            # HerdClient를 사용하셨다면, cluster와 호환성 문제가 생길 수 있습니다.
            # 캐시 스탬피드 방지를 위해 HerdClient를 쓰려면, 별도의 지원 여부를 확인해야 합니다.
            # 여기서는 cluster 대응이 잘 되는 DefaultClusterClient를 우선 사용 예시로 제시합니다.
            # 실제 노드(또는 Configuration Endpoint) 정보
            "STARTUP_NODES": [
                {
                    "host": REDIS_HOST,
                    "port": str(REDIS_PORT),
                }
            ],
            # 커넥션 관련 옵션
            "RETRY_ON_TIMEOUT": True,
            "MAX_CONNECTIONS": 100,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
                "socket_keepalive": True,
            },
        },
        # 캐시 키 prefix
        "KEY_PREFIX": "prod",
    }
}

# 세션을 캐시에 저장
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600  # 2주
CACHE_TTL = 60 * 5  # 5분

# ==============================================================================
# Channels 설정 (Redis Cluster 사용 시 주의)
# ==============================================================================
# Channels용 redis 라이브러리는 클러스터 모드를 공식 지원하지 않습니다.
# 그러나 샤드가 1개라면 'hosts'에 클러스터 Endpoint를 넣어 일단 동작시키는 방법이 있습니다.
# (실제로는 Redis가 "MOVED"나 "ASK"를 돌려줄 일은 샤드 1개라서 거의 없지만,
#  내부적으로 PubSub 키 분산이 있을 수 있어 완벽 호환은 장담 어렵습니다.)
# 안전하게 사용하시려면 단일 노드 모드나 다른 브로커를 고려하는 것이 좋습니다.

ASGI_APPLICATION = "a_core.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            # 여기서는 단순히 single endpoint를 지정합니다.
            # channels_redis는 'redis://' 스킴을 사용 가능하지만,
            #   클러스터 모드를 완전 인식하진 않습니다.
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

# ==============================================================================
# 보안 설정
# ==============================================================================
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

# ==============================================================================
# Database 설정
# ==============================================================================
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

# 비동기 DB 연결을 위한 별도 설정 (예: psycopg[async])
ASYNC_DB_CONFIG = {
    "user": os.getenv("AWS_RDS_USER"),
    "password": os.getenv("AWS_RDS_PASSWORD"),
    "database": os.getenv("AWS_RDS_NAME"),
    "host": os.getenv("AWS_RDS_HOST"),
    "port": os.getenv("AWS_RDS_PORT"),
}

# ==============================================================================
# AWS S3 & 정적/미디어 파일 설정
# ==============================================================================
AWS_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_S3_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_CLOUDFRONT_DOMAIN", "")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_DIRS = []

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIAFILES_LOCATION = "media"
AWS_LOCATION = MEDIAFILES_LOCATION
AWS_QUERYSTRING_AUTH = False

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

# ==============================================================================
# 로깅 설정
# ==============================================================================
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
