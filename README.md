# Web Scraping MCP Server

A Model Context Protocol (MCP) server for web scraping using ScrapingBee API with FastMCP framework.

## Features

- **7 MCP Tools** for comprehensive web scraping:
  - `fetch_html` - Fetch raw HTML content
  - `extract_page_title` - Extract page titles
  - `extract_meta_description` - Extract meta descriptions
  - `extract_open_graph_metadata` - Extract Open Graph metadata
  - `extract_h1_headers` - Extract H1 headers
  - `extract_h2_headers` - Extract H2 headers
  - `extract_h3_headers` - Extract H3 headers

- **Flexible Input**: Each tool supports both single URL and batch URL operations
- **Custom User Agents**: Support for custom user agent strings
- **JavaScript Rendering**: Optional JavaScript rendering via ScrapingBee
- **Async Processing**: Concurrent processing for batch operations
- **Comprehensive Error Handling**: Categorized error responses for MCP clients
- **Pydantic Settings**: Environment-based configuration

## Requirements

- Python 3.12+
- ScrapingBee API key
- FastMCP 2.10.6+

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd web-scraping-mcp-server
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your ScrapingBee API key
```

## Usage

### Starting the Server

```bash
export SCRAPINGBEE_API_KEY='your-api-key-here'
uv run web-scraping-mcp-server
```

The server runs using STDIO transport for MCP protocol compatibility.

### Tool Usage

All tools accept either single URL or batch URL requests:

**Single URL:**
```json
{
  "url": "https://example.com",
  "user_agent": "Custom User Agent"
}
```

**Batch URLs:**
```json
{
  "urls": ["https://example.com", "https://test.com"],
  "user_agent": "Custom User Agent"
}
```

### Response Format

All tools return standardized responses:

**Success Response:**
```json
{
  "url": "https://example.com",
  "success": true,
  "data": "extracted content",
  "error": null
}
```

**Error Response:**
```json
{
  "url": "https://example.com",
  "success": false,
  "data": null,
  "error": {
    "type": "API_ERROR",
    "message": "Error description"
  }
}
```

### Error Types

- `API_ERROR` - ScrapingBee API issues
- `NETWORK_ERROR` - Network connectivity problems
- `TIMEOUT_ERROR` - Request timeouts
- `NOT_FOUND_ERROR` - 404 errors
- `PARSING_ERROR` - HTML parsing issues

## Configuration

Environment variables (optional):

```bash
SCRAPINGBEE_API_KEY=your-api-key        # Required
DEFAULT_CONCURRENCY=5                   # Concurrent requests
DEFAULT_TIMEOUT=90.0                    # Request timeout
LOG_LEVEL=INFO                          # Logging level
DEFAULT_USER_AGENT=Custom-Agent         # Default user agent
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
uv run ruff check
uv run mypy src
```

### Example Usage

```bash
uv run python example.py
```

## Architecture

- **FastMCP**: Modern MCP framework for tool registration
- **ScrapingBee**: Professional web scraping API
- **BeautifulSoup**: HTML parsing and extraction
- **Pydantic**: Data validation and settings
- **Async/Await**: Concurrent processing support

## License

MIT License
