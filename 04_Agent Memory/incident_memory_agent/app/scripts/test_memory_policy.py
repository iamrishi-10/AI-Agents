import asyncio

from sqlalchemy import delete, func, select

from app.db.database import AsyncSessionLocal
from app.db.models import Memory
from app.services.memory_service import process_memory_candidate, store_memory


async def _count_memories(session, user_id: str, service_name: str) -> int:
    stmt = select(func.count()).select_from(Memory).where(
        Memory.user_id == user_id,
        Memory.service_name == service_name,
    )
    return (await session.execute(stmt)).scalar_one()


async def _reset_scope(user_id: str, service_name: str) -> None:
    """Delete any leftover rows from previous runs, so tests are repeatable."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Memory).where(
                Memory.user_id == user_id, Memory.service_name == service_name
            )
        )
        await session.commit()


async def test_insert() -> None:
    user_id = "policy-test-insert"
    service_name = "policy-test"

    await _reset_scope(user_id, service_name)

    async with AsyncSessionLocal() as session:
        before = await _count_memories(session, user_id, service_name)

    async with AsyncSessionLocal() as session:
        decision = await process_memory_candidate(
            session,
            user_id,
            service_name,
            "The user's preferred programming language is Python.",
        )

    async with AsyncSessionLocal() as session:
        after = await _count_memories(session, user_id, service_name)

    print(f"[INSERT] decision={decision.action} before={before} after={after}")
    assert decision.action == "insert", f"Expected insert, got {decision.action}"
    assert after == before + 1, f"Expected row count +1, went {before} -> {after}"
    print("[INSERT] PASS")


async def test_ignore() -> None:
    user_id = "policy-test-ignore"
    service_name = "policy-test"
    fact = "The user's timezone is IST (UTC+5:30)."

    await _reset_scope(user_id, service_name)

    async with AsyncSessionLocal() as session:
        await store_memory(
            session,
            user_id=user_id,
            service_name=service_name,
            memory_type="semantic",
            content=fact,
        )

    async with AsyncSessionLocal() as session:
        before = await _count_memories(session, user_id, service_name)

    async with AsyncSessionLocal() as session:
        decision = await process_memory_candidate(session, user_id, service_name, fact)

    async with AsyncSessionLocal() as session:
        after = await _count_memories(session, user_id, service_name)

    print(f"[IGNORE] decision={decision.action} before={before} after={after}")
    assert decision.action == "ignore", f"Expected ignore, got {decision.action}"
    assert after == before, f"Expected row count unchanged, went {before} -> {after}"
    print("[IGNORE] PASS")


async def test_supersede() -> None:
    user_id = "policy-test-supersede"
    service_name = "policy-test"

    await _reset_scope(user_id, service_name)

    async with AsyncSessionLocal() as session:
        old_memory = await store_memory(
            session,
            user_id=user_id,
            service_name=service_name,
            memory_type="semantic",
            content="User prefers IST.",
        )

    async with AsyncSessionLocal() as session:
        decision = await process_memory_candidate(
            session, user_id, service_name, "User now prefers UTC."
        )

    print(
        f"[SUPERSEDE] decision={decision.action} "
        f"supersede_memory_id={decision.supersede_memory_id}"
    )
    assert decision.action == "supersede", f"Expected supersede, got {decision.action}"
    assert decision.supersede_memory_id == old_memory.id, (
        f"Expected supersede_memory_id={old_memory.id}, "
        f"got {decision.supersede_memory_id}"
    )

    async with AsyncSessionLocal() as session:
        stmt = select(Memory).where(
            Memory.user_id == user_id, Memory.service_name == service_name
        )
        rows = (await session.execute(stmt)).scalars().all()

    old_row = next(m for m in rows if m.id == old_memory.id)
    assert old_row.status == "superseded", (
        f"Expected old row superseded, got {old_row.status}"
    )

    new_rows = [m for m in rows if m.id != old_memory.id]
    assert len(new_rows) == 1, f"Expected exactly one new row, got {len(new_rows)}"
    assert new_rows[0].status == "active", (
        f"Expected new row active, got {new_rows[0].status}"
    )

    print("[SUPERSEDE] PASS")


async def main() -> None:
    await test_insert()
    await test_ignore()
    await test_supersede()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
