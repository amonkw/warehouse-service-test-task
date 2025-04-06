from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.db.models import Movement


class MovementService:
    @staticmethod
    async def get_movement(
            db: AsyncSession,
            movement_id: UUID
    ) -> Optional[Movement]:
        """Получение перемещения по ID"""
        result = await db.execute(
            select(Movement)
            .where(Movement.id == movement_id)
            .options(
                selectinload(Movement.source_warehouse),
                selectinload(Movement.destination_warehouse),
                selectinload(Movement.product)
            ))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_movements(
            db: AsyncSession,
            warehouse_id: Optional[UUID] = None,
            product_id: Optional[UUID] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            limit: int = 100,
            offset: int = 0
    ) -> list[Movement]:
        """Получение списка перемещений с фильтрами"""
        query = select(Movement).limit(limit).offset(offset)

        if warehouse_id:
            query = query.where(or_(
                Movement.source_warehouse_id == warehouse_id,
                Movement.destination_warehouse_id == warehouse_id
            ))

        # Другие условия фильтрации...

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def calculate_duration(
            movement: Movement
    ) -> Optional[float]:
        """Расчет длительности перемещения в секундах"""
        if movement.departure_time and movement.arrival_time:
            return (movement.arrival_time - movement.departure_time).total_seconds()
        return None

    @staticmethod
    async def create_movement(
            db: AsyncSession,
            movement_id: UUID,
            source_warehouse_id: UUID,
            product_id: UUID,
            quantity: int,
            departure_time: datetime,
            is_completed: bool
    ) -> Movement:
        movement = Movement(
            movement_id=movement_id,
            source_warehouse_id=source_warehouse_id,
            product_id=product_id,
            quantity=quantity,
            departure_time=departure_time,
            is_completed=is_completed
        )
        db.add(movement)
        await db.flush()
        return movement

    @staticmethod
    async def update_movement_arrival(
            db: AsyncSession,
            movement_id: UUID,
            destination_warehouse_id: UUID,
            arrival_time: datetime,
            received_quantity: int
    ) -> Movement:
        movement = await db.execute(
            select(Movement)
            .where(Movement.movement_id == movement_id))
        movement = movement.scalar_one_or_none()

        if not movement:
            raise ValueError("Movement not found")

        movement.destination_warehouse_id = destination_warehouse_id
        movement.arrival_time = arrival_time
        movement.is_completed = True

        if movement.quantity != received_quantity:
            movement.quantity_diff = received_quantity - movement.quantity

        await db.flush()
        return movement

    @staticmethod
    async def get_movement_by_movement_id(
            db: AsyncSession,
            movement_id: UUID
    ) -> Optional[Movement]:
        result = await db.execute(
            select(Movement)
            .where(Movement.movement_id == movement_id)
            .options(
                selectinload(Movement.source_warehouse),
                selectinload(Movement.destination_warehouse),
                selectinload(Movement.product)
            ))
        return result.scalar_one_or_none()