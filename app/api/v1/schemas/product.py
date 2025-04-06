from pydantic import BaseModel, Field
from uuid import UUID


class ProductBase(BaseModel):
    """Базовая схема для товара"""
    name: str = Field(..., min_length=1, max_length=100, examples=["Ноутбук Dell XPS 15"])


class ProductCreate(ProductBase):
    """Схема для создания товара"""
    pass


class ProductResponse(ProductBase):
    """Схема для ответа с информацией о товаре"""
    id: UUID
    created_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
                "name": "Ноутбук Dell XPS 15",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }