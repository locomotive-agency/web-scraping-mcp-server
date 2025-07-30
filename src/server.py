"""Web scraping MCP server using FastMCP and ScrapingBee."""

from collections.abc import Callable
from typing import Annotated, Any

from fastmcp import FastMCP
from loguru import logger
from pydantic import BaseModel, Field, field_validator

import extractors
from scraper import ScrapingService
from scrapingbee.exceptions import ScrapingBeeError

# Initialize FastMCP server
mcp = FastMCP("Web Scraping Server")


# Request models
class UrlRequest(BaseModel):
    """Request model for URL operations."""

    urls: Annotated[
        list[str], Field(min_length=1, description="List of URLs to process")
    ]
    render_js: Annotated[bool, Field(description="Whether to render JavaScript")] = (
        False
    )
    user_agent: Annotated[str | None, Field(description="Custom user agent string")] = (
        None
    )
    custom_headers: Annotated[
        dict[str, str] | None, Field(description="Additional headers to send")
    ] = None

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[str]) -> list[str]:
        """Validate URL formats."""
        if v:
            for url in v:
                if not url.startswith(("http://", "https://")):
                    raise ValueError("Invalid URL format")  # noqa: TRY003
        return v


def create_error_response(url: str, error: Exception) -> dict[str, Any]:
    """Create a standardized error response."""
    # Categorize the error
    if isinstance(error, ScrapingBeeError):
        if "timeout" in str(error).lower():
            error_type = "TIMEOUT_ERROR"
        elif "network" in str(error).lower():
            error_type = "NETWORK_ERROR"
        elif "404" in str(error) or "not found" in str(error).lower():
            error_type = "NOT_FOUND_ERROR"
        else:
            error_type = "API_ERROR"
    else:
        error_type = "PARSING_ERROR"

    return {
        "url": url,
        "success": False,
        "data": None,
        "error": {
            "type": error_type,
            "message": str(error),
        },
    }


def create_success_response(
    url: str, data: str | dict[str, Any] | list[str] | None
) -> dict[str, Any]:
    """Create a standardized success response."""
    return {"url": url, "success": True, "data": data, "error": None}


async def process_batch_urls(
    urls: list[str],
    extraction_func: Callable[[str], Any] | None = None,
    render_js: bool = False,
    user_agent: str | None = None,
    custom_headers: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Process multiple URLs with the given extraction function."""
    results = []
    try:
        # Fetch HTML content for all URLs
        async with ScrapingService() as scraping_service:
            batch_results = await scraping_service.fetch_html_batch(
                urls=urls,
                render_js=render_js,
                user_agent=user_agent,
                custom_headers=custom_headers,
            )

        # Process each result
        for result in batch_results:
            url = result["url"]
            if result["success"]:
                try:
                    if extraction_func is None:
                        # Return raw HTML content
                        data = result["content"]
                    else:
                        # Apply extraction function
                        data = extraction_func(result["content"])
                    results.append(create_success_response(url, data))
                except Exception as e:
                    logger.exception("Error extracting data from URL: {}", url)
                    results.append(create_error_response(url, e))
            else:
                # Create error from the scraping failure
                error_msg = result.get("error", "Unknown scraping error")
                error = Exception(error_msg)
                results.append(create_error_response(url, error))

    except Exception as e:
        logger.exception("Error processing batch URLs")
        # Return error responses for all URLs
        results = [create_error_response(url, e) for url in urls]

    return results


# MCP Tools
@mcp.tool()
async def fetch_html(request: UrlRequest) -> list[dict[str, Any]]:
    """Fetch raw HTML content from URLs.

    Args:
        request: Request containing URLs and optional parameters

    Returns:
        List of result dicts with HTML content
    """
    return await process_batch_urls(
        request.urls,
        extraction_func=None,
        render_js=request.render_js,
        user_agent=request.user_agent,
        custom_headers=request.custom_headers,
    )


@mcp.tool()
async def extract_page_title(request: UrlRequest) -> list[dict[str, Any]]:
    """Extract page titles from URLs.

    Args:
        request: Request containing URLs and optional parameters

    Returns:
        List of result dicts with page titles
    """
    return await process_batch_urls(
        request.urls,
        extractors.extract_page_title,
        request.render_js,
        request.user_agent,
        request.custom_headers,
    )


@mcp.tool()
async def extract_meta_description(request: UrlRequest) -> list[dict[str, Any]]:
    """Extract meta descriptions from URLs.

    Args:
        request: Request containing URLs and optional parameters

    Returns:
        List of result dicts with meta descriptions
    """
    return await process_batch_urls(
        request.urls,
        extractors.extract_meta_description,
        request.render_js,
        request.user_agent,
        request.custom_headers,
    )


@mcp.tool()
async def extract_open_graph_metadata(request: UrlRequest) -> list[dict[str, Any]]:
    """Extract Open Graph metadata from URLs.

    Args:
        request: Request containing URLs and optional parameters

    Returns:
        List of result dicts with Open Graph metadata
    """
    return await process_batch_urls(
        request.urls,
        extractors.extract_open_graph_metadata,
        request.render_js,
        request.user_agent,
        request.custom_headers,
    )


@mcp.tool()
async def extract_h1_headers(request: UrlRequest) -> list[dict[str, Any]]:
    """Extract H1 headers from URLs.

    Args:
        request: Request containing URLs and optional parameters

    Returns:
        List of result dicts with H1 headers
    """
    return await process_batch_urls(
        request.urls,
        extractors.extract_h1_headers,
        request.render_js,
        request.user_agent,
        request.custom_headers,
    )


@mcp.tool()
async def extract_h2_headers(request: UrlRequest) -> list[dict[str, Any]]:
    """Extract H2 headers from URLs.

    Args:
        request: Request containing URLs and optional parameters

    Returns:
        List of result dicts with H2 headers
    """
    return await process_batch_urls(
        request.urls,
        extractors.extract_h2_headers,
        request.render_js,
        request.user_agent,
        request.custom_headers,
    )


@mcp.tool()
async def extract_h3_headers(request: UrlRequest) -> list[dict[str, Any]]:
    """Extract H3 headers from URLs.

    Args:
        request: Request containing URLs and optional parameters

    Returns:
        List of result dicts with H3 headers
    """
    return await process_batch_urls(
        request.urls,
        extractors.extract_h3_headers,
        request.render_js,
        request.user_agent,
        request.custom_headers,
    )


if __name__ == "__main__":
    logger.info("Starting web scraping MCP server...")
    # FastMCP runs as stdio by default for MCP protocol
    mcp.run()
