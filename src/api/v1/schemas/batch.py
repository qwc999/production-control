from datetime import date, datetime

from pydantic import BaseModel, Field

from src.api.v1.schemas.product import ProductResponse


class BatchCreate(BaseModel):
    is_closed: bool = Field(default=False)
    task_description: str
    work_center_id: int
    work_center_name: str
    shift: str
    team: str
    batch_number: int
    batch_date: date
    nomenclature: str
    ekn_code: str
    shift_start: datetime
    shift_end: datetime


class BatchResponse(BaseModel):
    id: int
    is_closed: bool
    closed_at: datetime | None = None
    task_description: str
    work_center_id: int
    shift: str
    team: str
    batch_number: int
    batch_date: date
    nomenclature: str
    ekn_code: str
    shift_start: date
    shift_end: date
    created_at: datetime
    updated_at: datetime
    products: list[ProductResponse] = []

class BatchUpdate(BaseModel):
    is_closed: bool | None = None
    task_description: str | None = None
    shift: str | None = None
    team: str | None = None
    nomenclature: str | None = None
    ekn_code: str | None = None

class BatchFilter(BaseModel):
    is_closed: bool | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    work_center_id: int | None = None
    shift: str | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=50)