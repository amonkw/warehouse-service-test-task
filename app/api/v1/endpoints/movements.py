from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.session import get_session_dependency
from app.db.models import Movement
from app.api.v1.schemas import (
    MovementResponse,
    MovementDurationResponse,
)
from app.services.redis import get_cache, get_movement_cache_key, set_cache

router = APIRouter()


# Получить информацию о перемещении
@router.get(
    "/{movement_id}",
    response_model=MovementResponse,
    summary="Получить перемещение по ID",
    responses={
        404: {"description": "Перемещение не найдено"},
        200: {"description": "Успешный ответ", "model": MovementResponse},
    },
)
async def get_movement(
    movement_id: UUID,
    session: AsyncSession = Depends(get_session_dependency),
):
    cache_key = get_movement_cache_key(movement_id)
    cached_data = await get_cache(cache_key)
    if cached_data is not None:
        return MovementResponse.model_validate(cached_data)

    stmt = select(Movement).where(Movement.id == movement_id)
    result = await session.execute(stmt)
    movement = result.scalar_one_or_none()

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found",
        )
    # Преобразуем в схему перед кэшированием и возвратом
    response_model = MovementResponse.model_validate(movement)
    await set_cache(cache_key, response_model.model_dump(mode="json"))
    return response_model


@router.get(
    "/{movement_id}/duration",
    response_model=MovementDurationResponse,
    summary="Получить длительность перемещения",
    responses={
        404: {"description": "Перемещение не найдено"},
        400: {"description": "Не указаны временные метки"},
        200: {"description": "Успешный ответ", "model": MovementDurationResponse},
    },
)
async def get_movement_duration(
    movement_id: UUID,
    session: AsyncSession = Depends(get_session_dependency),
):
    stmt = select(Movement).where(Movement.id == movement_id)
    result = await session.execute(stmt)
    movement = result.scalar_one_or_none()

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found",
        )

    if not movement.departure_time or not movement.arrival_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Departure or arrival time is missing",
        )

    duration = (movement.arrival_time - movement.departure_time).total_seconds()

    return {
        "movement_id": movement.id,
        "duration_seconds": duration,
        "departure_time": movement.departure_time,
        "arrival_time": movement.arrival_time,
    }
