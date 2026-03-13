import redis as _redis
from app.core.config import settings

_pool = _redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
    max_connections=20,
)

redis_client = _redis.Redis(connection_pool=_pool)


def get_redis() -> _redis.Redis:
    return redis_client
