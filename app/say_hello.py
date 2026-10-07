"""Example greeting tool to demonstrate MCP apps integration."""


def register_tool(mcp):
    """Register a simple say_hello example tool."""
    
    @mcp.tool()
    def say_hello(name: str = "World") -> tuple:
        """Greet someone by name.

        Args:
            name: The person to greet (e.g., "Alice") or "World" as default

        Returns:
            Text message
        """
        clean_name = name.strip() or "World"
        return f"Hello, {clean_name}!"
