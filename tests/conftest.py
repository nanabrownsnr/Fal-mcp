"""Pytest fixtures for Fal MCP tests."""

import pytest


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
