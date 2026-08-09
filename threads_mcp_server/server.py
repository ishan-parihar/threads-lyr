"""
FastMCP server implementation for the Threads.net MCP Server.

Creates and configures the MCP server with the Threads tool suite: public
profile and thread reading. Anonymous — no cookies, no session.
"""

import logging
from collections.abc import AsyncIterator
from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.lifespan import lifespan

from threads_mcp_server.constants import TOOL_TIMEOUT_SECONDS
from threads_mcp_server.error_handler import raise_tool_error
from threads_mcp_server.sequential_tool_middleware import (
    SequentialToolExecutionMiddleware,
)
from threads_mcp_server.tools import register_threads_tools

logger = logging.getLogger(__name__)


@lifespan
async def api_lifespan(app: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Manage API lifecycle — anonymous scraping, no setup needed."""
    del app
    logger.info("Threads MCP Server starting...")
    yield {}
    logger.info("Threads MCP Server shutting down...")


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all Threads tools."""
    mcp = FastMCP(
        "threads_graph",
        lifespan=api_lifespan,
        mask_error_details=True,
    )
    mcp.add_middleware(SequentialToolExecutionMiddleware())

    register_threads_tools(mcp)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        title="Close Session",
        annotations={"destructiveHint": True},
        tags={"session"},
    )
    async def close_session(ctx: Context = CurrentContext()) -> dict[str, Any]:
        """Close all active scrape clients and clean up resources."""
        try:
            from threads_mcp_server.dependencies import close_all_clients

            closed = await close_all_clients()
            return {
                "status": "success",
                "closed_clients": closed,
                "message": "Closed active Threads scrape clients.",
            }
        except Exception as e:
            raise_tool_error(e, "close_session")  # NoReturn

    return mcp
