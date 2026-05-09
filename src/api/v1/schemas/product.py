from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    unique_code: str
    batch_id: int

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unique_code: str
    is_aggregated: bool
    aggregated_at: datetime | None = None

class ProductAggregateRequest(BaseModel):
    unique_codes: list[str] = Field(min_length=1)

class ProductAggregateResponse(BaseModel):
    batch_id: int
    total: int
    aggregated: int
    failed: int
    errors: list[dict]
