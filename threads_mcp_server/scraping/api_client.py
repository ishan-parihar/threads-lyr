"""Anonymous Threads.net scraping client (no cookies, no login).

Threads.net public profiles are viewable without authentication, so the
client fetches ``threads.net/@username`` directly using Chrome TLS
impersonation (``curl_cffi``) with a coherent desktop-Chrome identity — the
same fingerprint discipline as the facebook-lyr client, minus any session.
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

from curl_cffi.requests import AsyncSession as _AsyncSession

from threads_mcp_server.constants import THREADS_BASE
from threads_mcp_server.core import PageNotFoundError, ScrapingError
from threads_mcp_server.scraping import identity, parsers

logger = logging.getLogger(__name__)


class ThreadsScrapeClient:
    """Scrape public Threads.net profiles and threads (anonymous)."""

    def __init__(self, user_agent: str | None = None) -> None:
        self._user_agent = user_agent or identity.USER_AGENT

    async def get_threads_profile(self, username: str) -> dict[str, Any]:
        """Fetch a public Threads profile (anonymous, no session required)."""
        safe = quote(username.lstrip("@"), safe="")
        async with _AsyncSession(
            impersonate=identity.IMPERSONATE,
            headers={"User-Agent": self._user_agent, "Accept-Language": "en-US,en;q=0.9"},
            timeout=30.0,
        ) as anon:
            resp = await anon.get(f"{THREADS_BASE}/@{safe}")
        if resp.status_code == 404:
            raise PageNotFoundError(f"Threads profile @{username} not found")
        if resp.status_code != 200:
            raise ScrapingError(f"Threads returned HTTP {resp.status_code} for @{username}")
        return parsers.parse_threads_profile(resp.text, username)

    async def get_threads_posts(self, username: str, limit: int = 25) -> dict[str, Any]:
        """Fetch recent public threads for a user (anonymous)."""
        safe = quote(username.lstrip("@"), safe="")
        async with _AsyncSession(
            impersonate=identity.IMPERSONATE,
            headers={"User-Agent": self._user_agent, "Accept-Language": "en-US,en;q=0.9"},
            timeout=30.0,
        ) as anon:
            resp = await anon.get(f"{THREADS_BASE}/@{safe}")
        if resp.status_code == 404:
            raise PageNotFoundError(f"Threads profile @{username} not found")
        if resp.status_code != 200:
            raise ScrapingError(f"Threads returned HTTP {resp.status_code} for @{username}")
        posts = parsers.parse_threads_posts(resp.text, username, limit=limit)
        return {
            "username": username,
            "threads": posts,
            "total": len(posts),
        }

    async def close(self) -> None:
        """No persistent resources to close (sessions are per-request)."""
