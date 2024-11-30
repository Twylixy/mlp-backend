from redis import Redis
from app.settings import app_settings

redis_conn = Redis(
    host=app_settings.REDIS_HOST,
    port=app_settings.REDIS_PORT,
    db=app_settings.REDIS_DB,
    password=app_settings.REDIS_PASSWORD,
)
