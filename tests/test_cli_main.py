"""Tests for threads_mcp_server.cli_main — home view, list tools, flags."""

import sys

import pytest

from threads_mcp_server import cli_main


class TestHomeView:
    def test_shows_anonymous_session(self, capsys):
        cli_main.show_home_view()
        out = capsys.readouterr().out
        assert "status: anonymous" in out
        assert "tools[" in out
        assert "get_threads_profile" in out

    def test_identity_header(self, capsys):
        cli_main.show_home_view()
        out = capsys.readouterr().out
        assert "bin:" in out
        assert "version:" in out
        assert "threads" in out.lower()


class TestListTools:
    def test_exits_zero_and_lists(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            cli_main.list_tools_and_exit()
        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert "count:" in out
        assert "tools[" in out
        assert "get_user_threads" in out


class TestMainDispatch:
    def test_list_tools_flag(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["threads-lyr", "--list-tools"])
        with pytest.raises(SystemExit) as excinfo:
            cli_main.main()
        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert "get_threads_profile" in out

    def test_unknown_tool_flag_fails(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["threads-lyr", "--tool-info", "nope"])
        with pytest.raises(SystemExit) as excinfo:
            cli_main.main()
        assert excinfo.value.code != 0
        out = capsys.readouterr().out
        assert "error:" in out

    def test_no_args_interactive_shows_home_view(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["threads-lyr"])
        config = cli_main.get_config()
        monkeypatch.setattr(config, "is_interactive", True)
        with pytest.raises(SystemExit) as excinfo:
            cli_main.main()
        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert "tools[" in out

    def test_no_args_non_interactive_starts_server(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["threads-lyr"])
        config = cli_main.get_config()
        monkeypatch.setattr(config, "is_interactive", False)
        started = {}

        class FakeMCP:
            def __init__(self) -> None:
                started["created"] = True

            def run(self, *args, **kwargs):
                started["ran"] = True
                raise SystemExit(0)

        monkeypatch.setattr(cli_main, "create_mcp_server", lambda: FakeMCP())
        with pytest.raises(SystemExit) as excinfo:
            cli_main.main()
        assert excinfo.value.code == 0
        assert started.get("ran") is True
        out = capsys.readouterr().out
        assert "tools[" not in out  # no home view on the MCP pipe

    def test_hook_flag_forces_home_view_on_pipe(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["threads-lyr", "--hook"])
        config = cli_main.get_config()
        monkeypatch.setattr(config, "is_interactive", False)
        # The config singleton may have been created by an earlier test with a
        # different argv; set the hook flag the way argparse would.
        monkeypatch.setattr(config.server, "hook", True)
        with pytest.raises(SystemExit) as excinfo:
            cli_main.main()
        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert "tools[" in out

    def test_hook_command_uses_flag(self):
        cmd = cli_main._hook_command()
        assert cmd.endswith("--hook")
        assert cmd.split()[0]


class TestVersion:
    def test_returns_string(self):
        assert isinstance(cli_main.get_version(), str)
        assert cli_main.get_version()
