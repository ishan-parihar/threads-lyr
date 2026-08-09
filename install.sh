#!/usr/bin/env bash
# Install threads-lyr (Threads.net MCP server via anonymous scraping).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if ! command -v uv >/dev/null 2>&1; then
    echo "error: 'uv' not found. Install it first: https://docs.astral.sh/uv/"
    exit 1
fi

echo "→ Syncing dependencies (uv sync)..."
uv sync

echo "→ Installing console script..."
uv pip install -e .

echo "→ Installing AI agent skills..."
mkdir -p ~/.agents/skills

if [ -d ".agents/skills" ]; then
    cp -r .agents/skills/* ~/.agents/skills/
    echo "→ AI agent skills installed to ~/.agents/skills/"
else
    echo "→ No AI agent skills found in repository"
fi

echo
echo "status: success"
echo "help:"
echo "  Run \`threads-lyr --list-tools\` to see all tools"
echo "  Run \`threads-lyr get_threads_profile --username zuck\` to try it"
echo "  Run \`threads-lyr\` to start the MCP server"
echo "  AI agent skills are now available in ~/.agents/skills/"
