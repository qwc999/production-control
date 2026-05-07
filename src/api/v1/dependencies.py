from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker
from src.domain.services.batch_service import BatchService


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_batch_service(
        session: AsyncSession = Depends(get_db)
) -> BatchService:
    return BatchService(session)
