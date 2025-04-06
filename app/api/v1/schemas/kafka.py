from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Optional


class KafkaMessage(BaseModel):
    """Схема для сообщения из Kafka"""
    id: UUID
    source: str = Field(..., pattern=r"^WH-\d{4}$", examples=["WH-3423"])
    specversion: str = Field(..., examples=["1.0"])
    type: str = Field(..., examples=["ru.retail.warehouses.movement"])
    datacontenttype: str = Field(..., examples=["application/json"])
    dataschema: str = Field(..., examples=["ru.retail.warehouses.movement.v1.0"])
    time: int = Field(..., examples=[1737439421623])
    subject: str = Field(..., examples=["WH-3423:ARRIVAL"])
    destination: str = Field(..., examples=["ru.retail.warehouses"])
    data: Dict

    class Config:
        json_schema_extra = {
            "example": {
                "id": "b3b53031-e83a-4654-87f5-b6b6fb09fd99",
                "source": "WH-3423",
                "specversion": "1.0",
                "type": "ru.retail.warehouses.movement",
                "datacontenttype": "application/json",
                "dataschema": "ru.retail.warehouses.movement.v1.0",
                "time": 1737439421623,
                "subject": "WH-3423:ARRIVAL",
                "destination": "ru.retail.warehouses",
                "data": {
                    "movement_id": "c6290746-790e-43fa-8270-014dc90e02e0",
                    "warehouse_id": "c1d70455-7e14-11e9-812a-70106f431230",
                    "timestamp": "2025-02-18T14:34:56Z",
                    "event": "arrival",
                    "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
                    "quantity": 100
                }
            }
        }


class KafkaResponse(BaseModel):
    """Схема для ответа обработчика Kafka"""
    status: str = Field(..., examples=["processed"])
    movement_id: Optional[UUID] = None
    details: Optional[str] = None