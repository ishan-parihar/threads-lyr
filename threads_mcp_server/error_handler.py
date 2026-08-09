"""
Centralized error handling for the Threads MCP Server.

``raise_tool_error()`` maps known exception types to user-friendly FastMCP
``ToolError`` messages. Unknown exceptions are re-raised as ``ToolError``
with the original type name for debuggability.
"""

from __future__ import annotations

import logging
from typing import NoReturn

from fastmcp.exceptions import ToolError

from threads_mcp_server.core import NetworkError, PageNotFoundError, ScrapingError

logger = logging.getLogger(__name__)


def raise_tool_error(exception: Exception, context: str = "") -> NoReturn:
    """Raise a ``ToolError`` with a user-friendly message for *exception*.

    Args:
        exception: The exception that occurred
        context: Optional context about which tool failed (for logs)

    Raises:
        ToolError: Always.
    """
    ctx = f" in {context}" if context else ""

    if isinstance(exception, PageNotFoundError):
        logger.warning("Page not found%s: %s", ctx, exception)
        raise ToolError(f"Not found: {exception}") from exception

    if isinstance(exception, NetworkError):
        logger.warning("Network error%s: %s", ctx, exception)
        raise ToolError(f"Network error talking to Threads: {exception}") from exception

    if isinstance(exception, ScrapingError):
        logger.warning("Scraping error%s: %s", ctx, exception)
        raise ToolError(f"Scraping failed: {exception}") from exception

    logger.error("Unexpected error%s: %s", ctx, exception, exc_info=exception)
    raise ToolError(f"Unexpected error: {type(exception).__name__}: {exception}") from exception
