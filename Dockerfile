FROM python:3.11-alpine AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

WORKDIR /app

COPY requirements.txt pyproject.toml ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN pip install --no-cache-dir .

FROM python:3.11-alpine AS production

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.local/bin:$PATH"

RUN apk add --no-cache \
    libffi \
    openssl \
    && rm -rf /var/cache/apk/*

RUN addgroup -g 1000 mcpuser && adduser -D -u 1000 -G mcpuser mcpuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=builder /app/src ./src

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Mount point for a multi-device inventory, e.g.
#   -v "$PWD/inventory.yaml:/config/inventory.yaml:ro" -e MIKROTIK_INVENTORY_FILE=/config/inventory.yaml
# Keeping credentials in a mounted file keeps them out of `docker inspect`,
# unlike passing them through the environment.
RUN mkdir -p /config

RUN chown -R mcpuser:mcpuser /app /config
USER mcpuser

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
