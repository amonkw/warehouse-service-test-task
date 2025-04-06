from pydantic import BaseModel, Field
from uuid import UUID
from .warehouse import WarehouseResponse
from .product import ProductResponse


class StockItemBase(BaseModel):
    """Базовая схема для записи о товаре на складе"""
    warehouse_id: UUID
    product_id: UUID
    quantity: int = Field(..., ge=0, examples=[100])


class StockItemResponse(StockItemBase):
    """Схема для ответа с информацией о товаре на складе"""
    id: UUID
    warehouse: WarehouseResponse
    product: ProductResponse

    class Config:
        from_attributes = True


class StockLevelResponse(BaseModel):
    """Схема для ответа с информацией о наличии товара на складе"""
    id: UUID
    warehouse: WarehouseResponse
    quantity: int

    class Config:
        from_attributes = True


class WarehouseStockResponse(BaseModel):
    """Схема для ответа с информацией о всех товарах на складе"""
    warehouse: WarehouseResponse
    items: list[StockItemResponse]
    total_items: int

    class Config:
        from_attributes = True


from pydantic import BaseModel
from uuid import UUID
from .warehouse import WarehouseResponse
from .product import ProductResponse


class WarehouseProductStockResponse(BaseModel):
    """
    Схема для ответа с информацией о количестве конкретного товара на конкретном складе

    Attributes:
        id: UUID записи о товаре на складе
        warehouse: Информация о складе
        product: Информация о товаре
        quantity: Текущее количество товара на складе
    """
    id: UUID
    warehouse: WarehouseResponse
    product: ProductResponse
    quantity: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv",
                "warehouse": {
                    "id": "c1d70455-7e14-11e9-812a-70106f431230",
                    "code": "WH-1234",
                    "created_at": "2023-01-01T00:00:00Z"
                },
                "product": {
                    "id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
                    "name": "Ноутбук Dell XPS 15",
                    "created_at": "2023-01-01T00:00:00Z"
                },
                "quantity": 42
            }
        }