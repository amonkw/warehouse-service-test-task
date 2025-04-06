import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.kafka_processor import (
    process_movement_event,
)
from app.db.models import Warehouse, Product, StockItem, Movement, MovementStatus
import uuid
from datetime import datetime

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()  # Добавляем мок для commit/rollback, если нужно
    session.rollback = AsyncMock()
    return session


async def test_process_departure_success(mock_db_session: AsyncMock):
    # Arrange
    movement_id = uuid.uuid4()
    wh_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    timestamp_str = "2025-02-18T12:12:56Z"
    timestamp_dt = datetime.fromisoformat(timestamp_str)
    quantity = 50

    event_data = {
        "movement_id": str(movement_id),
        "warehouse_id": str(wh_id),
        "warehouse_code": "WH-1234",
        "product_id": str(prod_id),
        "quantity": quantity,
        "timestamp": timestamp_str,
        "event": "departure",
    }

    mock_warehouse = Warehouse(id=str(wh_id), code="WH-1234")
    mock_product = Product(id=str(prod_id))
    mock_stock = StockItem(
        id=str(uuid.uuid4()),
        warehouse_id=str(wh_id),
        product_id=str(prod_id),
        quantity=100,
    )

    # Настраиваем моки для get_or_create и get_stock_item
    # Используем patch для подмены внутренних вызовов
    with patch(
        "app.services.kafka_processor._get_or_create_warehouse",
        return_value=mock_warehouse,
    ) as mock_get_wh, patch(
        "app.services.kafka_processor._get_or_create_product", return_value=mock_product
    ) as mock_get_prod, patch(
        "app.services.kafka_processor._get_stock_item", return_value=mock_stock
    ) as mock_get_stock:

        # Act
        result_movement = await process_movement_event(mock_db_session, event_data)

        # Assert
        mock_get_wh.assert_called_once_with(mock_db_session, wh_id, "WH-1234")
        mock_get_prod.assert_called_once_with(mock_db_session, prod_id)
        mock_get_stock.assert_called_once_with(
            mock_db_session, mock_warehouse.id, mock_product.id
        )

        # Проверяем, что остаток уменьшился
        assert mock_stock.quantity == 50  # 100 - 50

        # Проверяем, что создался Movement
        mock_db_session.add.assert_called_once()
        added_obj = mock_db_session.add.call_args[0][0]
        assert isinstance(added_obj, Movement)
        assert added_obj.kafka_movement_id == movement_id
        assert added_obj.source_warehouse_id == mock_warehouse.id
        assert added_obj.product_id == mock_product.id
        assert added_obj.quantity == quantity
        assert added_obj.departure_time == timestamp_dt
        assert added_obj.status == MovementStatus.IN_TRANSIT

        mock_db_session.flush.assert_called_once()
        # Проверьте вызов commit/rollback в зависимости от того, где он ожидается (внутри process_movement_event или снаружи)
        # В текущей реализации commit/rollback делаются снаружи (в consumer/webhook)

        assert result_movement is added_obj


# Добавить тесты для arrival, недостаточного количества, невалидных данных и т.д.
