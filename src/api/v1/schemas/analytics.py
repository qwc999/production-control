from datetime import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_batches: int
    active_batches: int
    closed_batches: int
    total_products: int
    aggregated_products: int
    aggregation_rate: float


class DashboardToday(BaseModel):
    batches_created: int
    batches_closed: int
    products_added: int
    products_aggregated: int


class DashboardShiftStats(BaseModel):
    batches: int
    products: int
    aggregated: int


class DashboardWorkCenterStats(BaseModel):
    id: str
    name: str
    batches_count: int
    products_count: int
    aggregation_rate: float


class DashboardStatisticsResponse(BaseModel):
    summary: DashboardSummary
    today: DashboardToday
    by_shift: dict[str, DashboardShiftStats]
    top_work_centers: list[DashboardWorkCenterStats]
    cached_at: datetime
