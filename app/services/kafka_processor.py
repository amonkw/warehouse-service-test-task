from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Movement, StockItem, Warehouse, Product, MovementStatus
from uuid import UUID
import logging
from datetime import datetime

from app.services.redis import (
    get_stock_cache_key,
    invalidate_cache,
    get_movement_cache_key,
)

logger = logging.getLogger(__name__)


async def process_movement_event(db: AsyncSession, event_data: dict) -> Movement:
    """Основной обработчик событий перемещения"""
    try:
        # Валидация и преобразование UUID
        movement_id = _validate_uuid(event_data.get("movement_id"), "movement_id")
        warehouse_id = _validate_uuid(event_data.get("warehouse_id"), "warehouse_id")
        product_id = _validate_uuid(event_data.get("product_id"), "product_id")
        quantity = _validate_quantity(event_data.get("quantity"))
        timestamp = _validate_timestamp(event_data.get("timestamp"))
        event_type = event_data.get("event")

        # Получаем или создаем сущности
        warehouse = await _get_or_create_warehouse(
            db,
            warehouse_id,
            event_data.get("warehouse_code", f"WH-{str(warehouse_id)[:4]}"),
        )
        product = await _get_or_create_product(db, product_id)

        # Обработка события
        if event_type == "departure":
            return await _process_departure(
                db, movement_id, warehouse, product, quantity, timestamp
            )
        elif event_type == "arrival":
            return await _process_arrival(
                db, movement_id, warehouse, product, quantity, timestamp
            )
        else:
            raise ValueError(f"Unknown event type: {event_type}")
    except Exception as e:
        logger.error(f"Failed to process movement event: {str(e)}", exc_info=True)
        raise


async def _process_departure(
    db: AsyncSession,
    movement_id: UUID,
    warehouse: Warehouse,
    product: Product,
    quantity: int,
    timestamp: datetime,
) -> Movement:
    """Обработка отгрузки товара"""
    # Проверяем остатки
    stock = await _get_stock_item(db, warehouse.id, product.id)
    if stock.quantity < 0 or stock.quantity < quantity:
        raise ValueError(
            f"Insufficient stock. Product: {product.id}, "
            f"Available: {stock.quantity}, Requested: {quantity}"
        )

    # Создаем запись о перемещении
    movement = Movement(
        kafka_movement_id=movement_id,
        source_warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=quantity,
        departure_time=timestamp,
        status=MovementStatus.IN_TRANSIT,
        quantity_diff=None,  # Для departure всегда NULL
    )
    db.add(movement)

    # Обновляем остатки
    stock.quantity -= quantity
    await db.flush()

    stock_cache_key = get_stock_cache_key(warehouse.id, product.id)
    await invalidate_cache(stock_cache_key)

    logger.info(
        f"Processed departure. Movement: {movement_id}, "
        f"Warehouse: {warehouse.id}, Quantity: {quantity}"
    )
    return movement


async def _process_arrival(
    db: AsyncSession,
    movement_id: UUID,
    warehouse: Warehouse,
    product: Product,
    quantity: int,
    timestamp: datetime,
) -> Movement:
    """Обработка поступления товара"""
    # 1. Находим соответствующую отгрузку (departure)
    try:
        stmt = select(Movement).where(
            (Movement.kafka_movement_id == movement_id)
            & (Movement.status == MovementStatus.IN_TRANSIT)
        )
        result = await db.execute(stmt)
        departure_movement = result.scalar_one_or_none()

        # 2. Рассчитываем расхождение (только если есть departure)
        qty_diff = (departure_movement.quantity - quantity) if departure_movement else 0
        movement_updated = False

        # 3. Обновляем/создаем запись
        if departure_movement:
            # Проверяем, что arrival пришел на другой склад
            if departure_movement.source_warehouse_id == warehouse.id:
                raise ValueError(
                    "Arrival warehouse must differ from departure warehouse"
                )
            # Обновляем существующую запись
            departure_movement.destination_warehouse_id = warehouse.id
            departure_movement.arrival_time = timestamp
            departure_movement.status = MovementStatus.COMPLETED
            departure_movement.quantity_diff = qty_diff  # Фиксация расхождения
            movement = departure_movement  # 0 для прямых поставок
            movement_updated = True
        else:
            # Создаем новую запись (если не было departure)
            movement = Movement(
                kafka_movement_id=movement_id,
                destination_warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=quantity,
                arrival_time=timestamp,
                status=MovementStatus.COMPLETED,
                quantity_diff=0,
            )
            db.add(movement)

        # Обновляем остатки
        stock = await _get_stock_item(db, warehouse.id, product.id)
        stock.quantity += quantity
        await db.flush()

        # Инвалидация кэша остатков
        stock_cache_key = get_stock_cache_key(warehouse.id, product.id)
        keys_to_invalidate = [stock_cache_key]

        # Если arrival обновил существующий movement, инвалидируем его кэш тоже
        # Исходя из кода get_movement, API принимает movement.id (внутренний ID).
        if movement_updated:
            movement_cache_key = get_movement_cache_key(movement.id)
            keys_to_invalidate.append(movement_cache_key)

        await invalidate_cache(*keys_to_invalidate)

        logger.info(
            f"Processed arrival. Movement: {movement_id}, "
            f"Warehouse: {warehouse.id}, Quantity: {quantity}"
        )
        return movement
    except Exception as e:
        logger.error(f"Arrival processing failed: {str(e)}", exc_info=True)
        raise


async def _get_stock_item(
    db: AsyncSession, warehouse_id: UUID, product_id: UUID
) -> StockItem:
    """Получаем или создаем запись об остатках"""
    stmt = select(StockItem).where(
        (StockItem.warehouse_id == warehouse_id) & (StockItem.product_id == product_id)
    )
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()

    if not stock:
        stock = StockItem(warehouse_id=warehouse_id, product_id=product_id, quantity=0)
        db.add(stock)
        await db.flush()

    return stock


async def _get_or_create_warehouse(
    db: AsyncSession, warehouse_id: UUID, code: str = None
) -> Warehouse:
    """Получаем или создаем склад"""
    warehouse = await db.get(Warehouse, warehouse_id)
    if not warehouse:
        code = code or f"WH-{str(warehouse_id)[:4]}"
        warehouse = Warehouse(id=warehouse_id, code=code)
        db.add(warehouse)
        await db.flush()
    return warehouse


async def _get_or_create_product(db: AsyncSession, product_id: UUID) -> Product:
    """Получаем или создаем товар"""
    product = await db.get(Product, product_id)
    if not product:
        product = Product(id=product_id)
        db.add(product)
        await db.flush()
    return product


def _validate_uuid(value: str, field_name: str) -> UUID:
    """Валидация UUID"""
    if not value:
        raise ValueError(f"Missing required field: {field_name}")
    try:
        return UUID(str(value))
    except ValueError as e:
        raise ValueError(f"Invalid UUID format for {field_name}: {value}") from e


def _validate_quantity(value: int) -> int:
    """Валидация количества"""
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Quantity must be positive integer, got: {value}")
    return value


def _validate_timestamp(value: str) -> datetime:
    """Валидация временной метки"""
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid timestamp format: {value}") from e
