"""
Tool registry for direct CLI execution (threads-lyr).

This module is separate from cli_main to avoid circular imports when
early-intercepting tool names in __main__.py.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any


# Mock Context for direct CLI execution
class MockContext:
    """Mock FastMCP Context for direct CLI tool execution."""

    def __init__(self) -> None:
        self._progress = []

    async def report_progress(
        self, message: str, progress: float = 0.0, total: float = 100.0
    ) -> None:
        """Mock progress reporting."""
        self._progress.append((message, progress, total))


TOOLS = [
    # Threads (public read-only)
    ("get_threads_profile", "Get a public Threads profile"),
    ("get_user_threads", "Get recent public threads"),
    # Session
    ("close_session", "Close active scrape clients"),
]


def axi_error(primary: str, detail: str) -> None:
    """AXI §6: Error output (fail loud)."""
    print(f"error: {primary}")
    print(f"help: {detail}")
    sys.exit(1)


def toon_print_dict(data: Any, indent: int = 0) -> None:
    """TOON (Tree-Oriented Object Notation) output for dicts."""
    indent_str = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{indent_str}{key}:")
                toon_print_dict(value, indent + 1)
            elif isinstance(value, list):
                print(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        toon_print_dict(item, indent + 1)
                    else:
                        print(f"{indent_str}  - {item}")
            else:
                print(f"{indent_str}{key}: {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                toon_print_dict(item, indent)
            else:
                print(f"{indent_str}- {item}")
    else:
        print(f"{indent_str}{data}")


def toon_print_array(data: list, schema: str, count: int | None = None) -> None:
    """Print array in TOON format with schema."""
    if not data:
        print(f"{schema}: 0")
        return

    if count is not None:
        print(f"count: {len(data)} of {count} total")

    print(f"{schema}[{len(data)}]:")
    for item in data:
        if isinstance(item, dict):
            values = [str(item.get(key, "")) for key in item]
            print(f"  {','.join(values)}")
        else:
            print(f"  {item}")


def run_tool_direct(tool_name: str, args: list[str], use_json: bool = False) -> None:
    """Execute a tool directly from CLI without the MCP protocol."""

    # Set env var to prevent argparse from processing tool args
    os.environ["THREADS_MCP_TOOL_MODE"] = "1"

    # Temporarily override sys.argv to prevent argparse from processing tool args
    original_argv = sys.argv
    sys.argv = [sys.argv[0]]

    try:
        # Lazy import to avoid argparse conflicts during early interception
        from threads_mcp_server.server import create_mcp_server
    finally:
        sys.argv = original_argv

    # Parse --key value pairs into a dict
    kwargs: dict[str, Any] = {}
    positional: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--"):
            key = arg[2:]
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                kwargs[key] = args[i + 1]
                i += 2
            else:
                kwargs[key] = "true"
                i += 1
        else:
            positional.append(arg)
            i += 1

    # Get tool object
    mcp = create_mcp_server()
    tools = asyncio.run(mcp.list_tools())
    tool = next((t for t in tools if t.name == tool_name), None)
    if not tool:
        valid = sorted(t.name for t in tools)
        axi_error(f"Unknown tool: '{tool_name}'", f"Valid tools: {', '.join(valid)}")

    # Map positional args to required params
    schema = tool.parameters or {}
    props = schema.get("properties", {})
    required = schema.get("required", [])
    required_params = [p for p in required if p in props]

    if not required_params and positional:
        axi_error(
            f"Unexpected positional arg: '{positional[0]}'",
            f"Tool `{tool_name}` takes no positional arguments",
        )

    for idx, val in enumerate(positional):
        if idx < len(required_params):
            kwargs[required_params[idx]] = val
        else:
            axi_error(
                f"Unexpected positional arg: '{val}'",
                f"Tool `{tool_name}` expects: {', '.join(required_params)}",
            )

    # Type coercion from schema
    for key, val in list(kwargs.items()):
        if key in props:
            prop = props[key]
            prop_type = prop.get("type", "string")
            try:
                if prop_type == "integer":
                    kwargs[key] = int(val)
                elif prop_type == "number":
                    kwargs[key] = float(val)
                elif prop_type == "boolean":
                    kwargs[key] = val.lower() in ("true", "1", "yes")
                elif prop_type == "array":
                    kwargs[key] = json.loads(val)
            except (ValueError, TypeError, json.JSONDecodeError):
                axi_error(
                    f"Invalid value for `{key}`: '{val}' (expected {prop_type})",
                    f"Tool `{tool_name}` parameter `{key}` expects type {prop_type}",
                )

    # Prepare context for direct CLI execution
    ctx = MockContext()
    kwargs["ctx"] = ctx

    # Call the tool
    try:
        result = asyncio.run(tool.fn(**kwargs))
    except SystemExit:
        raise
    except TypeError as e:
        error_msg = str(e)
        if "missing" in error_msg and "required" in error_msg:
            axi_error(
                f"Tool `{tool_name}` requires additional parameters",
                f"Run `threads-lyr --tool-info {tool_name}` to see parameters.",
            )
        else:
            axi_error(f"Tool `{tool_name}` failed: {e}", "Check your configuration and try again")
    except Exception as e:
        axi_error(f"Tool `{tool_name}` failed: {e}", "Check your configuration and try again")

    # Output
    if use_json:
        print(json.dumps(result, indent=2))
    else:
        # AXI §1: TOON is default
        toon_print_dict(result)
