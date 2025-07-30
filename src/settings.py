"""Configuration settings for the web scraping MCP server."""

from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ScrapingBee API configuration
    scrapingbee_api_key: Annotated[str, Field(description="ScrapingBee API key", alias="SCRAPINGBEE_API_KEY")] = ""

    # Server configuration
    server_host: Annotated[str, Field(description="Server host", alias="SERVER_HOST")] = "localhost"
    server_port: Annotated[int, Field(description="Server port", alias="SERVER_PORT")] = 8000

    # Scraping configuration
    default_concurrency: Annotated[int, Field(description="Default concurrency for scraping requests", alias="DEFAULT_CONCURRENCY")] = 5
    default_timeout: Annotated[float, Field(description="Default timeout for scraping requests in seconds", alias="DEFAULT_TIMEOUT")] = 90.0

    # Logging configuration
    log_level: Annotated[str, Field(description="Logging level", alias="LOG_LEVEL")] = "INFO"

    # User agent configuration
    default_user_agent: Annotated[str, Field(description="Default user agent string", alias="DEFAULT_USER_AGENT")] = "Mozilla/5.0 (compatible; WebScrapingMCPServer/1.0)"


# Global settings instance
settings = Settings()
