from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer,
        primary_key=True)

    subscription_id: Mapped[int] = mapped_column(Integer,
        ForeignKey("webhook_subscriptions.id"))

    event_type: Mapped[str] = mapped_column(String(100),
        nullable=False)

    payload: Mapped[dict] = mapped_column(JSON,
        nullable=False)

    status: Mapped[str] = mapped_column(String(10),
        nullable=False) # "pending", "success", "failed"

    attempts: Mapped[int] = mapped_column(Integer,
        default=0)

    response_status: Mapped[Optional[int]] = mapped_column(Integer,
        nullable=True)

    response_body: Mapped[Optional[str]] = mapped_column(String(500),
        nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(String(200),
        nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,
        default=datetime.utcnow)

    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime,
        nullable=True)

    subscription: Mapped["WebhookSubscription"] = relationship("WebhookSubscription",
                                                             back_populates="deliveries")
