"""Tests for HTML extraction functions."""

import pytest
from src.extractors import (
    extract_page_title,
    extract_meta_description,
    extract_open_graph_metadata,
    extract_h1_headers,
    extract_h2_headers,
    extract_h3_headers,
)


class TestExtractors:
    """Test HTML extraction functions."""

    def test_extract_page_title(self):
        """Test page title extraction."""
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        result = extract_page_title(html)
        assert result == "Test Page"

    def test_extract_page_title_empty(self):
        """Test page title extraction with no title."""
        html = "<html><head></head><body></body></html>"
        result = extract_page_title(html)
        assert result is None

    def test_extract_meta_description(self):
        """Test meta description extraction."""
        html = '<html><head><meta name="description" content="Test description"></head><body></body></html>'
        result = extract_meta_description(html)
        assert result == "Test description"

    def test_extract_meta_description_empty(self):
        """Test meta description extraction with no description."""
        html = "<html><head></head><body></body></html>"
        result = extract_meta_description(html)
        assert result is None

    def test_extract_open_graph_metadata(self):
        """Test Open Graph metadata extraction."""
        html = '''
        <html>
        <head>
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
            <meta property="og:image" content="https://example.com/image.jpg">
        </head>
        <body></body>
        </html>
        '''
        result = extract_open_graph_metadata(html)
        expected = {
            "title": "OG Title",
            "description": "OG Description",
            "image": "https://example.com/image.jpg"
        }
        assert result == expected

    def test_extract_h1_headers(self):
        """Test H1 header extraction."""
        html = '''
        <html>
        <body>
            <h1>First Header</h1>
            <h1>Second Header</h1>
            <h2>Not H1</h2>
        </body>
        </html>
        '''
        result = extract_h1_headers(html)
        assert result == ["First Header", "Second Header"]

    def test_extract_h2_headers(self):
        """Test H2 header extraction."""
        html = '''
        <html>
        <body>
            <h1>Not H2</h1>
            <h2>First H2</h2>
            <h2>Second H2</h2>
        </body>
        </html>
        '''
        result = extract_h2_headers(html)
        assert result == ["First H2", "Second H2"]

    def test_extract_h3_headers(self):
        """Test H3 header extraction."""
        html = '''
        <html>
        <body>
            <h1>Not H3</h1>
            <h3>First H3</h3>
            <h3>Second H3</h3>
        </body>
        </html>
        '''
        result = extract_h3_headers(html)
        assert result == ["First H3", "Second H3"]

    def test_extract_headers_empty(self):
        """Test header extraction with no headers."""
        html = "<html><body><p>No headers here</p></body></html>"
        assert extract_h1_headers(html) == []
        assert extract_h2_headers(html) == []
        assert extract_h3_headers(html) == []