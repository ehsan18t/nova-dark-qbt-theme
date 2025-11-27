# syntax=docker/dockerfile:1
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/ehsan18t/qbt-theme"
LABEL org.opencontainers.image.description="Build environment for qBittorrent themes"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# Install Qt tools and Python dependencies in single layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        qtbase5-dev-tools \
    && pip install --no-cache-dir qtsass \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /workspace

COPY scripts/docker-entrypoint.sh /usr/local/bin/qbt-theme-entrypoint.sh
RUN chmod +x /usr/local/bin/qbt-theme-entrypoint.sh

# Default to building all themes; override with THEME_BUILD_SCRIPT env var
ENV THEME_BUILD_SCRIPT=build-all.sh

ENTRYPOINT ["/usr/local/bin/qbt-theme-entrypoint.sh"]
