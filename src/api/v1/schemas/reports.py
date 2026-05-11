from typing import Literal

from pydantic import BaseModel


class BatchReportRequest(BaseModel):
    format: Literal["excel"] = "excel"


class BatchReportResult(BaseModel):
    success: bool
    file_url: str
    file_name: str
    file_size: int
    expires_at: str
