from celery.utils.log import get_task_logger
from app.core.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.services.user import delete_unverified_users
from app.services.email import send_verification_email

logger = get_task_logger(__name__)

@celery_app.task(name="app.tasks.worker.delete_unverified_users_task")
def delete_unverified_users_task():
    """
    Удаляет из БД пользователей, не подтвердивших email в течение 2 дней.
    Запускается раз в сутки (с midnight).
    """
    import asyncio

    async def _cleanup():
        async with AsyncSessionLocal() as db:
            await delete_unverified_users(db)
            logger.info("Deleted unverified users older than 2 days")

    asyncio.run(_cleanup())


@celery_app.task(name="app.tasks.worker.send_verification_email_task")
def send_verification_email_task(email: str, code: str):
    """
    Фоновая задача отправки письма с кодом верификации.
    """
    import asyncio

    async def _send():
        await send_verification_email(email, code)
        logger.info(f"Sent verification email to {email}")

    asyncio.run(_send())