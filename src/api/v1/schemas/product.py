from pydantic import BaseModel


class ProductCreate(BaseModel):
    unique_code: str
    batch_id: int

class ProductResponse:
    ...