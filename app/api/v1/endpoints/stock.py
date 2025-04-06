from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import StockItem
from app.db.session import get_session_dependency
from uuid import UUID

from app.api.v1.schemas.stock import ProductStockResponse

router = APIRouter()


# Получить количество товара на складе
@router.get(
    "/{warehouse_id}/products/{product_id}",
    response_model=ProductStockResponse,
    summary="Получить остаток товара на складе",
    responses={
        200: {"description": "Успешный ответ", "model": ProductStockResponse},
    },
)
async def get_product_stock(
        warehouse_id: UUID,
        product_id: UUID,
        session: AsyncSession = Depends(get_session_dependency),
):
    stmt = select(StockItem).where(
        and_(
            StockItem.warehouse_id == warehouse_id,
            StockItem.product_id == product_id,
        )
    )
    result = await session.execute(stmt)
    stock_item = result.scalar_one_or_none()

    quantity = stock_item.quantity if stock_item else 0

    return {
        "warehouse_id": warehouse_id,
        "product_id": product_id,
        "quantity": quantity,
    }