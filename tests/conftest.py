"""Pytest fixtures for Fal MCP tests."""

import os

import pytest

# Keep module imports deterministic without connecting to production services.
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("ACCOUNT_SERVICE_URL", "https://account.invalid")
os.environ.setdefault(
    "ENCRYPTION_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
)


@pytest.fixture
def authenticated_request():
    """Mock authenticated request with JWT and Persona-Id headers."""
    return {
        "headers": {
            "authorization": "Bearer test-token-from-account-service",
            "Persona-Id": "test-persona-id",
        }
    }


@pytest.fixture
def unauthenticated_request():
    """Mock unauthenticated request (for health checks, etc.)."""
    return {}


@pytest.fixture
async def mongo_client(mocker):
    """Fixture to mock MongoDB client for testing without DB setup."""
    mock_db = mocker.MagicMock()
    await mock_db.update_one.return_value.upserted_id = None
    
    return mock_db
