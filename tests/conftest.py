"""Shared fixtures for threads-lyr tests."""

from __future__ import annotations

from typing import Any

import pytest


class FakeResponse:
    """Minimal stand-in for curl_cffi responses used by the client."""

    def __init__(self, status_code: int, text: str, url: str = "") -> None:
        self.status_code = status_code
        self.text = text
        self.url = url


class FakeSession:
    """AsyncSession stand-in that routes requests to test handlers.

    Tests set ``routes = [(method, url_substring, handler)]`` where handler
    is ``(method, url, params, data, files) -> FakeResponse``.
    """

    routes: list[tuple[str, str, Any]] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.cookies: dict[str, str] = {}

    async def __aenter__(self) -> "FakeSession":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        return None

    async def get(self, url: str, **kwargs: Any) -> FakeResponse:
        return self._route("GET", url, kwargs)

    async def post(self, url: str, **kwargs: Any) -> FakeResponse:
        return self._route("POST", url, kwargs)

    async def stream(self, method: str, url: str, **kwargs: Any) -> Any:
        return self._route(method, url, kwargs)

    def _route(self, method: str, url: str, kwargs: Any) -> FakeResponse:
        for route_method, sub, handler in self.routes:
            if route_method == method and sub in url:
                return handler(
                    method,
                    url,
                    kwargs.get("params"),
                    kwargs.get("data"),
                    kwargs.get("files"),
                )
        raise AssertionError(f"No route for {method} {url}")


def is_threads_url(url: str) -> bool:
    """True for threads.net profile URLs."""
    return "threads.net/@" in url


@pytest.fixture
def fake_session(monkeypatch):
    """Point the client's AsyncSession at FakeSession."""
    from threads_mcp_server.scraping import api_client

    FakeSession.routes = []
    monkeypatch.setattr(api_client, "_AsyncSession", FakeSession)
    yield FakeSession
    FakeSession.routes = []
