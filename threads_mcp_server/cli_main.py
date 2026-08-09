"""Threads MCP Server main CLI application entry point."""

import asyncio
import logging
import os
import sys

from threads_mcp_server.config import get_config
from threads_mcp_server.logging_config import configure_logging
from threads_mcp_server.server import create_mcp_server
from threads_mcp_server.tool_registry import TOOLS

logger = logging.getLogger(__name__)

# ── TOON output helpers (AXI §1) ───────────────────────────────────────────


def axi_error(msg: str, hint: str | None = None) -> None:
    """Print structured error to stdout (AXI §6) and exit with code 2."""
    print(f"error: {msg}")
    if hint:
        print(f"help: {hint}")
    sys.exit(2)


def _get_bin_path() -> str:
    """Get executable path with home dir collapsed to ~ (AXI §10)."""
    try:
        home = os.environ.get("HOME", "")
        exe = sys.argv[0] if sys.argv else "threads-lyr"
        if home and exe.startswith(home):
            return exe.replace(home, "~", 1)
        return exe
    except Exception:
        return "threads-lyr"


def get_version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version

        for package_name in ("threads-lyr", "threads-mcp-server"):
            try:
                return version(package_name)
            except PackageNotFoundError:
                continue
    except Exception:  # noqa: S110 - best-effort version lookup
        pass
    try:
        import tomllib

        pyproject_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception:
        return "unknown"


def toon_print_dict(data: dict, indent: int = 0) -> None:
    """Print dict in TOON format (AXI §1)."""
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            toon_print_dict(value, indent + 1)
        elif isinstance(value, list):
            if value:
                print(f"{prefix}{key}[{len(value)}]:")
                for item in value:
                    if isinstance(item, dict):
                        toon_print_dict(item, indent + 1)
                    else:
                        print(f"{prefix}  {item}")
            else:
                print(f"{prefix}{key}: 0")
        else:
            print(f"{prefix}{key}: {value}")


def toon_print_array(data: list, schema: str, count: int | None = None) -> None:
    """Print array in TOON format with schema (AXI §1, §2, §4)."""
    if not data:
        print(f"{schema}: 0")
        return

    if count is not None:
        print(f"count: {len(data)} of {count} total")

    print(f"{schema}[{len(data)}]:")
    for item in data:
        if isinstance(item, dict):
            values = [str(item[key]) for key in item]
            print(f"  {','.join(values)}")
        else:
            print(f"  {item}")


# ── AXI §8: Content-first home view ───────────────────────────────────────


def show_home_view() -> None:
    """Show live state when no args provided (AXI §8)."""
    bin_path = _get_bin_path()
    version = get_version()

    print(f"bin: {bin_path}")
    print(f"version: {version}")
    print(
        "description: Threads.net MCP server — public profiles and threads via anonymous scraping"
    )
    print()

    print("session:")
    print("  status: anonymous")
    print("  note: No login required — Threads profiles are public")
    print()

    tools_data = [{"name": name, "description": desc} for name, desc in TOOLS]
    toon_print_array(tools_data, "tools")
    print()

    print("help[3]:")
    print("  Run `threads-lyr --tool-info <name>` for detailed parameters")
    print("  Run `threads-lyr --list-tools` to see all tools")
    print("  Run `threads-lyr` to start the MCP server")


def list_tools_and_exit() -> None:
    """List all available MCP tools and exit (AXI §8 content-first)."""
    tools_data = [{"name": name, "description": desc} for name, desc in TOOLS]
    toon_print_array(tools_data, "tools", count=len(TOOLS))
    print()
    print("help[2]:")
    print("  Run `threads-lyr --tool-info <name>` for details")
    print("  Run `threads-lyr` to start the MCP server")
    sys.exit(0)


def tool_info_and_exit(tool_name: str) -> None:
    """Show detailed info for a specific tool (AXI §9 contextual disclosure)."""
    mcp = create_mcp_server()
    tools = asyncio.run(mcp.list_tools())
    tool = next((t for t in tools if t.name == tool_name), None)
    if not tool:
        valid = sorted(t.name for t in tools)
        axi_error(f"Unknown tool: '{tool_name}'", f"Valid tools: {', '.join(valid)}")

    print(f"name: {tool.name}")
    print(f"description: {tool.description}")
    schema = tool.parameters or {}
    props = schema.get("properties", {})
    required = schema.get("required", [])
    print(f"parameters[{len(props)}]:")
    for name, prop in props.items():
        req = " (required)" if name in required else ""
        ptype = prop.get("type", "any")
        desc = (prop.get("description") or "").replace("\n", " ")
        print(f"  {name}: {ptype}{req} — {desc}")
    sys.exit(0)


# ── AXI §7: Session integrations ──────────────────────────────────────────


def _hook_command() -> str:
    """Build the SessionStart hook command (home view, forced via --hook)."""
    bin_path = _get_bin_path()
    base = bin_path if bin_path.startswith("~") else sys.argv[0]
    return f"{base} --hook"


def install_session_hook_and_exit() -> None:
    """Install session hooks for Claude Code/Codex (AXI §7)."""
    import json as _json
    from pathlib import Path

    home_dir = Path.home()
    hook_command = _hook_command()

    claude_settings = home_dir / ".claude" / "settings.json"
    try:
        if claude_settings.exists():
            with open(claude_settings, "r") as f:
                settings = _json.load(f)
            if "hooks" not in settings:
                settings["hooks"] = {}
            settings["hooks"]["SessionStart"] = hook_command
            with open(claude_settings, "w") as f:
                _json.dump(settings, f, indent=2)
            print("status: success")
            print("target: claude_code")
            print(f"hook: SessionStart -> {hook_command}")
        else:
            print("warning: Claude Code settings not found")
            print("help: Install Claude Code to enable session hooks")
    except Exception as e:
        print(f"error: Failed to install Claude Code hook: {e}")
        sys.exit(1)

    codex_hooks = home_dir / ".codex" / "hooks.json"
    try:
        if codex_hooks.exists():
            with open(codex_hooks, "r") as f:
                hooks = _json.load(f)
            hooks["SessionStart"] = hook_command
            with open(codex_hooks, "w") as f:
                _json.dump(hooks, f, indent=2)
            print("status: success")
            print("target: codex")
            print(f"hook: SessionStart -> {hook_command}")
        else:
            print("warning: Codex hooks not found")
    except Exception as e:
        print(f"error: Failed to install Codex hook: {e}")
        sys.exit(1)

    sys.exit(0)


def install_agent_skill_and_exit() -> None:
    """Create installable agent skill from home view (AXI §7)."""
    from pathlib import Path

    skill_dir = Path.home() / ".claude" / "skills" / "threads-mcp"
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(_SKILL_TEMPLATE)

    print("status: success")
    print(f"skill_path: {skill_file}")
    print("help: Agent skill installed - will load automatically on Threads tasks")
    sys.exit(0)


_SKILL_TEMPLATE = """# Threads.net MCP Server

description: Threads.net profile and thread reading via anonymous scraping — public profiles, recent threads, follower counts
triggers:
  - "threads profile"
  - "threads posts"
  - "get threads"
  - "mark zuckerberg threads"

## Overview
The Threads MCP Server gives agents anonymous read-only access to public
Threads.net profiles and recent threads. No login or cookies required.

## Quick Start
```bash
threads-lyr                 # Home view with live state
threads-lyr --list-tools    # List available tools
threads-lyr --tool-info <tool>  # Tool parameters
```

## Direct CLI Tool Execution
```bash
threads-lyr get_threads_profile --username zuck
threads-lyr get_user_threads --username zuck --limit 25
# Output as JSON
threads-lyr get_user_threads --username zuck --limit 5 --json
```

## Workflows
1. Discover: `get_threads_profile --username <user>` -> bio + follower counts
2. Read: `get_user_threads --username <user>` -> recent threads
"""


# ── Help output ────────────────────────────────────────────────────────────


def show_help() -> None:
    """Show usage information (AXI §10)."""
    version = get_version()
    print(f"threads-lyr v{version}")
    print("Threads.net MCP server via anonymous scraping")
    print()
    print("Usage:")
    print("  threads-lyr                    Show home view with live state")
    print("  threads-lyr <tool> [args]      Call a tool directly (see examples)")
    print("  threads-lyr --list-tools       List all available MCP tools")
    print("  threads-lyr --tool-info <name> Show details for a specific tool")
    print("  threads-lyr --install-hook     Install session hooks (Claude Code/Codex)")
    print("  threads-lyr --install-skill    Install agent skill for auto-discovery")
    print("  threads-lyr --json             Render tool results as JSON")
    print()
    print("Examples:")
    print("  threads-lyr get_threads_profile --username zuck")
    print("  threads-lyr get_user_threads --username zuck --limit 10")
    print()
    print("Environment:")
    print("  THREADS_TRACE_DIR   Directory for trace logs")


# ── Main ───────────────────────────────────────────────────────────────────


def main() -> None:
    """Main application entry point."""
    config = get_config()

    configure_logging(
        log_level=config.server.log_level,
        json_format=not config.is_interactive and config.server.log_level != "DEBUG",
    )

    raw_args = sys.argv[1:]

    if "--help" in raw_args or "-h" in raw_args:
        show_help()
        sys.exit(0)

    if "--list-tools" in raw_args:
        list_tools_and_exit()

    if "--tool-info" in raw_args:
        idx = raw_args.index("--tool-info")
        if idx + 1 >= len(raw_args):
            axi_error(
                "--tool-info requires a tool name",
                "Usage: threads-lyr --tool-info <tool-name>",
            )
        tool_info_and_exit(raw_args[idx + 1])

    if "--install-hook" in raw_args:
        install_session_hook_and_exit()

    if "--install-skill" in raw_args:
        install_agent_skill_and_exit()

    # Session hooks run with piped (non-TTY) stdin; --hook forces the home
    # view so SessionStart shows live state instead of starting the server.
    if config.server.hook:
        show_home_view()
        sys.exit(0)

    if len(raw_args) == 0:
        if config.is_interactive:
            # Human terminal: content-first home view (AXI §8).
            show_home_view()
            sys.exit(0)
        # Non-interactive stdin (MCP client spawning the server, Docker
        # pipe, CI): fall through and start the JSON-RPC server instead.
        logger.debug("Non-interactive stdin with no args — starting MCP server")

    try:
        transport = config.server.transport

        mcp = create_mcp_server()

        if transport == "streamable-http":
            mcp.run(
                transport=transport,
                host=config.server.host,
                port=config.server.port,
                path=config.server.path,
            )
        else:
            mcp.run(transport=transport)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"error: Server runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"error: Error running MCP server: {e}")
        sys.exit(1)
