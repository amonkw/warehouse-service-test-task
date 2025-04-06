from pydantic import BaseModel, Field
from uuid import UUID


class WarehouseBase(BaseModel):
    """Базовая схема для склада"""
    code: str = Field(..., pattern=r"^WH-\d{4}$", examples=["WH-1234"])


class WarehouseCreate(WarehouseBase):
    """Схема для создания склада"""
    pass


class WarehouseResponse(WarehouseBase):
    """Схема для ответа с информацией о складе"""
    id: UUID
    created_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "c1d70455-7e14-11e9-812a-70106f431230",
                "code": "WH-1234",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }