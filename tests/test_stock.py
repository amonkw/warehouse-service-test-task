import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Warehouse, Product, StockItem
import uuid

pytestmark = pytest.mark.asyncio


async def test_get_product_stock_exists(client: AsyncClient, db_session: AsyncSession):
    # Arrange: Создаем данные в тестовой БД
    wh_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    warehouse = Warehouse(id=str(wh_id), code=f"WH-{str(wh_id)[:4]}")
    product = Product(id=str(prod_id))
    stock = StockItem(warehouse_id=str(wh_id), product_id=str(prod_id), quantity=50)
    db_session.add_all([warehouse, product, stock])
    await db_session.commit()

    # Act: Делаем запрос к API
    response = await client.get(f"/api/v1/warehouse/{wh_id}/products/{prod_id}")

    # Assert: Проверяем результат
    assert response.status_code == 200
    data = response.json()
    assert data["warehouse_id"] == str(wh_id)
    assert data["product_id"] == str(prod_id)
    assert data["quantity"] == 50


async def test_get_product_stock_not_exists(
    client: AsyncClient, db_session: AsyncSession
):
    # Arrange: ID склада/товара, которых нет в базе
    wh_id = uuid.uuid4()
    prod_id = uuid.uuid4()

    # Act: Делаем запрос к API
    response = await client.get(f"/api/v1/warehouse/{wh_id}/products/{prod_id}")

    # Assert: Проверяем результат (ожидаем 0)
    assert response.status_code == 200
    data = response.json()
    assert data["warehouse_id"] == str(wh_id)
    assert data["product_id"] == str(prod_id)
    assert data["quantity"] == 0
