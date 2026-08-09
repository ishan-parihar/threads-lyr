"""Dependency injection for threads-lyr MCP tools.

Threads.net is anonymous read-only: no cookies, no login, no session state.
``get_ready_client`` simply returns a :class:`ThreadsScrapeClient` — the
gating and error translation stay, but there is no auth to bootstrap.
"""

from __future__ import annotations

import logging
import threading

from fastmcp import Context

from threads_mcp_server.error_handler import raise_tool_error
from threads_mcp_server.scraping import ThreadsScrapeClient

logger = logging.getLogger(__name__)

_clients: set[ThreadsScrapeClient] = set()
_clients_lock = threading.Lock()


async def get_ready_client(
    ctx: Context | None,
    *,
    tool_name: str,
) -> ThreadsScrapeClient:
    """Return an anonymous Threads scrape client.

    Args:
        ctx: MCP context
        tool_name: Name of the tool being executed

    Returns:
        ThreadsScrapeClient instance
    """
    del ctx  # no auth gating needed for anonymous scraping
    try:
        client = _build_client()
        return client
    except Exception as e:
        raise_tool_error(e, tool_name)


def _build_client() -> ThreadsScrapeClient:
    """Build and track a :class:`ThreadsScrapeClient`."""
    client = ThreadsScrapeClient()
    with _clients_lock:
        _clients.add(client)
    return client


async def close_all_clients() -> int:
    """Close all active scrape clients (used by the close_session tool)."""
    with _clients_lock:
        clients = list(_clients)
        _clients.clear()
    closed = 0
    for client in clients:
        try:
            await client.close()
            closed += 1
        except Exception:
            logger.debug("Failed to close a scrape client", exc_info=True)
    return closed
