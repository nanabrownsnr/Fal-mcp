"""Helper module to call fal.ai's Model API."""

from fal import Client

class FalApiClient:
    """Client for interacting with fal.ai endpoint."""
    
    def __init__(self, client=None):
        self.client = client or fal.Client()
    
    async def invoke(self, model_id: str, **kwargs) -> dict:
        """Invoke a model via fal.ai.
        
        Args:
            model_id: The model identifier (e.g., 'fal-ai/llama3')
            kwargs: Model-specific inputs
            
        Returns:
            Model output or error message
        """
        try:
            result = self.client.invoke(
                model=model_id,
                input=kwargs.get("input", {}),
                params=kwargs.get("params", {}),
            )
            return {"success": True, "output": str(result.get("output", ""))}
        except Exception as e:
            return {"success": False, "error": str(e)}
