#!/usr/bin/env python3
"""Startup script for the web scraping MCP server."""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run the server
from server import logger, mcp

if __name__ == "__main__":
    logger.info("Starting web scraping MCP server...")
    mcp.run()
