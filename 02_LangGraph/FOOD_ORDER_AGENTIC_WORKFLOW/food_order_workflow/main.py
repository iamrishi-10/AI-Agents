"""Entry point for the food order agentic workflow backend."""
import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.orders import router as orders_router
from db.checkpoint import get_checkpointer
from workflows.order.graph import build_order_graph

if sys.platform == "win32":
    # psycopg's async driver cannot run on Windows' default ProactorEventLoop.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with get_checkpointer() as checkpointer:
        await checkpointer.setup()
        app.state.checkpointer = checkpointer
        app.state.order_graph = build_order_graph(checkpointer)
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(orders_router)


@app.get("/")
async def root():
    return {"message": "Food Order Agentic Workflow API is running."}


@app.get("/health")
async def health():
    return {"status": "healthy"}