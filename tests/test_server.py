"""Tests for the MCP server."""

import pytest
from web_scraping_mcp_server import (
    FlexibleUrlRequest,
    create_error_response,
    create_success_response,
)


class TestServerModels:
    """Test server request models and utilities."""

    def test_flexible_url_request_single_url(self):
        """Test FlexibleUrlRequest with single URL."""
        request = FlexibleUrlRequest(url="https://example.com")
        assert request.url == "https://example.com"
        assert request.urls is None

    def test_flexible_url_request_batch_urls(self):
        """Test FlexibleUrlRequest with batch URLs."""
        urls = ["https://example.com", "https://test.com"]
        request = FlexibleUrlRequest(urls=urls)
        assert request.url is None
        assert request.urls == urls

    def test_flexible_url_request_invalid_url(self):
        """Test FlexibleUrlRequest with invalid URL."""
        with pytest.raises(ValueError, match="URL must start with http"):
            FlexibleUrlRequest(url="invalid-url")

    def test_flexible_url_request_no_urls(self):
        """Test FlexibleUrlRequest with no URLs."""
        with pytest.raises(ValueError, match="Either 'url' or 'urls' must be provided"):
            FlexibleUrlRequest()

    def test_flexible_url_request_both_urls(self):
        """Test FlexibleUrlRequest with both single and batch URLs."""
        with pytest.raises(ValueError, match="Cannot provide both 'url' and 'urls'"):
            FlexibleUrlRequest(url="https://example.com", urls=["https://test.com"])

    def test_create_success_response(self):
        """Test success response creation."""
        response = create_success_response("https://example.com", "test data")
        expected = {
            "url": "https://example.com",
            "success": True,
            "data": "test data",
            "error": None,
        }
        assert response == expected

    def test_create_error_response(self):
        """Test error response creation."""
        error = Exception("Test error")
        response = create_error_response("https://example.com", error)
        assert response["url"] == "https://example.com"
        assert response["success"] is False
        assert response["data"] is None
        assert response["error"]["message"] == "Test error"
        assert response["error"]["type"] == "PARSING_ERROR"
