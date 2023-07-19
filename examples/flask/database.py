from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

_engine = create_async_engine('sqlite+aiosqlite:///heroes.db')


async def init_db(engine=_engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def Session(engine=_engine) -> AsyncSession:
    _session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with _session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
