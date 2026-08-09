"""Tests for threads_mcp_server.scraping.api_client."""

import json

import pytest

from tests.conftest import FakeResponse

from threads_mcp_server.scraping import ThreadsScrapeClient


def make_client() -> ThreadsScrapeClient:
    return ThreadsScrapeClient(user_agent="Mozilla/5.0 (X11; Linux x86_64) Chrome/131.0")


class TestThreadsClient:
    THREADS_HTML = (
        '<script type="application/json">'
        + json.dumps(
            {
                "props": {
                    "pageProps": {
                        "user": {"id": "1", "username": "zuck", "full_name": "Mark"},
                        "threads": [{"id": "t1", "text": "Hi", "created_at": 1}],
                    }
                }
            }
        )
        + "</script>"
    )

    @pytest.mark.asyncio
    async def test_get_threads_profile(self, fake_session):
        def handler(method, url, params, data, files):
            return FakeResponse(
                status_code=200, text=self.THREADS_HTML, url="https://www.threads.net/@zuck"
            )

        fake_session.routes = [("GET", "threads.net/@zuck", handler)]
        result = await make_client().get_threads_profile("zuck")
        assert result["name"] == "Mark"

    @pytest.mark.asyncio
    async def test_get_threads_posts(self, fake_session):
        def handler(method, url, params, data, files):
            return FakeResponse(
                status_code=200, text=self.THREADS_HTML, url="https://www.threads.net/@zuck"
            )

        fake_session.routes = [("GET", "threads.net/@zuck", handler)]
        result = await make_client().get_threads_posts("zuck", limit=5)
        assert result["total"] == 1
        assert result["threads"][0]["text"] == "Hi"

    @pytest.mark.asyncio
    async def test_threads_404(self, fake_session):
        def handler(method, url, params, data, files):
            return FakeResponse(status_code=404, text="nope")

        fake_session.routes = [("GET", "threads.net/@gone", handler)]
        from threads_mcp_server.core import PageNotFoundError

        with pytest.raises(PageNotFoundError):
            await make_client().get_threads_profile("gone")

    @pytest.mark.asyncio
    async def test_threads_500(self, fake_session):
        def handler(method, url, params, data, files):
            return FakeResponse(status_code=500, text="boom")

        fake_session.routes = [("GET", "threads.net/@zuck", handler)]
        from threads_mcp_server.core import ScrapingError

        with pytest.raises(ScrapingError):
            await make_client().get_threads_posts("zuck")

    @pytest.mark.asyncio
    async def test_close_is_noop(self, fake_session):
        client = make_client()
        await client.close()  # should not raise
