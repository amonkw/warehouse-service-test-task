"""empty message

Revision ID: 0002_update_all_models
Revises: 0001_init
Create Date: 2025-04-06 08:27:03.358329

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_update_all_models"
down_revision: Union[str, None] = "0001_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    movement_status = sa.Enum(
        "PENDING", "IN_TRANSIT", "COMPLETED", "CANCELLED", name="movementstatus"
    )
    movement_status.create(op.get_bind())
    op.add_column(
        "movements",
        sa.Column(
            "kafka_movement_id",
            sa.UUID(as_uuid=False),
            nullable=False,
            comment="ID перемещения из Kafka",
        ),
    )
    op.add_column(
        "movements",
        sa.Column("status", movement_status, nullable=False, server_default="PENDING"),
    )
    op.add_column(
        "movements",
        sa.Column(
            "quantity_diff",
            sa.Integer(),
            nullable=True,
            comment="Разница между отправленным и полученным количеством",
        ),
    )
    op.alter_column(
        "movements",
        "id",
        existing_type=sa.UUID(),
        comment="Внутренний ID записи",
        existing_comment="Идентификатор перемещения",
        existing_nullable=False,
    )
    op.alter_column(
        "movements",
        "source_warehouse_id",
        existing_type=sa.UUID(),
        comment=None,
        existing_comment="Склад-отправитель (null для поступлений извне)",
        existing_nullable=True,
    )
    op.alter_column(
        "movements",
        "destination_warehouse_id",
        existing_type=sa.UUID(),
        comment=None,
        existing_comment="Склад-получатель (null для отправок наружу)",
        existing_nullable=True,
    )
    op.alter_column(
        "movements",
        "product_id",
        existing_type=sa.UUID(),
        comment=None,
        existing_comment="Товар",
        existing_nullable=False,
    )
    op.alter_column(
        "movements",
        "departure_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        comment=None,
        existing_comment="Время отправки",
        existing_nullable=True,
    )
    op.alter_column(
        "movements",
        "arrival_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        comment=None,
        existing_comment="Время прибытия",
        existing_nullable=True,
    )
    op.create_index(
        "ix_movement_kafka_id", "movements", ["kafka_movement_id"], unique=False
    )
    op.create_index("ix_movement_product", "movements", ["product_id"], unique=False)
    op.create_index("ix_movement_status", "movements", ["status"], unique=False)
    op.create_index(
        op.f("ix_movements_arrival_time"), "movements", ["arrival_time"], unique=False
    )
    op.create_index(
        op.f("ix_movements_departure_time"),
        "movements",
        ["departure_time"],
        unique=False,
    )
    op.create_index(
        op.f("ix_movements_destination_warehouse_id"),
        "movements",
        ["destination_warehouse_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_movements_product_id"), "movements", ["product_id"], unique=False
    )
    op.create_index(
        op.f("ix_movements_source_warehouse_id"),
        "movements",
        ["source_warehouse_id"],
        unique=False,
    )
    op.create_index(op.f("ix_movements_status"), "movements", ["status"], unique=False)
    op.create_table_comment(
        "movements",
        "История перемещений товаров между складами",
        existing_comment=None,
        schema=None,
    )
    op.drop_column("movements", "is_completed")
    op.drop_column("movements", "movement_id")
    op.alter_column(
        "products",
        "id",
        existing_type=sa.UUID(),
        comment="UUID товара из Kafka",
        existing_comment="Идентификатор товара",
        existing_nullable=False,
    )
    op.create_index("ix_product_id", "products", ["id"], unique=True)
    op.create_table_comment(
        "products",
        "Справочник товаров (основной идентификатор из Kafka)",
        existing_comment=None,
        schema=None,
    )
    op.drop_column("products", "name")
    op.alter_column(
        "stock_items",
        "id",
        existing_type=sa.UUID(),
        comment="Внутренний ID записи",
        existing_comment="Идентификатор записи",
        existing_nullable=False,
    )
    op.alter_column(
        "stock_items",
        "warehouse_id",
        existing_type=sa.UUID(),
        comment=None,
        existing_comment="Ссылка на склад",
        existing_nullable=False,
    )
    op.alter_column(
        "stock_items",
        "product_id",
        existing_type=sa.UUID(),
        comment=None,
        existing_comment="Ссылка на товар",
        existing_nullable=False,
    )
    op.alter_column(
        "stock_items",
        "quantity",
        existing_type=sa.INTEGER(),
        comment="Текущее количество (>= 0)",
        existing_comment="Количество товара на складе",
        existing_nullable=False,
    )
    op.create_index(
        "ix_stock_warehouse_product",
        "stock_items",
        ["warehouse_id", "product_id"],
        unique=True,
    )
    op.create_table_comment(
        "stock_items",
        "Текущие остатки товаров на складах",
        existing_comment=None,
        schema=None,
    )
    op.alter_column(
        "warehouses",
        "id",
        existing_type=sa.UUID(),
        comment="UUID склада из Kafka",
        existing_comment="Идентификатор склада",
        existing_nullable=False,
    )
    op.alter_column(
        "warehouses",
        "code",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=10),
        comment="Уникальный код в формате WH-XXXX",
        existing_comment="Код склада в формате WH-XXXX",
        existing_nullable=False,
    )
    op.drop_constraint("warehouses_code_key", "warehouses", type_="unique")
    op.create_index("ix_warehouse_code", "warehouses", ["code"], unique=True)
    op.create_table_comment(
        "warehouses", "Справочник складов", existing_comment=None, schema=None
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table_comment(
        "warehouses", existing_comment="Справочник складов", schema=None
    )
    op.drop_index("ix_warehouse_code", table_name="warehouses")
    op.create_unique_constraint("warehouses_code_key", "warehouses", ["code"])
    op.alter_column(
        "warehouses",
        "code",
        existing_type=sa.String(length=10),
        type_=sa.VARCHAR(length=50),
        comment="Код склада в формате WH-XXXX",
        existing_comment="Уникальный код в формате WH-XXXX",
        existing_nullable=False,
    )
    op.alter_column(
        "warehouses",
        "id",
        existing_type=sa.UUID(),
        comment="Идентификатор склада",
        existing_comment="UUID склада из Kafka",
        existing_nullable=False,
    )
    op.drop_table_comment(
        "stock_items",
        existing_comment="Текущие остатки товаров на складах",
        schema=None,
    )
    op.drop_index("ix_stock_warehouse_product", table_name="stock_items")
    op.alter_column(
        "stock_items",
        "quantity",
        existing_type=sa.INTEGER(),
        comment="Количество товара на складе",
        existing_comment="Текущее количество (>= 0)",
        existing_nullable=False,
    )
    op.alter_column(
        "stock_items",
        "product_id",
        existing_type=sa.UUID(),
        comment="Ссылка на товар",
        existing_nullable=False,
    )
    op.alter_column(
        "stock_items",
        "warehouse_id",
        existing_type=sa.UUID(),
        comment="Ссылка на склад",
        existing_nullable=False,
    )
    op.alter_column(
        "stock_items",
        "id",
        existing_type=sa.UUID(),
        comment="Идентификатор записи",
        existing_comment="Внутренний ID записи",
        existing_nullable=False,
    )
    op.add_column(
        "products",
        sa.Column(
            "name",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=False,
            comment="Наименование товара",
        ),
    )
    op.drop_table_comment(
        "products",
        existing_comment="Справочник товаров (основной идентификатор из Kafka)",
        schema=None,
    )
    op.drop_index("ix_product_id", table_name="products")
    op.alter_column(
        "products",
        "id",
        existing_type=sa.UUID(),
        comment="Идентификатор товара",
        existing_comment="UUID товара из Kafka",
        existing_nullable=False,
    )
    op.add_column(
        "movements",
        sa.Column(
            "movement_id",
            sa.UUID(),
            autoincrement=False,
            nullable=False,
            comment="Идентификатор перемещения (одинаковый для отправки и приемки)",
        ),
    )
    op.add_column(
        "movements",
        sa.Column(
            "is_completed",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
            comment="Флаг завершенности перемещения",
        ),
    )
    op.drop_table_comment(
        "movements",
        existing_comment="История перемещений товаров между складами",
        schema=None,
    )
    op.drop_index(op.f("ix_movements_status"), table_name="movements")
    op.drop_index(op.f("ix_movements_source_warehouse_id"), table_name="movements")
    op.drop_index(op.f("ix_movements_product_id"), table_name="movements")
    op.drop_index(op.f("ix_movements_destination_warehouse_id"), table_name="movements")
    op.drop_index(op.f("ix_movements_departure_time"), table_name="movements")
    op.drop_index(op.f("ix_movements_arrival_time"), table_name="movements")
    op.drop_index("ix_movement_status", table_name="movements")
    op.drop_index("ix_movement_product", table_name="movements")
    op.drop_index("ix_movement_kafka_id", table_name="movements")
    op.alter_column(
        "movements",
        "arrival_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        comment="Время прибытия",
        existing_nullable=True,
    )
    op.alter_column(
        "movements",
        "departure_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        comment="Время отправки",
        existing_nullable=True,
    )
    op.alter_column(
        "movements",
        "product_id",
        existing_type=sa.UUID(),
        comment="Товар",
        existing_nullable=False,
    )
    op.alter_column(
        "movements",
        "destination_warehouse_id",
        existing_type=sa.UUID(),
        comment="Склад-получатель (null для отправок наружу)",
        existing_nullable=True,
    )
    op.alter_column(
        "movements",
        "source_warehouse_id",
        existing_type=sa.UUID(),
        comment="Склад-отправитель (null для поступлений извне)",
        existing_nullable=True,
    )
    op.alter_column(
        "movements",
        "id",
        existing_type=sa.UUID(),
        comment="Идентификатор перемещения",
        existing_comment="Внутренний ID записи",
        existing_nullable=False,
    )
    op.drop_column("movements", "quantity_diff")
    op.drop_column("movements", "status")
    op.drop_column("movements", "kafka_movement_id")
    # ### end Alembic commands ###
