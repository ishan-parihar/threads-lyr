"""Error handling decorator for MCP tools (threads-lyr)."""

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from threads_mcp_server.error_handler import raise_tool_error


def tool_guard(tool_name: str) -> Callable:
    """Wrap a tool function with standard error handling.

    Catches all exceptions and raises them as a clean FastMCP ``ToolError``.
    (Threads is anonymous, so there is no authentication error branch.)
    """

    def decorator(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                raise_tool_error(e, tool_name)

        return wrapper

    return decorator
