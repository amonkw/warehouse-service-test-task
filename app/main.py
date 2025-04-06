import asyncio

from fastapi import FastAPI

from app.api.v1.endpoints import movements, stock, kafka, admin
from app.db.session import create_db_async
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

app.include_router(movements.router, prefix="/api/v1/movements", tags=["movements"])
app.include_router(stock.router, prefix="/api/v1/warehouse", tags=["warehouse"])
app.include_router(kafka.router, prefix="/api/v1/kafka", tags=["kafka"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


def create_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db_async())
