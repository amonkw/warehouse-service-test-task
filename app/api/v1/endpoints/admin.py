from typing import Optional, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session_dependency

router = APIRouter(include_in_schema=False)


class ServiceVersionAnswer(BaseModel):
    version: str
    is_autotest: Optional[bool]


OkAnswer = Literal["OK"]


@router.get("/service_version", include_in_schema=False)
async def service_version() -> ServiceVersionAnswer:
    return ServiceVersionAnswer(
        version=settings.VERSION, is_autotest="_autotest_" in settings.database_url
    )


@router.get("/liveness", include_in_schema=False)
async def liveness() -> OkAnswer:
    return "OK"


@router.get("/readiness", include_in_schema=False)
async def readiness(
    session: AsyncSession = Depends(get_session_dependency),
) -> OkAnswer:
    (await session.execute(text("SELECT 1;"))).scalars()
    return "OK"
