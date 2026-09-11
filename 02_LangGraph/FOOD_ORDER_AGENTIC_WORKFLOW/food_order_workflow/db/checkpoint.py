"""Durable Postgres checkpointer for the LangGraph workflow."""
import os

from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

load_dotenv()

DB_URI = os.getenv("DATABASE_URL")

if not DB_URI:
    raise RuntimeError("DATABASE_URL is not configured")

def get_checkpointer():
    """Return the AsyncPostgresSaver async context manager for DB_URI.

    Usage:
        async with get_checkpointer() as checkpointer:
            await checkpointer.setup()

    Keeping this connection alive for the FastAPI app's lifetime (instead of
    a short-lived `async with` block) is handled separately in main.py's
    lifespan, not implemented here yet.
    """
    return AsyncPostgresSaver.from_conn_string(DB_URI)
