from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models import StockItem


class StockService:
    @staticmethod
    async def get_stock_level(
            db: AsyncSession,
            warehouse_id: UUID,
            product_id: UUID
    ) -> Optional[int]:
        """Получение текущего количества товара на складе"""
        result = await db.execute(
            select(StockItem.quantity)
            .where(StockItem.warehouse_id == warehouse_id)
            .where(StockItem.product_id == product_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_stock(
            db: AsyncSession,
            warehouse_id: UUID,
            product_id: UUID,
            quantity_change: int
    ) -> StockItem:
        """Обновление количества товара на складе"""
        stock_item = await db.execute(
            select(StockItem)
            .where(StockItem.warehouse_id == warehouse_id)
            .where(StockItem.product_id == product_id))
        stock_item = stock_item.scalar_one_or_none()

        if not stock_item:
            if quantity_change < 0:
                raise ValueError("Cannot have negative stock for new item")
            # Создание новой записи если не существует
            stock_item = StockItem(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=0
            )
            db.add(stock_item)

        new_quantity = stock_item.quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Not enough quantity. Available: {stock_item.quantity}, requested: {-quantity_change}")
        stock_item.quantity = new_quantity
        return stock_item

    @staticmethod
    async def get_warehouse_inventory(
            db: AsyncSession,
            warehouse_id: UUID
    ) -> list[StockItem]:
        """Получение полной инвентаризации склада"""
        result = await db.execute(
            select(StockItem)
            .where(StockItem.warehouse_id == warehouse_id)
            .options(
                selectinload(StockItem.product)
            ))
        return list(result.scalars().all())

    @staticmethod
    async def get_stock_item_by_id(
            db: AsyncSession,
            item_id: UUID
    ) -> Optional[StockItem]:
        result = await db.execute(
            select(StockItem)
            .where(StockItem.id == item_id)
            .options(
                selectinload(StockItem.warehouse),
                selectinload(StockItem.product)
            ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_warehouse_product_stock(
            db: AsyncSession,
            warehouse_id: UUID,
            product_id: UUID
    ) -> Optional[StockItem]:
        result = await db.execute(
            select(StockItem)
            .where(StockItem.warehouse_id == warehouse_id)
            .where(StockItem.product_id == product_id)
            .options(
                selectinload(StockItem.warehouse),
                selectinload(StockItem.product)
            ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_product_stock_levels(
            db: AsyncSession,
            product_id: UUID
    ) -> List[StockItem]:
        result = await db.execute(
            select(StockItem)
            .where(StockItem.product_id == product_id)
            .where(StockItem.quantity > 0)
            .options(
                selectinload(StockItem.warehouse)
            ))
        return list(result.scalars().all())