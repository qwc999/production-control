from typing import Any

from pydantic import BaseModel


class TaskStartResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Any = None
