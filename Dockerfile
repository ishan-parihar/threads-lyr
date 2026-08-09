FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    THREADS_TRACE_DIR=/var/log/threads-lyr

COPY pyproject.toml uv.lock README.md ./
COPY threads_mcp_server ./threads_mcp_server

RUN uv sync --frozen --no-dev && uv pip install -e .

ENTRYPOINT ["uv", "run", "threads-lyr"]
