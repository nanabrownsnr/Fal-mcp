"""Resolve the decrypted credentials for the authenticated active project."""

from fastmcp.server.dependencies import get_http_headers
from starlette.exceptions import HTTPException

from app.auth import get_identity_from_headers
from app.connection_store import get_active_store


async def get_current_connection() -> dict[str, str]:
    identity = await get_identity_from_headers(get_http_headers())
    store = get_active_store()
    if store is None:
        raise HTTPException(status_code=503, detail="Credential storage is unavailable")
    connection = await store.get(identity.user_id, identity.persona_id)
    if connection is None:
        raise HTTPException(status_code=404, detail="Configure fal.ai credentials first")
    return connection
