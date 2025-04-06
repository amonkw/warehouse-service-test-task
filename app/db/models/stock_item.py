from sqlalchemy import UUID, Integer, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import mapped_column, Mapped
import uuid
from app.db.base import Base


class StockItem(Base):
    __tablename__ = "stock_items"
    __table_args__ = (
        CheckConstraint(
            'quantity >= 0',
            name='ck_stock_quantity_non_negative'
        ),
        Index(
            'ix_stock_warehouse_product',
            'warehouse_id', 'product_id',
            unique=True
        ),
        {'comment': 'Текущие остатки товаров на складах'}
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Внутренний ID записи"
    )

    warehouse_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Текущее количество (>= 0)"
    )