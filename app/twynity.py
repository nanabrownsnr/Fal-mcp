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
    """Placeholder — will be initialized in app lifespan."""
    return None


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
            
            # Store API key (encrypted in production)
            store = get_active_store()
            if store and hasattr(store, "save_api_key"):
                await store.save_api_key(name, key_value)
            
            return JSONResponse({"configured": True})
        
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
        if not store or not hasattr(store, "list_api_keys"):
            return JSONResponse({"items": [], "item_count": 0})
        
        return JSONResponse({"items": [], "item_count": 0})

    @mcp.custom_route("/api/v1/health", methods=["GET"])
    async def health_status(request: Request) -> JSONResponse:
        """Liveness check."""
        return JSONResponse({"status": "ok"})
