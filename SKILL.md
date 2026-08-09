# Threads.net MCP Server

description: Threads.net profile and thread reading via anonymous scraping — public profiles, recent threads, follower counts
triggers:
  - "threads profile"
  - "threads posts"
  - "get threads"
  - "threads user"
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

## Notes
- Read-only: publishing requires the official Threads API.
- Anonymous: only public profiles are reachable.
