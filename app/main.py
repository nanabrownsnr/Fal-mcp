"""Compose FastMCP app with tools and routes."""

import os
from fal import Client
from fastmcp import FastMCP
from pymongo import AsyncMongoClient


async def app_lifespan(server):
    """Initialize database connection for credential storage with graceful fallback."""
    from app.config import settings
    
    # Try to connect to MongoDB, but don't fail if unavailable
    mongouri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    if len(mongouri.strip()) > 0 and "mongodb://" in mongouri.lower():
        try:
            mongo = AsyncMongoClient(mongouri, tz_aware=True)
            
            # Initialize connection store on startup  
            from app.connection_store import ConnectionStore, set_active_store
            
            db_name = settings.DATABASE_NAME.replace("_keys", "") or "fal_mcp_key"
            
            # Extract DB name from MONGODB_URI if it has / after mongodb://
            actual_db_from_uri = mongouri.split("/", 3)[-1] if "/" in mongouri else db_name
            
            store = ConnectionStore(
                mongo[actual_db_from_uri],
                os.getenv("ENCRYPTION_KEY", "fallback_key")
            )
            await store.setup()
            set_active_store(store)
            
        except Exception as e:
            import logging
            logging.warning(f"MongoDB unavailable on startup (Atlas not ready): {e}")

    yield


# Cleanup is handled in lifespan - app runs even if MongoDB setup fails
    


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
