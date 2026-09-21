from pydantic import BaseModel, Field
from typing import Literal


class MemoryDecision(BaseModel):
    action: Literal["insert", "ignore", "supersede"]
    memory_type: Literal["semantic", "episodic", "procedural"]
    content: str
    importance: float = Field(le=1, ge=0)
    reason: str
    supersede_memory_id: int | None = None