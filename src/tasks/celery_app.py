from celery import Celery
from celery.schedules import crontab

from src.core.config import settings

celery_app = Celery(
    "production_control",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.tasks.batch_tasks",
        "src.tasks.report_tasks",
        "src.tasks.import_tasks",
        "src.tasks.export_tasks",
        "src.tasks.schedule_tasks"
    ]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,

    beat_schedule={
        "auto-close-expired-batches": {
            "task": "schedule.auto_close_expired_batches",
            "schedule": crontab(hour=1, minute=0)
            # "schedule": 30.0
        },
        "cleanup-old-files": {
            "task": "schedule.cleanup_old_files",
            "schedule": crontab(hour=2, minute=0)
            # "schedule": 30.0
        },
        "update_statistics": {
            "task": "schedule.update_cached_statistics",
            "schedule": crontab(minute="*/5")
            # "schedule": 30.0
        },
    }
)
