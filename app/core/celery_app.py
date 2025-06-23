import os
from celery import Celery
from app.core.config import settings

# имя «coffee_shop_api» — может быть любым
celery_app = Celery(
    "coffee_shop_api",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# эта секция позволяет задавать задачи через строку «module:function»
celery_app.autodiscover_tasks(packages=["app.tasks"])

# периодика: раз в сутки
celery_app.conf.beat_schedule = {
    "cleanup-unverified-users-every-midnight": {
        "task": "app.tasks.worker.delete_unverified_users_task",
        "schedule": 24 * 3600,  # в секундах
    },
}

celery_app.conf.timezone = "UTC"