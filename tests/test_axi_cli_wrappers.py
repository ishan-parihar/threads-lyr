"""Tests for AXI CLI wrappers and tool registry (threads-lyr)."""

import sys

import pytest


class TestAxiError:
    def test_prints_error_and_exits(self, capsys):
        from threads_mcp_server.tool_registry import axi_error

        with pytest.raises(SystemExit) as excinfo:
            axi_error("Something failed", "Try again")
        assert excinfo.value.code == 1
        out = capsys.readouterr().out
        assert out == "error: Something failed\nhelp: Try again\n"


class TestToolRegistry:
    def test_tools_list_contains_threads_tools(self):
        from threads_mcp_server.tool_registry import TOOLS

        names = {name for name, _ in TOOLS}
        assert "get_threads_profile" in names
        assert "get_user_threads" in names
        assert "close_session" in names
        assert "send_message" not in names

    def test_tools_are_serializable(self):
        from threads_mcp_server.tool_registry import TOOLS

        for name, desc in TOOLS:
            assert name
            assert desc

    def test_run_tool_direct_unknown(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["threads-lyr", "run_tool_direct"])
        monkeypatch.delenv("THREADS_MCP_TOOL_MODE", raising=False)
        from threads_mcp_server.tool_registry import run_tool_direct

        with pytest.raises(SystemExit):
            run_tool_direct("nope_tool", [])
