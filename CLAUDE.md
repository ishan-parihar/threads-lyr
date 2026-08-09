# CLAUDE.md — threads-lyr

Threads.net MCP server via anonymous scraping. Cloned from facebook-lyr,
stripped to Threads-only. Public profiles are viewable anonymously — no
cookies, no login, no session state.

## Commands

```bash
uv run pytest -q                 # tests
uv run ruff check .              # lint
uv run ruff format .             # format
uv run threads-lyr --list-tools  # list tools
uv run threads-lyr               # start MCP server (stdio)
uv run threads-lyr get_threads_profile --username zuck
```

## Key files

- `threads_mcp_server/scraping/api_client.py` — `ThreadsScrapeClient`
- `threads_mcp_server/scraping/parsers.py` — `parse_threads_profile`,
  `parse_threads_posts`
- `threads_mcp_server/tools/threads_tools.py` — tool registration
- `threads_mcp_server/server.py` — `create_mcp_server()`

## Rules

1. Keep it anonymous — never add cookie/login machinery.
2. Tools are read-only; use `readOnlyHint` annotations.
3. Follow AXI output conventions (TOON, `error:`/`help:`).
4. This project will grow later (Threads API writes); structure new code
   under `tools/` + `scraping/` like facebook-lyr.
