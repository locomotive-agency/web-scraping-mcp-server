"""Configuration settings for the web scraping MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    # ScrapingBee API configuration
    scrapingbee_api_key: str = Field(
        default="",
        description="ScrapingBee API key",
        alias="SCRAPINGBEE_API_KEY",
    )

    # Server configuration
    server_host: str = Field(
        default="localhost",
        description="Server host",
        alias="SERVER_HOST",
    )
    server_port: int = Field(
        default=8000,
        description="Server port",
        alias="SERVER_PORT",
    )

    # Scraping configuration
    default_concurrency: int = Field(
        default=5,
        description="Default concurrency for scraping requests",
        alias="DEFAULT_CONCURRENCY",
    )
    default_timeout: float = Field(
        default=90.0,
        description="Default timeout for scraping requests in seconds",
        alias="DEFAULT_TIMEOUT",
    )

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        alias="LOG_LEVEL",
    )

    # User agent configuration
    default_user_agent: str = Field(
        default="Mozilla/5.0 (compatible; WebScrapingMCPServer/1.0)",
        description="Default user agent string",
        alias="DEFAULT_USER_AGENT",
    )


# Global settings instance
settings = Settings()
