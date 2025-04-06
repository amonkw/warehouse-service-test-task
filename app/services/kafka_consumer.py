from aiokafka import AIOKafkaConsumer
from app.db.session import get_scoped_session
from app.api.v1.schemas import KafkaMessageData
from app.services.kafka_processor import process_movement_event
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class KafkaConsumer:
    """Фоновый потребитель Kafka-сообщений о перемещениях"""

    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="warehouse-service-group",
            auto_offset_reset="earliest",
            enable_auto_commit=False  # Ручное подтверждение после обработки
        )

    async def consume(self):
        """Основной цикл обработки сообщений"""
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                try:
                    message = self._parse_message(msg.value)
                    async with get_scoped_session() as db:
                        await process_movement_event(db, message)
                        await db.commit()
                        await self.consumer.commit()
                except ValueError as e:
                    logger.warning(f"Invalid message: {str(e)}")
                except Exception as e:
                    logger.error(f"Processing failed: {str(e)}", exc_info=True)
        finally:
            await self.consumer.stop()

    def _parse_message(self, raw_msg: bytes) -> KafkaMessageData:
        """Парсинг и валидация сырого сообщения"""
        try:
            data = json.loads(raw_msg.decode('utf-8'))
            return KafkaMessageData(**data)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid message format: {str(e)}")

async def run_consumer():
    """Запуск потребителя (вызывается при старте приложения)"""
    consumer = KafkaConsumer()
    await consumer.consume()