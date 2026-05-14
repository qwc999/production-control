from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "production_control",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.tasks.batch_tasks",
        "src.tasks.report_tasks",
        "src.tasks.import_tasks",
        "src.tasks.export_tasks"
    ]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True
)
