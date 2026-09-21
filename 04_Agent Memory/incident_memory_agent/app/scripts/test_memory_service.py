import asyncio

from sqlalchemy import delete, select

from app.db.database import AsyncSessionLocal
from app.db.models import Memory
from app.services.embedding_service import embed_query
from app.services.memory_service import retrieve_memories, store_memory

USER_ID = "test-user"
SERVICE_NAME = "test-service"
CONTENT = "The user's preferred timezone is IST (UTC+5:30)."
QUERY = "What timezone does the user prefer?"


async def main() -> None:
    # Clear leftover rows from previous runs so this test is repeatable.
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Memory).where(
                Memory.user_id == USER_ID, Memory.service_name == SERVICE_NAME
            )
        )
        await session.commit()

    async with AsyncSessionLocal() as session:
        memory = await store_memory(
            session,
            user_id=USER_ID,
            service_name=SERVICE_NAME,
            memory_type="semantic",
            content=CONTENT,
        )
        print(f"Stored memory id={memory.id} content={memory.content!r}")

    async with AsyncSessionLocal() as session:
        results = await retrieve_memories(
            session,
            user_id=USER_ID,
            service_name=SERVICE_NAME,
            query=QUERY,
            top_k=3,
        )

        found = memory.id in [m.id for m in results]
        print(f"Retrieved {len(results)} memories, target present: {found}")
        for m in results:
            print(f"  id={m.id} content={m.content!r}")

        assert found, "Stored memory was not retrieved back."

    # Inspect the raw cosine distance directly (not exposed by retrieve_memories yet)
    async with AsyncSessionLocal() as session:
        query_embedding = embed_query(QUERY)
        distance = Memory.embedding.cosine_distance(query_embedding).label("distance")

        stmt = select(Memory, distance).where(Memory.id == memory.id)
        row = (await session.execute(stmt)).one()

        retrieved_memory, distance_value = row
        print(f"Cosine distance for id={retrieved_memory.id}: {distance_value:.6f}")


if __name__ == "__main__":
    asyncio.run(main())
