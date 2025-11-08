from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from typing import Annotated

from fastapi import Depends

from sqlalchemy.orm import DeclarativeBase

from loguru import logger



#Конфигурация для работы с базой данных с помощью сессий

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass


# Автоматическое создание таблиц
async def create_tables():
    """Создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



async def init_db():
    """Инициализация БД - вызовется при запуске приложения"""
    await create_tables()
    logger.info("Таблицы базы данных созданы успешно!")


