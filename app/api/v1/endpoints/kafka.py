from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime

from app.services.movement_service import MovementService
from app.services.stock_service import StockService
from app.db.session import get_session
from app.api.v1.schemas.kafka import KafkaMessage, KafkaResponse
from app.api.v1.schemas.movement import MovementResponse

router = APIRouter()


@router.post("/webhook", response_model=KafkaResponse)
async def handle_kafka_message(
        message: KafkaMessage,
        db: AsyncSession = Depends(get_session)
):
    """
    Webhook для приема сообщений из Kafka

    - Принимает события arrival/departure
    - Обновляет состояние складов
    - Создает/обновляет записи о перемещениях
    - Возвращает статус обработки
    """
    try:
        event_data = message.data
        event_type = event_data["event"]
        movement_id = UUID(event_data["movement_id"])

        if event_type == "departure":
            # Обработка отправки
            await StockService.update_stock(
                db,
                warehouse_id=UUID(event_data["warehouse_id"]),
                product_id=UUID(event_data["product_id"]),
                quantity_change=-int(event_data["quantity"])
            )

            movement = await MovementService.create_movement(
                db,
                movement_id=movement_id,
                source_warehouse_id=UUID(event_data["warehouse_id"]),
                product_id=UUID(event_data["product_id"]),
                quantity=int(event_data["quantity"]),
                departure_time=datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00")),
                is_completed=False
            )

        elif event_type == "arrival":
            # Обработка получения
            await StockService.update_stock(
                db,
                warehouse_id=UUID(event_data["warehouse_id"]),
                product_id=UUID(event_data["product_id"]),
                quantity_change=int(event_data["quantity"])
            )

            movement = await MovementService.update_movement_arrival(
                db,
                movement_id=movement_id,
                destination_warehouse_id=UUID(event_data["warehouse_id"]),
                arrival_time=datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00")),
                received_quantity=int(event_data["quantity"])
            )

        await db.commit()
        return KafkaResponse(
            status="processed",
            movement_id=movement_id
        )

    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processed/{movement_id}", response_model=MovementResponse)
async def check_processed_movement(
        movement_id: UUID,
        db: AsyncSession = Depends(get_session)
):
    """
    Проверить статус обработки перемещения

    - **movement_id**: UUID перемещения
    - Возвращает информацию о перемещении если оно было обработано
    """
    movement = await MovementService.get_movement_by_movement_id(db, movement_id)
    if not movement:
        raise HTTPException(
            status_code=404,
            detail="Movement not found or not processed yet"
        )
    return movement