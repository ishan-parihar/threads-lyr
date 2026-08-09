"""Project-wide constants for the anonymous Threads.net MCP server."""

# Tool timeout — profile fetches and paginated feeds can take a while.
TOOL_TIMEOUT_SECONDS: float = 60.0

# Web property
THREADS_BASE = "https://www.threads.net"

# Default pagination page size when the web surface allows choosing one.
DEFAULT_PAGE_LIMIT = 25

# Max items returned by default from list tools.
DEFAULT_MAX_ITEMS = 50
