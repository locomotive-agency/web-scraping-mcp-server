"""Scraping service using ScrapingBee."""

from typing import Any

from loguru import logger

try:
    from .scrapingbee import ScrapingBeeClient
    from .scrapingbee.exceptions import ScrapingBeeError
    from .settings import settings
except ImportError:
    from scrapingbee import ScrapingBeeClient
    from settings import settings


class ScrapingService:
    """Service for scraping HTML content using ScrapingBee."""

    def __init__(self):
        """Initialize the scraping service."""
        self._client: ScrapingBeeClient | None = None

    async def _get_client(self) -> ScrapingBeeClient:
        """Get or create the ScrapingBee client."""
        if self._client is None:
            if not settings.scrapingbee_api_key:
                raise ValueError(
                    "SCRAPINGBEE_API_KEY is required. Please set it as an environment variable."
                )
            self._client = ScrapingBeeClient(
                api_key=settings.scrapingbee_api_key,
                concurrency=settings.default_concurrency,
            )
        return self._client

    async def close(self) -> None:
        """Close the scraping service and cleanup resources."""
        if self._client:
            await self._client.close()
            self._client = None

    async def fetch_html(
        self,
        url: str,
        render_js: bool = False,
        user_agent: str | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> str:
        """Fetch HTML content from a single URL.

        Args:
            url: URL to scrape
            render_js: Whether to render JavaScript
            user_agent: Custom user agent string
            custom_headers: Additional headers to send

        Returns:
            HTML content as string

        Raises:
            ScrapingBeeError: If the request fails
        """
        client = await self._get_client()

        # Use default user agent if none provided
        if user_agent is None:
            user_agent = settings.default_user_agent

        logger.info(f"Fetching HTML from: {url}")
        return await client.get(
            url=url,
            render_js=render_js,
            user_agent=user_agent,
            custom_headers=custom_headers,
        )

    async def fetch_html_batch(
        self,
        urls: list[str],
        render_js: bool = False,
        user_agent: str | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch HTML content from multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            render_js: Whether to render JavaScript
            user_agent: Custom user agent string
            custom_headers: Additional headers to send

        Returns:
            List of results with 'url', 'success', 'content', and 'error' keys
        """
        client = await self._get_client()

        # Use default user agent if none provided
        if user_agent is None:
            user_agent = settings.default_user_agent

        logger.info(f"Fetching HTML from {len(urls)} URLs")
        return await client.get_batch(
            urls=urls,
            render_js=render_js,
            user_agent=user_agent,
            custom_headers=custom_headers,
        )


# Global scraping service instance
scraping_service = ScrapingService()
