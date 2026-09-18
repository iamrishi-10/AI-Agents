import asyncio

from app.db.database import Base, engine
from app.db import models  # noqa: F401 - import registers Memories on Base.metadata


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"Tables created: {list(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    asyncio.run(init_models())
