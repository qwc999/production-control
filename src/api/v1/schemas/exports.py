from datetime import date
from pydantic import BaseModel


class BatchExportFilter(BaseModel):
    is_closed: bool | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    work_center_identifier: str | None = None
    shift: str | None = None
