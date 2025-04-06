from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.stock_service import StockService
from app.db.session import get_session
from app.api.v1.schemas.stock import (
    StockItemResponse,
    StockLevelResponse,
    WarehouseStockResponse,
    WarehouseProductStockResponse
)

router = APIRouter()


@router.get("/items/{item_id}", response_model=StockItemResponse)
async def get_stock_item(
        item_id: UUID,
        db: AsyncSession = Depends(get_session)
):
    stock_item = await StockService.get_stock_item_by_id(db, item_id)
    if not stock_item:
        raise HTTPException(status_code=404, detail="Stock item not found")
    return stock_item


@router.get("/{warehouse_id}", response_model=WarehouseStockResponse)
async def get_warehouse_stock(
        warehouse_id: UUID,
        threshold: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_session)
):
    inventory = await StockService.get_warehouse_inventory(db, warehouse_id)

    # Apply threshold filter
    filtered_items = [item for item in inventory if item.quantity >= threshold]

    return {
        "warehouse_id": warehouse_id,
        "items": filtered_items,
        "total_items": len(filtered_items)
    }


@router.get("/{warehouse_id}/product/{product_id}",
            response_model=WarehouseProductStockResponse)
async def get_warehouse_product_stock(
        warehouse_id: UUID,
        product_id: UUID,
        db: AsyncSession = Depends(get_session)
):
    stock = await StockService.get_warehouse_product_stock(
        db, warehouse_id, product_id
    )
    if not stock:
        raise HTTPException(
            status_code=404,
            detail="Product not found in specified warehouse"
        )
    return stock


@router.get("/product/{product_id}", response_model=List[StockLevelResponse])
async def get_product_stock_levels(
        product_id: UUID,
        db: AsyncSession = Depends(get_session)
):
    stock_levels = await StockService.get_product_stock_levels(db, product_id)
    if not stock_levels:
        raise HTTPException(
            status_code=404,
            detail="Product not found in any warehouse"
        )
    return stock_levels