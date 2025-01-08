import logging

import asyncpg

from django.conf import settings

logger = logging.getLogger(__name__)

db_pool = None


async def init_db():
    global db_pool
    try:
        if db_pool is None:
            db_pool = await asyncpg.create_pool(
                **settings.ASYNC_DB_CONFIG,
                min_size=5,
                max_size=20,
                timeout=30,
                command_timeout=60,
            )
            logger.info("Database connection pool initialized successfully")
    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


async def close_db():
    global db_pool
    try:
        if db_pool:
            await db_pool.close()
            db_pool = None
            logger.info("Database connection pool closed successfully")
    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"Error closing database pool: {e}")
        raise


async def execute_query(query: str, *args):
    try:
        async with db_pool.acquire() as conn:
            return await conn.fetch(query, *args)
    except (
        asyncpg.exceptions.ConnectionDoesNotExistError,
        asyncpg.exceptions.ConnectionFailureError,
    ) as e:
        logger.error(f"Database connection error: {e}")
        raise
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise
