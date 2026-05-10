## Commands

poetry run celery -A src.tasks.celery_app.celery_app worker --loglevel=info --pool=solo --concurrency=1

