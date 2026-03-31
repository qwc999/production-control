from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer,
        primary_key=True)

    unique_code: Mapped[str] = mapped_column(String(100),
        nullable=False,
        unique=True,
        index=True)

    batch_id: Mapped[int] = mapped_column(Integer,
        ForeignKey("batches.id"),
        nullable=False,
        index=True)

    # Аггрегация
    is_aggregated: Mapped[bool] = mapped_column(Boolean,
        default=False,
        index=True)

    aggregated_at: Mapped[Optional[datetime]] = mapped_column(DateTime,
        nullable=True)

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime,
        default=datetime.utcnow)

    # Связи
    batch: Mapped["Batch"] = relationship("Batch", back_populates="products")

    __table_args__ = (
        Index('idx_product_batch_aggregated', 'batch_id', 'is_aggregated'),
    )
