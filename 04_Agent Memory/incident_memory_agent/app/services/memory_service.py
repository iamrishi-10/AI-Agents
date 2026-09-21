from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory
from app.schemas.memory import MemoryDecision
from app.services.embedding_service import embed_document, embed_query
from app.services.memory_policy import decide_memory_action


async def store_memory(
    session: AsyncSession,
    user_id: str,
    service_name: str,
    memory_type: str,
    content: str,
    importance: float = 0.5,
) -> Memory:
    """Embed and persist a new memory, returning the fully-refreshed ORM object."""
    embedding = embed_document(content)

    memory = Memory(
        user_id=user_id,
        service_name=service_name,
        memory_type=memory_type,
        content=content,
        importance=importance,
        embedding=embedding,
    )

    session.add(memory)
    await session.commit()
    await session.refresh(memory)

    return memory


async def retrieve_memories(
    session: AsyncSession,
    user_id: str,
    service_name: str,
    query: str,
    top_k: int = 5,
) -> list[Memory]:
    """Return the top_k active memories for this user/service closest to `query`."""
    query_embedding = embed_query(query)

    distance = Memory.embedding.cosine_distance(query_embedding).label("distance")

    stmt = (
        select(Memory, distance)
        .where(
            Memory.user_id == user_id,
            Memory.service_name == service_name,
            Memory.status == "active",
        )
        .order_by(distance)
        .limit(top_k)
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [memory for memory, _distance in rows]


async def process_memory_candidate(
    session: AsyncSession,
    user_id: str,
    service_name: str,
    candidate_content: str,
) -> MemoryDecision:
    """Retrieve similar memories, ask the policy for a decision, then execute it."""
    similar_memories = await retrieve_memories(
        session,
        user_id=user_id,
        service_name=service_name,
        query=candidate_content,
    )

    decision = await decide_memory_action(candidate_content, similar_memories)

    if decision.action == "insert":
        await store_memory(
            session,
            user_id=user_id,
            service_name=service_name,
            memory_type=decision.memory_type,
            content=decision.content,
            importance=decision.importance,
        )

    elif decision.action == "supersede":
        stmt = select(Memory).where(
            Memory.id == decision.supersede_memory_id,
            Memory.user_id == user_id,
            Memory.service_name == service_name,
            Memory.status == "active",
        )
        old_memory = (await session.execute(stmt)).scalar_one_or_none()

        if old_memory is None:
            raise ValueError(
                f"Cannot supersede memory id={decision.supersede_memory_id}: "
                "not found, not active, or does not belong to this user/service."
            )

        old_memory.status = "superseded"

        await store_memory(
            session,
            user_id=user_id,
            service_name=service_name,
            memory_type=decision.memory_type,
            content=decision.content,
            importance=decision.importance,
        )

    # "ignore" -> no DB mutation

    return decision
