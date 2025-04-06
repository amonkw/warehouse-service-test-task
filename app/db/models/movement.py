from datetime import datetime
from sqlalchemy import (
    UUID, DateTime, Integer, ForeignKey, Boolean
)
from sqlalchemy.orm import (
    relationship,
    mapped_column, Mapped
)
import uuid

from app.db.base import Base

class Movement(Base):
    __tablename__ = "movements"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Идентификатор перемещения"
    )
    movement_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        comment="Идентификатор перемещения (одинаковый для отправки и приемки)"
    )
    source_warehouse_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("warehouses.id"),
        nullable=True,
        comment="Склад-отправитель (null для поступлений извне)"
    )
    destination_warehouse_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("warehouses.id"),
        nullable=True,
        comment="Склад-получатель (null для отправок наружу)"
    )
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("products.id"),
        nullable=False,
        comment="Товар"
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Количество товара"
    )
    departure_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время отправки"
    )
    arrival_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время прибытия"
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Флаг завершенности перемещения"
    )

    source_warehouse: Mapped["Warehouse | None"] = relationship(
        back_populates="movements_as_source",
        foreign_keys=[source_warehouse_id]
    )
    destination_warehouse: Mapped["Warehouse | None"] = relationship(
        back_populates="movements_as_destination",
        foreign_keys=[destination_warehouse_id]
    )
    product: Mapped["Product"] = relationship(back_populates="movements")