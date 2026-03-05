from urllib.parse import urlparse

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings


def _parse_redis_url(url: str) -> dict:
    parsed = urlparse(url)
    return {
        "host": parsed.hostname,
        "port": parsed.port,
        "db": int(parsed.path.lstrip("/")) if parsed.path else None,
        "password": parsed.password,
    }


if settings.redis_url:
    _jobstores = {
        "default": RedisJobStore(
            **_parse_redis_url(settings.redis_url.get_secret_value()),
        )
    }
else:
    _jobstores = {"default": MemoryJobStore()}

_executors = {"default": AsyncIOExecutor()}

_job_defaults = {"misfire_grac"}

scheduler = AsyncIOScheduler(
    jobstores=_jobstores,
    executors=_executors,
)
