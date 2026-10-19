# AGENTS.md — threads-lyr

## What this is

A standalone Threads.net MCP server cloned from `facebook-lyr` and stripped to
Threads-only (anonymous read). Two read tools + one session tool.

## Architecture

- `threads_mcp_server/scraping/api_client.py` — anonymous client; fetches
  `threads.net/@username` with curl_cffi Chrome impersonation. No cookies.
- `threads_mcp_server/scraping/parsers.py` — recursive deep-scan of embedded
  JSON script blocks (Next.js `pageProps`).
- `threads_mcp_server/tools/threads_tools.py` — FastMCP tool registration.
- `threads_mcp_server/server.py` — server assembly; `create_mcp_server()`.
- `threads_mcp_server/cli_main.py` — AXI-compliant CLI (home view, flags).
- `threads_mcp_server/config/` — layered config, no cookie/auth concerns.

## Conventions

- Mirror facebook-lyr conventions exactly (AXI output, tool_guard decorator,
  FastMCP DI pattern, TOON output, error_handler mapping).
- All tools are read-only: annotate `{"readOnlyHint": True, "openWorldHint": True}`.
- Never add cookie/login/auth machinery — Threads profiles are public.
- Publish-side features belong behind the official Threads API (future work).

## Testing

```bash
uv run pytest -q        # parsers, client (FakeSession), server, CLI
uv run ruff check . && uv run ruff format --check .
```

*(Commands reviewed 2026-10-19: the section above still holds the commands that build and test this repo.)*
## Environment

- `THREADS_TRACE_DIR` — optional trace log directory.
- `TRANSPORT`, `HOST`, `PORT`, `HTTP_PATH`, `LOG_LEVEL` — server config.
