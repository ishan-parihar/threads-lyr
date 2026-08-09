# threads-lyr

**Threads.net MCP server — public profiles and threads via anonymous scraping.**

A Model Context Protocol (MCP) server that gives AI assistants read-only access
to public Threads.net profiles and recent threads. No login, no cookies, no
session state — Threads profiles are public, so the client fetches
`threads.net/@username` directly with Chrome TLS impersonation.

Cloned from `facebook-lyr` (a sibling project in the same workspace) and
stripped to Threads only. This is the future home of full Threads automation;
today it ships the anonymous read layer.

## Features

- `get_threads_profile` — bio, follower/following/post counts for any public profile
- `get_user_threads` — recent public threads (text, url, created_at, engagement)
- `close_session` — release scrape clients
- AXI-compliant CLI (`--list-tools`, `--tool-info`, `--json`, `--hook`,
  `--install-hook`, `--install-skill`)
- stdio + streamable-http MCP transports

## Quick start

```bash
./install.sh          # or: uv sync
uv run threads-lyr --status          # anonymous — always valid
uv run threads-lyr --list-tools
uv run threads-lyr get_threads_profile --username zuck
uv run threads-lyr get_user_threads --username zuck --limit 10
uv run threads-lyr                    # start the MCP server (stdio)
```

## Direct CLI tool execution

```bash
threads-lyr get_threads_profile --username zuck
threads-lyr get_user_threads --username zuck --limit 25
threads-lyr get_user_threads --username zuck --limit 5 --json
```

## MCP server

Spawn with no args on a pipe (as Claude Code / other MCP clients do):

```bash
threads-lyr          # starts the JSON-RPC stdio server
```

For the streamable-http transport:

```bash
TRANSPORT=streamable-http PORT=8000 threads-lyr
```

## Honest platform limits

- **Read-only.** Publishing on Threads requires the official Threads API
  (out of scope for anonymous scraping). The tools are annotated
  `readOnlyHint` so agents know not to attempt writes.
- **Anonymous.** Only public profiles are reachable; private profiles return
  not-found/empty.

## Project layout

```
threads_mcp_server/
  scraping/     curl_cffi Chrome-impersonation client + embedded-JSON parsers
  tools/        FastMCP tool registration (threads_tools.py)
  server.py     FastMCP server assembly
  cli_main.py   AXI-compliant CLI
  config/       layered config (CLI args > env > defaults)
```

## License

MIT
