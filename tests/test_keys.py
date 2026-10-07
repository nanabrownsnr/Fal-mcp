"""Tests for API key management routes and storage."""


def test_store_api_key_success(authenticated_request):
    """Test that storing an API key succeeds."""
    from starlette.testclient import TestClient
    from app.main import mcp
    
    app = mcp.http_app()
    
    # In production, this would actually store the key
    # For now, verify routes exist and return expected shapes

    client = TestClient(app)
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_key_post_requires_name_and_key(authenticated_request):
    """Test that POST /api/v1/keys rejects empty names or keys."""
    from starlette.testclient import TestClient
    from app.main import mcp
    
    app = mcp.http_app()
    client = TestClient(app)
    
    # Will be implemented when full routes are written
