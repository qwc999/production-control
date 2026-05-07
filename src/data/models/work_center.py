from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base


class WorkCenter(Base):
    __tablename__ = "work_centers"

    id: Mapped[int] = mapped_column(Integer,
        primary_key=True)

    identifier: Mapped[str] = mapped_column(String(500),
        unique=True,
        index=True,
        nullable=False)

    name: Mapped[str] = mapped_column(String(500),
        nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc))

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc))

    batches: Mapped[list["Batch"]] = relationship("Batch", back_populates="work_center")
