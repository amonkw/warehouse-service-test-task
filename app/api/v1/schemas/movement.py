from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from uuid import UUID
from typing import Optional


class MovementResponse(BaseModel):
    id: UUID = Field(..., examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    kafka_movement_id: UUID = Field(..., description="ID перемещения из Kafka")
    product_id: UUID = Field(..., description="ID товара")
    quantity: int = Field(..., gt=0, examples=[10], description="Количество товара")

    source_warehouse_id: Optional[UUID] = Field(None, description="ID исходного склада")
    destination_warehouse_id: Optional[UUID] = Field(
        None, description="ID склада назначения"
    )

    departure_time: Optional[datetime] = Field(None, examples=["2023-01-01T00:00:00Z"])
    arrival_time: Optional[datetime] = Field(None, examples=["2023-01-01T01:00:00Z"])

    status: str = Field(..., examples=["completed"], description="Статус перемещения")
    quantity_diff: Optional[int] = Field(None, description="Разница в количестве")

    @computed_field
    @property
    def duration_seconds(self) -> Optional[float]:
        """Возвращает абсолютную длительность в секундах (всегда >= 0 или None)"""
        if self.departure_time and self.arrival_time:
            return abs((self.arrival_time - self.departure_time).total_seconds())
        return None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "movement_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "quantity": 10,
                "source_warehouse_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "destination_warehouse_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "departure_time": "2023-01-01T00:00:00Z",
                "arrival_time": "2023-01-01T01:00:00Z",
                "status": "completed",
                "quantity_diff": 0,
                "duration_seconds": 3600.0,
            }
        }


class MovementDurationResponse(BaseModel):
    movement_id: UUID = Field(..., examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    duration_seconds: float = Field(
        ..., examples=[3600.0], description="Длительность в секундах"
    )
    departure_time: datetime = Field(..., examples=["2023-01-01T00:00:00Z"])
    arrival_time: datetime = Field(..., examples=["2023-01-01T01:00:00Z"])

    class Config:
        from_attributes = True
