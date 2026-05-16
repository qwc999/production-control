from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from src.core.config import settings


celery_engine = create_async_engine(
    str(settings.database_url),
    poolclass=NullPool
)

celery_async_session_maker = async_sessionmaker(
    bind=celery_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
