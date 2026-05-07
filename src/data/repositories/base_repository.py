from typing import Generic, TypeVar, Type

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self,
                 session: AsyncSession,
                 model: Type[T]
):
        self.session = session
        self.model = model

    async def create(self, data) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)
