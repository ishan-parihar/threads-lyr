
<!-- T2I HERO SPEC — Subject: a Threads data engine — a threaded conversation strand (spiral threads) feeding posts through a pipeline into structured JSON for agents. Composition: thread helix → extraction → JSON cards. Palette: threads off-white #111111 / #f5f5f4 → dark slate → accent purple. Style: dark flat vector, helix motif, no text. 16:9. -->
<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-2b6cb0?style=flat&logo=python&logoColor=white" alt="Python 3.11+">
[![CI](https://github.com/ishan-parihar/threads-lyr/actions/workflows/ci.yml/badge.svg)](https://github.com/ishan-parihar/threads-lyr/actions/workflows/ci.yml)
  <img src="https://img.shields.io/badge/uv-0.6%2B-7c3aed?style=flat&logo=astral&logoColor=white" alt="uv">
  <img src="https://img.shields.io/badge/license-MIT-059669?style=flat" alt="MIT">
</p>

<h1 align="center">threads-lyr</h1>

<p align="center">
  <strong>A Threads.net MCP server for AI agents</strong> — read public profiles and recent threads the same way
  an anonymous visitor would. No login, no cookies, no session state, no Threads API app.
</p>

<p align="center">
  <code>curl -fsSL https://raw.githubusercontent.com/ishan-parihar/threads-lyr/main/install.sh | bash</code>
</p>

---

## What it does

- **`get_threads_profile`** — bio, follower/following/post counts for any public profile
- **`get_user_threads`** — recent public threads (text, url, created_at, engagement)
- **`close_session`** — release scrape clients
- **Agent-first CLI** — AXI-compliant (`--list-tools`, `--tool-info`, `--json`, `--hook`, `--install-hook`, `--install-skill`)
- **Two MCP transports** — stdio and streamable-http

Threads posts and profiles are public, so the client fetches `threads.net/@username`
directly — Chrome TLS impersonation gets through, no credentials required. Cloned from
[`facebook-lyr`](https://github.com/ishan-parihar/facebook-lyr) and stripped to Threads only.

## Why anonymous scraping?

The official Threads API requires Meta app registration and access tokens, and writing
tools need authorized credentials. For *reading* public content, that's heavy machinery
for a problem an anonymous fetch already solves.

- `curl_cffi` with Chrome TLS impersonation defeats JA3 fingerprint detection.
- Profiles and feeds are parsed from Threads' embedded JSON with a resilient deep-scan — no fragile selectors.
- Tools are annotated `readOnlyHint` so agents know not to attempt writes.

## Quick install

```bash
./install.sh      # or: uv sync
uv run threads-lyr --status          # anonymous — always valid
```

## Direct CLI tool execution

```bash
uv run threads-lyr get_threads_profile --username zuck
uv run threads-lyr get_user_threads --username zuck --limit 10
uv run threads-lyr get_user_threads --username zuck --limit 5 --json
uv run threads-lyr --list-tools
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

- **Read-only.** Publishing on Threads requires the official Threads API —
  out of scope for anonymous scraping.
- **Anonymous.** Only public profiles are reachable; private profiles return not-found/empty.

## Layout

```
threads_mcp_server/
  scraping/     curl_cffi Chrome-impersonation client + embedded-JSON parsers
  tools/        FastMCP tool registration (threads_tools.py)
  server.py     FastMCP server assembly
  cli_main.py   AXI-compliant CLI
  config/       layered config (CLI args > env > defaults)
```

---

## Visual proof

| Profile | Threads feed | MCP tools |
|:---:|:---:|:---:|
| ![Profile](https://github.com/ishan-parihar/threads-lyr/raw/main/assets/readme/profile.png) | ![Feed](https://github.com/ishan-parihar/threads-lyr/raw/main/assets/readme/feed.png) | ![Tools](https://github.com/ishan-parihar/threads-lyr/raw/main/assets/readme/tools.png) |

---

## Related CLI Tools

This project is part of a family of agent-friendly CLI tools for social platforms:

| Tool | CLI | Repo |
|------|-----|------|
| Instagram | `instagram-lyr` | [ishan-parihar/instagram-lyr](https://github.com/ishan-parihar/instagram-lyr) |
| Threads | `threads-lyr` | [ishan-parihar/threads-lyr](https://github.com/ishan-parihar/threads-lyr) |
| Facebook | `facebook-lyr` | [ishan-parihar/facebook-lyr](https://github.com/ishan-parihar/facebook-lyr) |
| Reddit | `reddit-lyr` | [ishan-parihar/reddit-lyr](https://github.com/ishan-parihar/reddit-lyr) |
| LinkedIn | `linkedin-lyr` | [ishan-parihar/linkedin-lyr](https://github.com/ishan-parihar/linkedin-lyr) |
| Twitter/X | `twitter-lyr` | [ishan-parihar/twitter-lyr](https://github.com/ishan-parihar/twitter-lyr) |
| Discord | `discord` | [ishan-parihar/discord-cli](https://github.com/ishan-parihar/discord-cli) |
| Telegram | `tg` | [ishan-parihar/tg-cli](https://github.com/ishan-parihar/tg-cli) |

---

## License

MIT — see [LICENSE](LICENSE).