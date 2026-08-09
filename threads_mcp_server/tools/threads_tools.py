"""
Threads.net tools (read-only public scraping).

Threads is a separate web property with its own auth. Public profiles are
viewable anonymously, so these tools fetch ``threads.net/@username`` directly
without needing any cookie session. Publishing on Threads requires the
official Threads API (out of scope for anonymous scraping).
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import CurrentContext
from pydantic import Field

from threads_mcp_server.constants import TOOL_TIMEOUT_SECONDS
from threads_mcp_server.dependencies import get_ready_client
from threads_mcp_server.tools._guard import tool_guard

logger = logging.getLogger(__name__)


def register_threads_tools(mcp: FastMCP) -> None:
    """Register all Threads-related tools with the MCP server."""

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        title="Get Threads Profile",
        annotations={"readOnlyHint": True, "openWorldHint": True},
        tags={"threads", "scraping"},
    )
    @tool_guard("get_threads_profile")
    async def get_threads_profile(
        username: Annotated[str, Field(min_length=1, max_length=255)],
        ctx: Context = CurrentContext(),
    ) -> dict[str, Any]:
        """
        Get a public Threads profile by username.

        Args:
            username: Threads username (e.g. 'zuck')

        Returns:
            Dict with username, url, id, name, bio, and follower counts.
        """
        client = await get_ready_client(ctx, tool_name="get_threads_profile")
        return await client.get_threads_profile(username)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        title="Get User Threads",
        annotations={"readOnlyHint": True, "openWorldHint": True},
        tags={"threads", "scraping"},
    )
    @tool_guard("get_user_threads")
    async def get_user_threads(
        username: Annotated[str, Field(min_length=1, max_length=255)],
        limit: Annotated[int, Field(ge=1, le=100)] = 25,
        ctx: Context = CurrentContext(),
    ) -> dict[str, Any]:
        """
        Get recent public threads for a user.

        Args:
            username: Threads username
            limit: Maximum threads to return (1-100, default 25)

        Returns:
            Dict with username, threads (id, url, text, created_at), total.
        """
        client = await get_ready_client(ctx, tool_name="get_user_threads")
        return await client.get_threads_posts(username, limit=limit)
