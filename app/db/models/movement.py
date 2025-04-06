from datetime import datetime
from sqlalchemy import UUID, DateTime, Integer, ForeignKey, CheckConstraint, Index, Enum
from sqlalchemy.orm import mapped_column, Mapped
from enum import Enum as PyEnum
import uuid
from app.db.base import Base


class MovementStatus(str, PyEnum):
    PENDING = 'pending'
    IN_TRANSIT = 'in_transit'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class Movement(Base):
    __tablename__ = "movements"
    __table_args__ = (
        CheckConstraint(
            'quantity > 0',
            name='ck_movement_quantity_positive'
        ),
        CheckConstraint(
            'source_warehouse_id IS NOT NULL OR destination_warehouse_id IS NOT NULL',
            name='ck_movement_warehouse_presence'
        ),
        Index('ix_movement_kafka_id', 'kafka_movement_id'),
        Index('ix_movement_product', 'product_id'),
        Index('ix_movement_status', 'status'),
        {'comment': 'История перемещений товаров между складами'}
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Внутренний ID записи"
    )

    kafka_movement_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        comment="ID перемещения из Kafka"
    )

    source_warehouse_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("warehouses.id"),
        index=True
    )

    destination_warehouse_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("warehouses.id"),
        index=True
    )

    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Количество товара"
    )

    departure_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True
    )

    arrival_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True
    )

    status: Mapped[MovementStatus] = mapped_column(
        Enum(MovementStatus),
        default=MovementStatus.PENDING,
        nullable=False,
        index=True
    )

    quantity_diff: Mapped[int | None] = mapped_column(
        Integer,
        comment="Разница между отправленным и полученным количеством"
    )