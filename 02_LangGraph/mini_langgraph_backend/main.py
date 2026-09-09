"""Entry point for the mini LangGraph backend."""
from fastapi import FastAPI

from api.refunds import router as refunds_router

app = FastAPI()

app.include_router(refunds_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the mini LangGraph backend!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
