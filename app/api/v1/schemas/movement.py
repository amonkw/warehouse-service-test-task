from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from .warehouse import WarehouseResponse
from .product import ProductResponse


class MovementBase(BaseModel):
    """Базовая схема для перемещения"""
    movement_id: UUID
    product_id: UUID
    quantity: int = Field(..., gt=0, examples=[10])


class MovementCreate(MovementBase):
    """Схема для создания перемещения"""
    source_warehouse_id: Optional[UUID] = None
    destination_warehouse_id: Optional[UUID] = None


class MovementResponse(MovementBase):
    """Схема для ответа с полной информацией о перемещении"""
    id: UUID
    source_warehouse: Optional[WarehouseResponse] = None
    destination_warehouse: Optional[WarehouseResponse] = None
    product: ProductResponse
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    is_completed: bool
    quantity_diff: Optional[int] = None

    class Config:
        from_attributes = True


class MovementListResponse(BaseModel):
    """Схема для ответа с краткой информацией о перемещении (для списков)"""
    id: UUID
    movement_id: UUID
    product: ProductResponse
    quantity: int
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    is_completed: bool

    class Config:
        from_attributes = True


class MovementDurationResponse(BaseModel):
    """Схема для ответа с информацией о длительности перемещения"""
    movement_id: UUID
    duration_seconds: float
    departure_time: datetime
    arrival_time: datetime

    class Config:
        from_attributes = True