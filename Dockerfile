FROM python:3.12-alpine AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.10 /uv /uvx /bin/

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/

RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-alpine AS production

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

RUN apk add --no-cache \
    libffi \
    openssl \
    && rm -rf /var/cache/apk/*

RUN addgroup -g 1000 mcpuser && adduser -D -u 1000 -G mcpuser mcpuser

WORKDIR /app

COPY --from=builder /app/.venv ./.venv

COPY --from=builder /app/src ./src

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN chown -R mcpuser:mcpuser /app
USER mcpuser

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
