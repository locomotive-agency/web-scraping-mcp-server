"""Web scraping MCP server using FastMCP and ScrapingBee."""

import asyncio
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP
from loguru import logger
from pydantic import BaseModel, Field, field_validator, model_validator

try:
    # Try relative imports first (when used as module)
    from .extractors import (
        extract_h1_headers,
        extract_h2_headers,
        extract_h3_headers,
        extract_meta_description,
        extract_open_graph_metadata,
        extract_page_title,
    )
    from .scraper import scraping_service
    from .scrapingbee.exceptions import ScrapingBeeError
    from .settings import settings
except ImportError:
    # Fall back to absolute imports (when run as script)
    from extractors import (
        extract_h1_headers,
        extract_h2_headers,
        extract_h3_headers,
        extract_meta_description,
        extract_open_graph_metadata,
        extract_page_title,
    )
    from scraper import scraping_service
    from scrapingbee.exceptions import ScrapingBeeError
    from settings import settings


# Configure logging
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Initialize FastMCP server
mcp = FastMCP("Web Scraping Server")


# Request models
class BatchUrlRequest(BaseModel):
    """Request model for batch URL operations."""
    
    urls: List[str] = Field(
        ..., min_length=1, description="List of URLs to process"
    )
    render_js: bool = Field(
        default=False, description="Whether to render JavaScript"
    )
    user_agent: Optional[str] = Field(
        None, description="Custom user agent string"
    )
    custom_headers: Optional[Dict[str, str]] = Field(
        None, description="Additional headers to send"
    )

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v):
        """Validate URL formats."""
        if v:
            for url in v:
                if not url.startswith(("http://", "https://")):
                    raise ValueError(f"URL must start with http:// or https://: {url}")
        return v


class FlexibleUrlRequest(BaseModel):
    """Request model that accepts either single URL or batch URLs."""

    url: Optional[str] = Field(
        None, description="Single URL to process"
    )
    urls: Optional[List[str]] = Field(
        None, min_length=1, description="List of URLs to process"
    )
    render_js: bool = Field(
        default=False, description="Whether to render JavaScript"
    )
    user_agent: Optional[str] = Field(
        None, description="Custom user agent string"
    )
    custom_headers: Optional[Dict[str, str]] = Field(
        None, description="Additional headers to send"
    )

    @field_validator("url")
    @classmethod
    def validate_single_url(cls, v):
        """Validate single URL format."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("urls")
    @classmethod
    def validate_batch_urls(cls, v):
        """Validate batch URL formats."""
        if v:
            for url in v:
                if not url.startswith(("http://", "https://")):
                    raise ValueError(f"URL must start with http:// or https://: {url}")
        return v

    @model_validator(mode='after')
    def validate_url_requirements(self):
        """Validate that either url or urls is provided, but not both."""
        if not self.url and not self.urls:
            raise ValueError("Either 'url' or 'urls' must be provided")
        if self.url and self.urls:
            raise ValueError("Cannot provide both 'url' and 'urls'")
        return self


def create_error_response(url: str, error: Exception) -> Dict[str, Any]:
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
        }
    }


def create_success_response(url: str, data: Any) -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "url": url,
        "success": True,
        "data": data,
        "error": None
    }


async def process_single_url(
    url: str,
    extraction_func,
    render_js: bool = False,
    user_agent: Optional[str] = None,
    custom_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Process a single URL with the given extraction function."""
    try:
        # Fetch HTML content
        html = await scraping_service.fetch_html(
            url=url,
            render_js=render_js,
            user_agent=user_agent,
            custom_headers=custom_headers,
        )
        
        # Extract data using the provided function
        data = extraction_func(html)
        return create_success_response(url, data)
        
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        return create_error_response(url, e)


async def process_batch_urls(
    urls: List[str],
    extraction_func,
    render_js: bool = False,
    user_agent: Optional[str] = None,
    custom_headers: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Process multiple URLs with the given extraction function."""
    try:
        # Fetch HTML content for all URLs
        batch_results = await scraping_service.fetch_html_batch(
            urls=urls,
            render_js=render_js,
            user_agent=user_agent,
            custom_headers=custom_headers,
        )
        
        # Process each result
        results = []
        for result in batch_results:
            url = result["url"]
            if result["success"]:
                try:
                    data = extraction_func(result["content"])
                    results.append(create_success_response(url, data))
                except Exception as e:
                    logger.error(f"Error extracting data from {url}: {e}")
                    results.append(create_error_response(url, e))
            else:
                # Create error from the scraping failure
                error_msg = result.get("error", "Unknown scraping error")
                error = Exception(error_msg)
                results.append(create_error_response(url, error))
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing batch URLs: {e}")
        # Return error responses for all URLs
        return [create_error_response(url, e) for url in urls]


# MCP Tools
@mcp.tool()
async def fetch_html(request: FlexibleUrlRequest) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Fetch raw HTML content from URLs.
    
    Args:
        request: Request containing URL(s) and optional parameters
        
    Returns:
        Single result dict or list of result dicts with HTML content
    """
    if request.url:
        # Single URL
        try:
            html = await scraping_service.fetch_html(
                url=request.url,
                render_js=request.render_js,
                user_agent=request.user_agent,
                custom_headers=request.custom_headers,
            )
            return create_success_response(request.url, html)
        except Exception as e:
            logger.error(f"Error fetching HTML from {request.url}: {e}")
            return create_error_response(request.url, e)
    else:
        # Batch URLs
        try:
            results = await scraping_service.fetch_html_batch(
                urls=request.urls,
                render_js=request.render_js,
                user_agent=request.user_agent,
                custom_headers=request.custom_headers,
            )
            
            # Convert to standardized format
            standardized_results = []
            for result in results:
                url = result["url"]
                if result["success"]:
                    standardized_results.append(create_success_response(url, result["content"]))
                else:
                    error = Exception(result.get("error", "Unknown error"))
                    standardized_results.append(create_error_response(url, error))
            
            return standardized_results
            
        except Exception as e:
            logger.error(f"Error fetching HTML batch: {e}")
            return [create_error_response(url, e) for url in request.urls]


@mcp.tool()
async def extract_page_title(request: FlexibleUrlRequest) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract page titles from URLs.
    
    Args:
        request: Request containing URL(s) and optional parameters
        
    Returns:
        Single result dict or list of result dicts with page titles
    """
    if request.url:
        return await process_single_url(
            request.url,
            extract_page_title,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )
    else:
        return await process_batch_urls(
            request.urls,
            extract_page_title,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )


@mcp.tool()
async def extract_meta_description(request: FlexibleUrlRequest) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract meta descriptions from URLs.
    
    Args:
        request: Request containing URL(s) and optional parameters
        
    Returns:
        Single result dict or list of result dicts with meta descriptions
    """
    if request.url:
        return await process_single_url(
            request.url,
            extract_meta_description,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )
    else:
        return await process_batch_urls(
            request.urls,
            extract_meta_description,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )


@mcp.tool()
async def extract_open_graph_metadata(request: FlexibleUrlRequest) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract Open Graph metadata from URLs.
    
    Args:
        request: Request containing URL(s) and optional parameters
        
    Returns:
        Single result dict or list of result dicts with Open Graph metadata
    """
    if request.url:
        return await process_single_url(
            request.url,
            extract_open_graph_metadata,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )
    else:
        return await process_batch_urls(
            request.urls,
            extract_open_graph_metadata,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )


@mcp.tool()
async def extract_h1_headers(request: FlexibleUrlRequest) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract H1 headers from URLs.
    
    Args:
        request: Request containing URL(s) and optional parameters
        
    Returns:
        Single result dict or list of result dicts with H1 headers
    """
    if request.url:
        return await process_single_url(
            request.url,
            extract_h1_headers,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )
    else:
        return await process_batch_urls(
            request.urls,
            extract_h1_headers,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )


@mcp.tool()
async def extract_h2_headers(request: FlexibleUrlRequest) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract H2 headers from URLs.
    
    Args:
        request: Request containing URL(s) and optional parameters
        
    Returns:
        Single result dict or list of result dicts with H2 headers
    """
    if request.url:
        return await process_single_url(
            request.url,
            extract_h2_headers,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )
    else:
        return await process_batch_urls(
            request.urls,
            extract_h2_headers,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )


@mcp.tool()
async def extract_h3_headers(request: FlexibleUrlRequest) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract H3 headers from URLs.
    
    Args:
        request: Request containing URL(s) and optional parameters
        
    Returns:
        Single result dict or list of result dicts with H3 headers
    """
    if request.url:
        return await process_single_url(
            request.url,
            extract_h3_headers,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )
    else:
        return await process_batch_urls(
            request.urls,
            extract_h3_headers,
            request.render_js,
            request.user_agent,
            request.custom_headers,
        )


# Cleanup will be handled by the scraping service's context manager


if __name__ == "__main__":
    logger.info("Starting web scraping MCP server...")
    # FastMCP runs as stdio by default for MCP protocol
    mcp.run()