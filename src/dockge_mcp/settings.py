import os
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Manages application configuration using Pydantic."""

    model_config = SettingsConfigDict(
        env_file=[os.path.expanduser("~/.mcp-env"), ".env"],
        extra="ignore",
    )

    # URL for the Dockge server
    dockge_url: AnyHttpUrl = "http://192.168.0.2:5001"

    # API Token for Dockge Enhanced REST API
    dockge_api_token: str | None = None

    # Credentials for Dockge Socket.IO (optional/fallback)
    dockge_username: str | None = None
    dockge_password: str | None = None

    # Transport mode: stdio (default for MCP agents) or http
    mcp_transport: str = "stdio"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000


# Create a single, reusable instance of the settings
settings = Settings()
