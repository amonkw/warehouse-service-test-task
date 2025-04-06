from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas import KafkaWebhookRequest, KafkaResponse
from app.services.kafka_processor import process_movement_event
from app.db.session import get_session_dependency
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


def validate_and_prepare_event_data(message_data):
    """Валидация и подготовка данных события"""
    try:
        # Преобразуем UUID в строки для обработки
        movement_id = str(message_data.movement_id)
        warehouse_id = str(message_data.warehouse_id)
        product_id = str(message_data.product_id)

        # Проверяем quantity
        if message_data.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Проверяем timestamp
        if not isinstance(message_data.timestamp, datetime):
            raise ValueError("Invalid timestamp format")

        return {
            "movement_id": movement_id,
            "warehouse_id": warehouse_id,
            "product_id": product_id,
            "quantity": message_data.quantity,
            "timestamp": message_data.timestamp.isoformat(),
            "event": message_data.event.value
        }
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise ValueError(f"Invalid event data: {str(e)}")


@router.post(
    "/webhook",
    response_model=KafkaResponse,
    summary="Обработчик Kafka-сообщений",
    responses={
        200: {"description": "Сообщение успешно обработано"},
        400: {"description": "Неверные данные в запросе"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def kafka_webhook(
        request: KafkaWebhookRequest,
        db: AsyncSession = Depends(get_session_dependency)
) -> KafkaResponse:
    """
    Обрабатывает входящие сообщения о перемещениях товаров.

    Требования к данным:
    - source: должен быть в формате WH-XXXX или будет автоматически сгенерирован
    - quantity: должно быть положительным числом
    - timestamp: должен быть валидной датой/временем
    """
    try:
        # Валидация и подготовка данных
        event_data = validate_and_prepare_event_data(request.data)

        # Добавляем код склада (из source или генерируем)
        warehouse_code = (
            request.source
            if hasattr(request, 'source') and request.source.startswith('WH-')
            else f"WH-{str(request.data.warehouse_id)[:4]}"
        )
        event_data['warehouse_code'] = warehouse_code

        # Обработка события
        await process_movement_event(db, event_data)

        # Формируем успешный ответ
        return KafkaResponse(
            status="processed",
            message_id=request.id,
            movement_id=request.data.movement_id,
            details={
                "event_type": request.data.event.value,
                "warehouse_id": str(request.data.warehouse_id),
                "product_id": str(request.data.product_id),
                "processed_at": datetime.utcnow().isoformat()
            }
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )