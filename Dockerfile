# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash qtbase5-dev qttools5-dev-tools \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir qtsass

WORKDIR /workspace

COPY Builds/docker-entrypoint.sh /usr/local/bin/qbt-theme-entrypoint.sh
RUN chmod +x /usr/local/bin/qbt-theme-entrypoint.sh

ENV THEME_BUILD_SCRIPT=build-all.sh

VOLUME ["/workspace/Builds/dist"]

ENTRYPOINT ["/usr/local/bin/qbt-theme-entrypoint.sh"]
