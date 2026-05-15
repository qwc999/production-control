## Commands

Worker:  
poetry run celery -A src.tasks.celery_app.celery_app worker --loglevel=info --pool=solo --concurrency=1

Beat:  
poetry run celery -A src.tasks.celery_app.celery_app beat --loglevel=info
