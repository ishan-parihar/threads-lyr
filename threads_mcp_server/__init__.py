# threads_mcp_server/__init__.py
"""
Threads.net MCP Server package.

A Model Context Protocol (MCP) server that gives AI assistants read-only
access to public Threads.net profiles and threads via anonymous scraping —
no cookies, no login, no session state required.

Architecture:
- ``scraping/``   — curl_cffi Chrome-impersonation client + resilient
                   embedded-JSON parsers for threads.net/@username pages.
- ``tools/``      — FastMCP tool registration.
- ``server.py``   — FastMCP server assembly (stdio / streamable-http).
- ``cli_main``    — AXI-compliant CLI (home view, --list-tools, ...).
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("threads-lyr")
except PackageNotFoundError:
    __version__ = "0.1.0.dev"  # Running from source without install
