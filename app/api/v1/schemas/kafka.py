from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional


class MovementEventType(str, Enum):
    ARRIVAL = "arrival"
    DEPARTURE = "departure"


class KafkaMessageData(BaseModel):
    """Схема для data-части Kafka-сообщения"""
    movement_id: UUID = Field(..., description="Уникальный ID перемещения (одинаковый для отправки/приемки)")
    warehouse_id: UUID = Field(..., description="ID склада")
    product_id: UUID = Field(..., description="ID товара")
    quantity: int = Field(..., gt=0, description="Количество товара (должно быть > 0)")
    timestamp: datetime = Field(..., description="Время события в ISO формате")
    event: MovementEventType = Field(..., description="Тип события: arrival или departure")


class KafkaFullMessage(BaseModel):
    """Полная схема Kafka-сообщения"""
    id: UUID = Field(default=None, description="ID сообщения")
    source: str = Field(default=None, pattern=r'^WH-\d{4}$', description="Источник отправки в формате WH-XXXX")
    specversion: Optional[str] = Field(default=None, description="Версия спецификации CloudEvents")
    type: Optional[str] = Field(default=None, description="Тип события", )
    datacontenttype: Optional[str] = Field(default="application/json", description="Тип содержимого")
    dataschema: Optional[str] = Field(default=None, description="Схема данных")
    time: Optional[int] = Field(default=None, description="Временная метка в миллисекундах")
    subject: Optional[str] = Field(default=None, description="Тема сообщения")
    destination: Optional[str] = Field(default=None, description="Назначение сообщения")
    data: KafkaMessageData = Field(..., description="Данные перемещения")


class KafkaWebhookRequest(KafkaFullMessage):
    """Схема для вебхук-запроса (имитация Kafka)"""
    pass


class KafkaResponse(BaseModel):
    """Схема ответа API"""
    status: str = Field(..., examples=["processed"], description="Статус обработки")
    message_id: UUID = Field(..., description="ID обработанного сообщения")
    movement_id: UUID = Field(..., description="ID перемещения")
    details: dict = Field(None, description="Дополнительные детали")
