"""Optional Twynity license activation and periodic verification."""

import asyncio
import os
import signal
import uuid
from logging import getLogger

import httpx
from jose import JWTError, jwt

from app.config import settings

logger = getLogger(__name__)


def _device_id() -> str:
    return f"{uuid.getnode():012x}"


async def _validate_license() -> bool:
    base_url = settings.LICENSE_SERVER_BASE_URL.rstrip("/")
    jwks_url = f"{base_url}/{settings.LICENSE_SERVER_JWKS_ENDPOINT.lstrip('/')}"
    activation_url = f"{base_url}/{settings.LICENSE_SERVER_ACTIVATION_ENDPOINT.lstrip('/')}"
    payload = {
        "device_id": _device_id(),
        "license_key": settings.LICENSE_KEY,
        "service_id": settings.SERVICE_ID,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(activation_url, json=payload)
        response.raise_for_status()
        activation = response.json()
        if not isinstance(activation, dict):
            return False
        token = activation.get("activation_token")
        if not isinstance(token, str) or not token:
            return False
        jwks_response = await client.get(jwks_url)
        jwks_response.raise_for_status()

    try:
        jwks_document = jwks_response.json()
        if not isinstance(jwks_document, dict) or not isinstance(jwks_document.get("keys"), list):
            return False
        header = jwt.get_unverified_header(token)
        key = next(
            item for item in jwks_document["keys"]
            if item.get("kid") == header.get("kid")
        )
        claims = jwt.decode(token, key, algorithms=["RS256"])
    except (JWTError, KeyError, StopIteration, ValueError):
        return False
    return (
        claims.get("service_id") == settings.SERVICE_ID
        and claims.get("device_id") == _device_id()
    )


async def license_watcher(interval_seconds: float = 86400, max_failures: int = 14) -> None:
    """Allow a two-week outage window, then stop an unlicensed service."""
    failures = 0
    while True:
        try:
            if await _validate_license():
                failures = 0
                logger.info("License check passed")
            else:
                failures += 1
                logger.warning("License check failed (%s/%s)", failures, max_failures)
        except Exception as exc:
            failures += 1
            logger.warning(
                "License service unavailable (%s/%s): %s", failures, max_failures, type(exc).__name__
            )
        if failures >= max_failures:
            logger.critical("Maximum license validation failures reached; stopping service")
            os.kill(os.getpid(), signal.SIGTERM)
            return
        await asyncio.sleep(interval_seconds)
