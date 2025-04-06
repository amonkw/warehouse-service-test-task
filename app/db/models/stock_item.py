from sqlalchemy import (
     UUID, Integer, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import (
    relationship,
    mapped_column, Mapped
)
import uuid

from app.db.base import Base


class StockItem(Base):
    __tablename__ = "stock_items"
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='quantity_non_negative'),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Идентификатор записи"
    )
    warehouse_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        comment="Ссылка на склад"
    )
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        comment="Ссылка на товар"
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Количество товара на складе"
    )

    warehouse: Mapped["Warehouse"] = relationship(back_populates="stock_items")
    product: Mapped["Product"] = relationship(back_populates="stock_items")