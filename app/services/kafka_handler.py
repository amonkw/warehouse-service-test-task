from uuid import UUID

from aiokafka import AIOKafkaConsumer
from fastapi import HTTPException

from app.config import settings
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import json


class KafkaHandler:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_GROUP_ID,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')))

    async def consume_messages(self):
        """Основной цикл обработки сообщений из Kafka"""
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                await self.process_message(msg.value)
        finally:
            await self.consumer.stop()

    async def process_message(self, message: dict):
        """Обработка одного сообщения из Kafka"""
        async with get_session() as db:
            try:
                event_data = message['data']
                event_type = event_data['event']

                # Основная логика обработки
                if event_type == 'arrival':
                    await self._handle_arrival(event_data, db)
                elif event_type == 'departure':
                    await self._handle_departure(event_data, db)

                await db.commit()
            except Exception as e:
                await db.rollback()
                # Логирование ошибки

    async def _handle_arrival(self, data: dict, db: AsyncSession):
        """Обработка события прибытия товара"""
        pass

    async def _handle_departure(self, data: dict, db: AsyncSession):
        """Обработка события отправки товара"""
        from app.services.stock_service import StockService  # Ленивый импорт
        try:
            await StockService.update_stock(
                db,
                warehouse_id=UUID(data["warehouse_id"]),
                product_id=UUID(data["product_id"]),
                quantity_change=-int(data["quantity"])
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
