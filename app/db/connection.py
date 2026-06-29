import os
from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

@asynccontextmanager
async def get_checkpointer():
    """
    Async version - needed because our agent nodes use async (httpx calls).
    Use with 'async with', e.g.:
    
        async with get_checkpointer() as checkpointer:
            app = graph.compile(checkpointer=checkpointer)
    """
    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        await checkpointer.setup()
        yield checkpointer