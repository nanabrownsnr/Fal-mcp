"""Compose FastMCP app with tools and routes."""

import os
from fal import Client
from fastmcp import FastMCP
from pymongo import AsyncMongoClient


async def app_lifespan(server):
    """Initialize database connection for credential storage."""
    from app.config import settings
    
    mongo = AsyncMongoClient(
        os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        tz_aware=True
    )
    
    # Initialize connection store on startup  
    from app.connection_store import ConnectionStore, set_active_store
    
    if len(os.getenv("MONGODB_URI", "").strip()) > 0:
        store = ConnectionStore(
            mongo[settings.DATABASE_NAME.replace("_keys", "")],
            os.getenv("ENCRYPTION_KEY", "fallback_key")
        )
        await store.setup()
        set_active_store(store)
    
    yield
    
    # Cleanup on shutdown
    set_active_store(None)
    if hasattr(mongo, "close"):
        await mongo.close()


# Build FastMCP server  
from app.config import settings

mcp = FastMCP(
    settings.APP_TITLE,
    lifespan=app_lifespan,
)


# Register example tool
import sys
sys.path.insert(0, str(__file__))
from app.say_hello import register_tool as register_greeting
register_greeting(mcp)


# Register HTTP routes for key management
from app.twynity import register_routes
register_routes(mcp)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:mcp", host="0.0.0.0", port=8000)
