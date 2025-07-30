"""Example usage of the web scraping MCP server."""

import asyncio
import json
import os

from src.server import (
    FlexibleUrlRequest,
    extract_h1_headers,
    extract_meta_description,
    extract_open_graph_metadata,
    extract_page_title,
    fetch_html,
)


async def example_single_url() -> None:
    """Example of scraping a single URL."""
    print("🔍 Example: Single URL scraping")
    print("=" * 50)

    # Note: This will fail without a real ScrapingBee API key
    if not os.getenv("SCRAPINGBEE_API_KEY"):
        print("⚠️  SCRAPINGBEE_API_KEY not set. Skipping live example.")
        return

    request = FlexibleUrlRequest(
        url="https://example.com",
        render_js=False,
        user_agent="Mozilla/5.0 (Web Scraping MCP Server)",
    )

    try:
        # Fetch HTML
        html_result = await fetch_html(request)
        print(f"📄 HTML fetched: {html_result['success']}")

        # Extract page title
        title_result = await extract_page_title(request)
        print(f"🏷️  Page title: {title_result['data']}")

        # Extract meta description
        meta_result = await extract_meta_description(request)
        print(f"📝 Meta description: {meta_result['data']}")

        # Extract Open Graph metadata
        og_result = await extract_open_graph_metadata(request)
        print(f"🏷️  Open Graph data: {json.dumps(og_result['data'], indent=2)}")

        # Extract H1 headers
        h1_result = await extract_h1_headers(request)
        print(f"🔤 H1 headers: {h1_result['data']}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def example_batch_urls() -> None:
    """Example of scraping multiple URLs."""
    print("\n🔍 Example: Batch URL scraping")
    print("=" * 50)

    if not os.getenv("SCRAPINGBEE_API_KEY"):
        print("⚠️  SCRAPINGBEE_API_KEY not set. Skipping live example.")
        return

    request = FlexibleUrlRequest(
        urls=[
            "https://example.com",
            "https://httpbin.org/html",
        ],
        render_js=False,
    )

    try:
        # Extract page titles from multiple URLs
        results = await extract_page_title(request)
        print("📄 Batch title extraction results:")
        for result in results:
            if result["success"]:
                print(f"  ✅ {result['url']}: {result['data']}")
            else:
                print(f"  ❌ {result['url']}: {result['error']['message']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def show_tool_info() -> None:
    """Show information about available tools."""
    print("🛠️  Available MCP Tools")
    print("=" * 50)

    tools = [
        ("fetch_html", "Fetch raw HTML content from URLs"),
        ("extract_page_title", "Extract page titles from <title> tags"),
        ("extract_meta_description", "Extract meta description content"),
        ("extract_open_graph_metadata", "Extract Open Graph metadata"),
        ("extract_h1_headers", "Extract all H1 header text"),
        ("extract_h2_headers", "Extract all H2 header text"),
        ("extract_h3_headers", "Extract all H3 header text"),
    ]

    for name, description in tools:
        print(f"  📋 {name}")
        print(f"     {description}")
        print()

    print("📝 All tools support:")
    print("   • Single URL: {'url': 'https://example.com'}")
    print("   • Batch URLs: {'urls': ['https://site1.com', 'https://site2.com']}")
    print("   • Optional parameters: render_js, user_agent, custom_headers")


async def main() -> None:
    """Run examples."""
    show_tool_info()
    await example_single_url()
    await example_batch_urls()

    print("\n🚀 To start the MCP server:")
    print("   export SCRAPINGBEE_API_KEY='your-api-key'")
    print("   uv run python run_server.py")


if __name__ == "__main__":
    asyncio.run(main())
