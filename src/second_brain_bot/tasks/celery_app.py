from celery import Celery

from second_brain_bot.config import settings

celery_app = Celery(
    "second_brain_bot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["second_brain_bot.tasks.research"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
