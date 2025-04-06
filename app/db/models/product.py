from sqlalchemy import (
    String, UUID
)
from sqlalchemy.orm import (
    relationship,
    mapped_column, Mapped
)
import uuid

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Идентификатор товара"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Наименование товара"
    )

    stock_items: Mapped[list["StockItem"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )
    movements: Mapped[list["Movement"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )
