from sqlalchemy import UUID, Index
from sqlalchemy.orm import mapped_column, Mapped
import uuid
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index('ix_product_id', 'id', unique=True),
        {'comment': 'Справочник товаров (основной идентификатор из Kafka)'}
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID товара из Kafka"
    )