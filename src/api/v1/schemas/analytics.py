from datetime import datetime, date

from pydantic import BaseModel


# DASHBOARD STATS
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


# BATCH STATS
class BatchStatisticsBatchInfo(BaseModel):
    id: int
    team: str
    batch_number: int
    batch_date: date
    is_closed: bool


class BatchProductionStats(BaseModel):
    total_products: int
    aggregated: int
    remaining: int
    aggregation_rate: float


class BatchTimelineStats(BaseModel):
    shift_duration_hours: float
    elapsed_hours: float
    products_per_hour: float
    estimated_completion: datetime | None = None


class BatchStatisticsResponse(BaseModel):
    batch_info: BatchStatisticsBatchInfo
    production_stats: BatchProductionStats
    timeline: BatchTimelineStats
