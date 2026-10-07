"""Twynity discovery and project-scoped fal.ai configuration routes."""

from fastmcp import FastMCP
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.auth import get_identity_from_headers
from app.config import settings
from app.connection_store import get_active_store


def register_routes(mcp: FastMCP) -> None:
    @mcp.custom_route("/api/v1/.well-known/mcp.json", methods=["GET"])
    async def manifest(request: Request) -> JSONResponse:
        return JSONResponse({
            "name": settings.APP_TITLE,
            "base_url": f"{settings.PUBLIC_URL.rstrip('/')}/mcp",
            "version": settings.APP_VERSION,
            "external_connections": {"project": {"name": "fal_configuration"}},
        })

    @mcp.custom_route("/api/v1/schema", methods=["GET"])
    async def configuration_schema(request: Request) -> JSONResponse:
        return JSONResponse({
            "name": "fal_configuration",
            "endpoint": "/api/v1/configuration",
            "method": "POST",
            "schema": {"name": "string", "api_key": "string"},
        })

    @mcp.custom_route("/api/v1/configuration", methods=["OPTIONS"])
    async def configuration_options(request: Request) -> JSONResponse:
        return JSONResponse({}, headers={"Allow": "GET, POST, OPTIONS"})

    @mcp.custom_route("/api/v1/configuration", methods=["POST"])
    async def save_configuration(request: Request) -> JSONResponse:
        identity = await get_identity_from_headers(request.headers)
        try:
            payload = await request.json()
        except (ValueError, UnicodeDecodeError) as exc:
            raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise HTTPException(status_code=422, detail="Request body must be a JSON object")

        name = str(payload.get("name", "fal.ai")).strip() or "fal.ai"
        api_key = payload.get("api_key")
        if not isinstance(api_key, str) or not api_key.strip():
            raise HTTPException(status_code=422, detail="api_key is required")
        if len(api_key) > 4096 or len(name) > 120:
            raise HTTPException(status_code=422, detail="Configuration value is too long")

        store = get_active_store()
        if store is None:
            raise HTTPException(status_code=503, detail="Credential storage is unavailable")
        await store.save(
            identity.user_id,
            identity.persona_id,
            {"name": name, "api_key": api_key.strip()},
        )
        return JSONResponse({"configured": True})

    @mcp.custom_route("/api/v1/configuration", methods=["GET"])
    async def get_configuration(request: Request) -> JSONResponse:
        identity = await get_identity_from_headers(request.headers)
        store = get_active_store()
        if store is None:
            raise HTTPException(status_code=503, detail="Credential storage is unavailable")
        metadata = await store.public_metadata(identity.user_id, identity.persona_id)
        items = [metadata] if metadata else []
        return JSONResponse({"items": items, "item_count": len(items), "next_cursor": None})

    @mcp.custom_route("/api/v1/external-connection/me", methods=["GET"])
    async def connection_status(request: Request) -> JSONResponse:
        identity = await get_identity_from_headers(request.headers)
        store = get_active_store()
        if store is None:
            raise HTTPException(status_code=503, detail="Credential storage is unavailable")
        connected = await store.public_metadata(identity.user_id, identity.persona_id) is not None
        return JSONResponse({"connected": connected})

    @mcp.custom_route("/api/v1/health", methods=["GET"])
    async def health_status(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})
