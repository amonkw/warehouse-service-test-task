from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Optional, List

from app.services.movement_service import MovementService
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.movement import (
    MovementResponse,
    MovementListResponse,
    MovementDurationResponse
)

router = APIRouter()


@router.get("/{movement_id}", response_model=MovementResponse)
async def get_movement(
        movement_id: UUID,
        db: AsyncSession = Depends(get_session)
):
    movement = await MovementService.get_movement(db, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    return movement


@router.get("/", response_model=List[MovementListResponse])
async def list_movements(
        warehouse_id: Optional[UUID] = Query(None),
        product_id: Optional[UUID] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_session)
):
    movements = await MovementService.list_movements(
        db,
        warehouse_id=warehouse_id,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return movements


@router.get("/{movement_id}/duration", response_model=MovementDurationResponse)
async def get_movement_duration(
        movement_id: UUID,
        db: AsyncSession = Depends(get_session)
):
    movement = await MovementService.get_movement(db, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")

    if not movement.is_completed:
        raise HTTPException(status_code=400, detail="Movement not completed")

    duration = await MovementService.calculate_duration(movement)

    return {
        "movement_id": movement.id,
        "duration_seconds": duration,
        "departure_time": movement.departure_time,
        "arrival_time": movement.arrival_time
    }