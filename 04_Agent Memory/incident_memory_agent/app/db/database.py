from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import DB_URL

engine = create_async_engine(DB_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


if __name__ == "__main__":
    import asyncio

    async def check_connection() -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            print("Connected. SELECT 1 ->", result.scalar())

    asyncio.run(check_connection())
