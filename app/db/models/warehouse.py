from sqlalchemy import String, UUID, CheckConstraint, Index
from sqlalchemy.orm import mapped_column, Mapped, validates
import uuid
import re
from app.db.base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"
    __table_args__ = (
        CheckConstraint(
            "code ~ '^WH-\\d{4}$'",
            name="ck_warehouse_code_format"
        ),
        Index('ix_warehouse_code', 'code', unique=True),
        {'comment': 'Справочник складов'}
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID склада из Kafka"
    )

    code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Уникальный код в формате WH-XXXX"
    )

    @validates('code')
    def validate_code(self, key, code):
        if not re.match(r'^WH-\d{4}$', code):
            raise ValueError("Код склада должен быть в формате WH-XXXX")
        return code