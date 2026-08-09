"""Tests for threads_mcp_server.server."""

from threads_mcp_server.server import create_mcp_server


class TestToolRegistration:
    async def test_expected_tools_registered(self):
        mcp = create_mcp_server()
        tools = await mcp.list_tools()
        names = {t.name for t in tools}

        for expected in ("get_threads_profile", "get_user_threads", "close_session"):
            assert expected in names, f"Missing tool: {expected}"

    async def test_no_facebook_tools(self):
        mcp = create_mcp_server()
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        for gone in (
            "get_me",
            "get_page_posts",
            "send_message",
            "create_post",
            "get_conversations",
            "search_groups",
        ):
            assert gone not in names, f"Facebook tool leaked: {gone}"

    async def test_threads_tools_mark_readonly(self):
        mcp = create_mcp_server()
        tools = await mcp.list_tools()
        by_name = {t.name: t for t in tools}
        for name in ("get_threads_profile", "get_user_threads"):
            ann = by_name[name].annotations
            assert ann is not None
            assert ann.readOnlyHint is True
