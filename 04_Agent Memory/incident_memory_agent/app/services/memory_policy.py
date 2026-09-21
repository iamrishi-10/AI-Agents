from openai import AsyncOpenAI

from app.config.settings import LLM_MODEL, OPENAI_KEY
from app.db.models import Memory
from app.schemas.memory import MemoryDecision

client = AsyncOpenAI(api_key=OPENAI_KEY)

INSTRUCTIONS = (
    "You are a memory-management policy for an AI agent's long-term memory store. "
    "Given a candidate memory and a list of existing similar memories, decide exactly "
    "one action:\n\n"
    "INSERT - the candidate is useful, new, durable information not already captured.\n"
    "IGNORE - the candidate is a duplicate, trivial, speculative, temporary, or "
    "otherwise not worth storing.\n"
    "SUPERSEDE - the candidate conflicts with or replaces one of the existing active "
    "memories; you must set supersede_memory_id to that memory's id.\n\n"
    "Only choose SUPERSEDE if one of the listed existing memories should actually be "
    "replaced. If action is SUPERSEDE, supersede_memory_id must match one of the "
    "provided existing memory IDs.\n\n"
    "Do not store hypotheses, guesses, or unconfirmed incident diagnoses as durable "
    "memories. Only confirmed facts, confirmed resolutions, stable preferences, or "
    "reusable procedures are eligible for INSERT or SUPERSEDE.\n\n"
    "Always explain your decision in `reason`."
)


def _format_similar_memories(similar_memories: list[Memory]) -> str:
    if not similar_memories:
        return "(none)"

    return "\n".join(
        f"- id={memory.id} | type={memory.memory_type} | status={memory.status} | "
        f"content={memory.content!r}"
        for memory in similar_memories
    )


async def decide_memory_action(
    candidate_content: str,
    similar_memories: list[Memory],
) -> MemoryDecision:
    """Ask the LLM whether to insert, ignore, or supersede, given existing similar memories."""
    prompt = (
        f"Candidate memory:\n{candidate_content!r}\n\n"
        f"Existing similar memories:\n{_format_similar_memories(similar_memories)}"
    )

    response = await client.responses.parse(
        model=LLM_MODEL,
        instructions=INSTRUCTIONS,
        input=prompt,
        text_format=MemoryDecision,
    )

    return response.output_parsed
