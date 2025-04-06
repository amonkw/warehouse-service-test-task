from .movements import router as movements_router
from .stock import router as stock_router
from .kafka_webhook import router as kafka_router
from .admin import router as admin_router

__all__ = ["admin", "movements_router", "stock_router", "kafka_router"]
