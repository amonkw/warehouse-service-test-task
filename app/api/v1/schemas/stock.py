from pydantic import BaseModel, Field
from uuid import UUID


class ProductStockResponse(BaseModel):
    warehouse_id: UUID = Field(..., examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    product_id: UUID = Field(..., examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    quantity: int = Field(..., examples=[42], description="Текущее количество товара")

    class Config:
        from_attributes = True
