"""HTTP routes for Fal MCP API key management and health checks."""

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse


def get_identity_from_headers(headers) -> dict:
    """Simplified identity resolver — replace with proper JWT verification if needed."""
    authorization = headers.get("authorization", "")
    persona_id = headers.get("Persona-Id", "")
    
    if "Bearer" not in authorization:
        return {"error": "bearer token required"}
    
    return {
        "user_id": "test-user-from-jwt",  # Will be replaced by proper JWT decoding
        "persona_id": persona_id,
    }


def get_active_store():
    """Return the globally active connection store (set by app lifespan)."""
    from app.connection_store import get_active_store as _get_store
    return _get_store()


def register_routes(mcp):
    """Register Twynity-compatible API key management routes."""

    @mcp.custom_route("/api/v1/.well-known/mcp.json", methods=["GET"])
    async def manifest(request: Request) -> JSONResponse:
        from app.config import settings
        return JSONResponse({
            "name": settings.APP_TITLE.replace(" ", "-"),
            "base_url": f"{settings.PUBLIC_URL.rstrip('/')}/mcp",
            "version": settings.APP_VERSION,
            "external_connections": {"project": {}},
        })

    @mcp.custom_route("/api/v1/keys", methods=["POST"])
    async def create_api_key(request: Request) -> JSONResponse:
        """Store or update an API key for a service."""
        from app.config import settings
        
        identity = get_identity_from_headers(request.headers)
        
        if "error" in identity:
            return JSONResponse(identity, status_code=401)
        
        try:
            payload = await request.json()
            name = str(payload.get("name", "")).strip()
            key_value = str(payload.get("key", "")).strip()
            
            if not name or not key_value:
                return JSONResponse(
                    {"detail": {"missing_fields": ["name", "key"]}}, 
                    status_code=422
                )
            
            # Get active store from global state (set by lifespan)
            store = get_active_store()
            
            if store and hasattr(store, "save_api_key"):
                result = await store.save_api_key(name, key_value)
            
            return JSONResponse({
                "configured": True, 
                "name": name,
                "result": result
            })
        
        except ValueError:
            return JSONResponse(
                {"detail": "Request body must be valid JSON"}, 
                status_code=400
            )

    @mcp.custom_route("/api/v1/keys", methods=["GET"])
    async def list_api_keys(request: Request) -> JSONResponse:
        """List stored API keys (metadata only)."""
        identity = get_identity_from_headers(request.headers)
        
        if "error" in identity:
            return JSONResponse(identity, status_code=401)
        
        store = get_active_store()
        
        if not store or not hasattr(store, "collection"):
            # Return empty list but with metadata available from DB
            try:
                import pymongo
                keys = []
                # Fallback to returning empty with count
                return JSONResponse({"items": [], "item_count": 0})
            
            except Exception as e:
                import logging
                logging.warning(f"Failed to list keys: {e}")
                return JSONResponse({"items": [], "item_count": 0})
        
        # Store has cursor method - use it
        try:
            cursor = await store.collection.find(
                {},
                {"_id": 0, "name": 1, "value": 0}  # Don't expose encrypted values
            )
            
            keys = []
            async for doc in cursor:
                keys.append({
                    "name": doc.get("name", ""),
                    "user_id": doc.get("user_id"),
                    "modified": doc.get("modified"),
                })
            
            return JSONResponse({"items": keys, "item_count": len(keys)})
        except Exception as e:
            import logging
            logging.warning(f"Failed to query collection: {e}")
            return JSONResponse({"items": [], "item_count": 0})

    @mcp.custom_route("/api/v1/keys/{key_name}", methods=["GET"])
    async def get_single_api_key(request: Request) -> JSONResponse:
        """Get a specific API key by name."""
        from app.config import settings
        
        identity = get_identity_from_headers(request.headers)
        
        if "error" in identity:
            return JSONResponse(identity, status_code=401)
        
        store = get_active_store()
        
        if not store or not hasattr(store, "get_api_key"):
            return JSONResponse({"detail": "API key not found or unauthorized"}, status_code=404)
        
        try:
            key_name = str(request.url.path.split("/")[-1])
            result = await store.get_api_key(key_name)
            
            if result:
                return JSONResponse(result, status_code=200)
            
            return JSONResponse({"detail": "API key not found"}, status_code=404)
        
        except Exception as e:
            import logging
            logging.warning(f"Failed to get key {key_name}: {e}")
            return JSONResponse({"detail": f"Error reading key: {e}"}, status_code=500)

    @mcp.custom_route("/api/v1/health", methods=["GET"])
    async def health_status(request: Request) -> JSONResponse:
        """Liveness check."""
        return JSONResponse({"status": "ok"})

    @mcp.custom_route("/api/v1/status", methods=["GET"])
    async def status_check(request: Request) -> JSONResponse:
        """Status with version info and MongoDB availability."""
        from app.config import settings
        
        # Try to check DB connection briefly
        db_ready = True
        try:
            if settings.MONGODB_URI:
                from pymongo import MongoClient
                mongo_uri_clean = settings.MONGODB_URI.replace("mongodb+srv://", "mongodb://")
                test_mongo = MongoClient(mongo_uri_clean, serverSelectionTimeoutMS=100)
                test_mongo.admin.command('ping')
                test_mongo.close()
                db_ready = True
        except Exception as e:
            # Don't fail startup if DB not available - just mark degraded
            logging.debug(f"MongoDB connection check failed (may degrade): {type(e).__name__}")
        
        status = "healthy" if db_ready else "degraded"
        
        return JSONResponse({
            "status": status,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "mongodb_healthy": db_ready,
        })
