from datetime import datetime, date
from typing import Optional

from sqlalchemy import Integer, Boolean, DateTime, String, UniqueConstraint, Index, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(Integer,
        primary_key=True)

    is_closed: Mapped[bool] = mapped_column(Boolean,
        default=False,
        nullable=False)

    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime,
        nullable=True)

    # Описание задания
    task_description: Mapped[str] = mapped_column(String(500),
        nullable=False)

    work_center_id: Mapped[int] = mapped_column(Integer,
        ForeignKey("work_centers.id"),
        nullable=False)

    shift: Mapped[str] = mapped_column(String(50),
        nullable=False)

    team: Mapped[str] = mapped_column(String(50),
        nullable=False)

    # Идентификация партии
    batch_number: Mapped[int] = mapped_column(Integer,
        nullable=False,
        index=True)

    batch_date: Mapped[date] = mapped_column(Date,
        nullable=False,
        index=True)

    # Продукция
    nomenclature: Mapped[str] = mapped_column(String(100),
        nullable=False)

    ekn_code: Mapped[str] = mapped_column(String(20),
        nullable=False)

    # Временные рамки
    shift_start: Mapped[datetime] = mapped_column(DateTime,
        nullable=False)

    shift_end: Mapped[datetime] = mapped_column(DateTime,
        nullable=False)

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime,
        default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    # Связи
    products: Mapped[list["Product"]] = relationship("Product", back_populates="batch")
    work_center: Mapped["WorkCenter"] = relationship("WorkCenter", back_populates="batches")

    # Уникальный составной индекс
    __table_args__ = (
        UniqueConstraint('batch_number', 'batch_date', name='uq_batch_number_date'),
        Index('idx_batch_closed', 'is_closed'),
        Index('idx_batch_shift_times', 'shift_start', 'shift_end'),
        )