from uuid import UUID

from sqlmodel import delete, select, update

from .cache import cache
from .database import Session
from .log import logger
from .models import Hero
from .schemas import HeroUpdate, Filter


@cache.clear(namespaces=['hero'])
async def create_hero(body: Hero) -> Hero:
    logger.debug('Create Hero')
    async with Session() as session:
        session.add(body)
        await session.commit()
    return body


@cache(ttl=60, namespace='hero')
async def read_hero() -> list[Hero]:
    logger.debug('Read')
    async with Session() as session:
        result = await session.execute(select(Hero))
        heroes = result.scalars().all()
    return heroes


@cache(ttl=60, namespace='hero')
async def read_hero_filter(body: Filter) -> list[Hero]:
    logger.debug('Read filter')
    query = select(Hero)

    if body.id is not None:
        query = query.where(Hero.id == body.id)
    if body.name is not None:
        query = query.where(Hero.name == body.name)
    if body.secret_name is not None:
        query = query.where(Hero.secret_name == body.secret_name)
    if body.age is not None:
        query = query.where(Hero.age == body.age)

    async with Session() as session:
        result = await session.execute(query)
        heroes = result.scalars().all()
    return heroes


@cache.clear(namespaces=['hero'])
async def update_hero(_id: UUID, body: HeroUpdate) -> Hero:
    logger.debug('Update')

    query = (
        update(Hero)
        .where(Hero.id == _id)
        .values(**body.dict(exclude_none=True))
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()

        result = await session.execute(select(Hero).where(Hero.id == _id))
        hero_updated = result.scalars().one()
    return hero_updated


@cache.clear(namespaces=['hero'])
async def delete_hero(_id: UUID):
    logger.debug('Delete')

    async with Session() as session:
        await session.execute(delete(Hero).where(Hero.id == _id))
        await session.commit()
