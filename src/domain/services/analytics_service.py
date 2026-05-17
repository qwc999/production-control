from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analytics_repo = AnalyticsRepository(session)
