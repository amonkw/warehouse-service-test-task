import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints import movements, stock, kafka_webhook, admin
from app.db.session import create_db_async
from app.config import settings
from app.services.kafka_consumer import run_consumer
from app.services.redis import get_redis_client, redis_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""

    await get_redis_client()

    consumer_task = None
    if settings.APP_MODE == "kafka":
        consumer_task = asyncio.create_task(run_consumer())
        logger.info("Kafka consumer started")

    yield

    if settings.APP_MODE == "kafka":
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Kafka consumer stopped")

    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed.")


app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan
)

app.include_router(movements.router, prefix="/api/v1/movements", tags=["movements"])
app.include_router(stock.router, prefix="/api/v1/warehouse", tags=["warehouse"])
app.include_router(kafka_webhook.router, prefix="/api/v1/kafka", tags=["Kafka Webhook"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


def create_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db_async())
