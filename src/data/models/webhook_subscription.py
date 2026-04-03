from datetime import datetime

from sqlalchemy import Integer, String, ARRAY, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True)

    url: Mapped[str] = mapped_column(String(200),
                                     nullable=False)

    events: Mapped[list[str]] = mapped_column(ARRAY(String),
                                              nullable=False)  # ["batch_created", "batch_closed"]

    secret_key: Mapped[str] = mapped_column(String(200),
                                            nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean,
                                            default=True,
                                            nullable=False)

    retry_count: Mapped[int] = mapped_column(Integer,
                                             default=3)

    timeout: Mapped[int] = mapped_column(Integer,
                                         default=10)  # секунды

    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.utcnow,
                                                 onupdate=datetime.utcnow)

    deliveries: Mapped[list["WebhookDelivery"]] = relationship("WebhookDelivery",
                                                     back_populates="subscription")