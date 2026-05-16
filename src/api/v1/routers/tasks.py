from celery.result import AsyncResult
from fastapi import APIRouter

from src.api.v1.schemas.tasks import TaskStatusResponse
from src.tasks.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}",
             response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    if task.status == "PENDING":
        result = None
    elif task.status in {"STARTED", "PROGRESS"}:
        result = task.info
    elif task.status == "FAILURE":
        result = {"error": str(task.result)}
    else:
        result = task.result

    return TaskStatusResponse(
        task_id=task_id,
        status=str(task.status),
        result=result
    )
