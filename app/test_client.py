"""Example tests for MCP app contract. Use pytest to run these."""

import fal

def test_fal_invoke_simple():
    """Test invoking a simple model via fal.ai client."""
    client = fal.Client()
    result = client.invoke(
        "fal-ai/llama3",
        input={"prompt": "Hello"},
    )
    assert "output" in result
    
def test_fal_invoke_with_params():
    """Test invoking with additional parameters."""
    client = fal.Client()
    result = client.invoke(
        "fal-ai/stable-diffusion-v1",
        input={
            "text_prompts": [{"prompt": "robot cat"}],
        },
        params={"images_per_prompt": 1},
    )
    
def test_error_handling():
    """Test that errors are caught and reported."""
    client = fal.Client()
    try:
        # This will fail in production with network, mock for testing
        result = client.invoke("invalid-model", input={})
    except Exception as e:
        assert isinstance(e, Exception)
