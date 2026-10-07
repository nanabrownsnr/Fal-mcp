"""JWT verification for Twynity-deployed Fal MCP."""

from dataclasses import dataclass
from starlette.requests import Request
from starlette.exceptions import HTTPException
from typing import Mapping


@dataclass(frozen=True)
class AuthenticatedIdentity:
    """Verified user identity from JWT token."""
    user_id: str
    persona_id: Optional[str] = None
