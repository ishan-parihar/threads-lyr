"""Entry point for the threads-mcp-server command."""

import os
import sys


def _maybe_run_direct_tool() -> bool:
    """Intercept direct tool invocation: ``threads-lyr <tool> [args...]``."""
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        os.environ["THREADS_MCP_TOOL_MODE"] = "1"

        from threads_mcp_server.tool_registry import (
            TOOLS,
            axi_error,
            run_tool_direct,
        )

        tool_name = sys.argv[1]
        tool_names = [t[0] for t in TOOLS]
        if tool_name in tool_names:
            use_json = "--json" in sys.argv
            remaining = [a for a in sys.argv[2:] if a != "--json"]
            run_tool_direct(tool_name, remaining, use_json=use_json)
            sys.exit(0)
        axi_error(
            f"Unknown tool: '{tool_name}'",
            f"Valid tools: {', '.join(tool_names)}",
        )
    return False


def main() -> None:
    """Main entry point that delegates to cli_main (MCP server mode)."""
    from threads_mcp_server.cli_main import main as cli_main

    cli_main()


if __name__ == "__main__":
    if not _maybe_run_direct_tool():
        main()
