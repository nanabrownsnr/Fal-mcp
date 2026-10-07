"""Configure Fal MCP environment and logging."""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


def configured_mcp_name():
    """Return default service name until customizing."""
    name = os.getenv("FAL_MCP_NAME", "starter").strip() or "starter"
    return "fal-mcp" if not name else name


def configure_logging():
    """Set up logging to files and console."""
    from datetime import date
    os.makedirs("./logs", exist_ok=True)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    log_file = f"./logs/{configured_mcp_name()}_{date.today().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


class Settings(BaseSettings):
    """Environment settings for Fal MCP server."""
    
    SERVICE_ID: str = (f"{configured_mcp_name()}_dev" if not os.getenv("ENVIRONMENT")
                      else f"{configured_mcp_name()}_{os.getenv('ENVIRONMENT', 'development')}")
    APP_TITLE: str = "Fal MCP Server - AI Models"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    ALLOWED_ORIGINS: str = "*"

    # Fal client endpoint  
    PUBLIC_URL: str = os.getenv(
        "PUBLIC_URL",
        f"http://localhost:{os.getenv('PORT', '8000')}"
    )
    
    # MongoDB storage for keys - accepts both DATABASE_NAME and MONGODB_DATABASE env vars
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", os.getenv("MONGODB_DATABASE", "fal_mcp_keys"))
    ENCRYPTION_KEY: str

    # Optional reporting (replace with your endpoint)
    USAGE_REPORT_ENDPOINT: str = os.getenv("USAGE_REPORT_ENDPOINT", "")
    
    @property
    def service_short(self) -> str:
        """Return short name for API calls."""
        return self.APP_TITLE.replace(" ", "-").lower()


settings = Settings()

configure_logging()
