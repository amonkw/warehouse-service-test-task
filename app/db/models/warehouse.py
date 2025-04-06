from sqlalchemy import (
    String, UUID
)
from sqlalchemy.orm import (
    relationship,
    mapped_column, Mapped
)
import uuid

from app.db.base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Идентификатор склада"
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Код склада в формате WH-XXXX"
    )

    stock_items: Mapped[list["StockItem"]] = relationship(
        back_populates="warehouse",
        cascade="all, delete-orphan"
    )
    movements_as_source: Mapped[list["Movement"]] = relationship(
        back_populates="source_warehouse",
        foreign_keys="Movement.source_warehouse_id"
    )
    movements_as_destination: Mapped[list["Movement"]] = relationship(
        back_populates="destination_warehouse",
        foreign_keys="Movement.destination_warehouse_id"
    )