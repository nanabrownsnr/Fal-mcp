"""Twynity JWT verification and project/persona identity resolution."""

import asyncio
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx
from fastmcp.server.auth.providers.jwt import JWTVerifier
from jose import JWTError, jwt
from starlette.exceptions import HTTPException

from app.config import settings


@dataclass(frozen=True)
class AuthenticatedIdentity:
    user_id: str
    persona_id: str


_jwks: list[dict[str, Any]] = []
_jwks_expires_at = 0.0
_jwks_lock = asyncio.Lock()


def get_auth_provider() -> JWTVerifier:
    """Protect the MCP transport with the account service's signing keys."""
    return JWTVerifier(
        jwks_uri=settings.account_jwks_url,
        algorithm="RS256",
    )


async def _get_jwks() -> list[dict[str, Any]]:
    global _jwks, _jwks_expires_at
    if _jwks and time.monotonic() < _jwks_expires_at:
        return _jwks
    async with _jwks_lock:
        if _jwks and time.monotonic() < _jwks_expires_at:
            return _jwks
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(settings.account_jwks_url)
            response.raise_for_status()
        keys = response.json().get("keys")
        if not isinstance(keys, list):
            raise ValueError("JWKS response does not contain a keys list")
        _jwks = keys
        _jwks_expires_at = time.monotonic() + settings.ACCOUNT_SERVICE_JWKS_CACHE_TTL
        return _jwks


async def get_identity_from_headers(headers: Mapping[str, str]) -> AuthenticatedIdentity:
    """Verify bearer JWT and require the trusted active persona header."""
    normalized = {key.lower(): value for key, value in headers.items()}
    authorization = normalized.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    persona_id = normalized.get(settings.PERSONA_ID_HEADER.lower(), "").strip()
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="A valid bearer token is required")
    if not persona_id:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required {settings.PERSONA_ID_HEADER} header",
        )

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        key = next(item for item in await _get_jwks() if item.get("kid") == kid)
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.SERVICE_ID,
        )
    except (httpx.HTTPError, JWTError, KeyError, StopIteration, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Bearer token could not be verified") from exc

    user_id = claims.get("id") or claims.get("sub")
    if not isinstance(user_id, str) or not user_id.strip():
        raise HTTPException(status_code=401, detail="Verified token has no user identity")
    return AuthenticatedIdentity(user_id=user_id, persona_id=persona_id)
