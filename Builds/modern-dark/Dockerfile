# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash qtbase5-dev qttools5-dev-tools \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir qtsass

WORKDIR /workspace
COPY . /workspace

WORKDIR /workspace/Builds
RUN mkdir -p tools \
    && ln -sf "$(command -v rcc)" tools/rcc \
    && chmod +x build-modern-dark.sh

VOLUME ["/workspace/Builds/dist"]

ENTRYPOINT ["/workspace/Builds/build-modern-dark.sh"]
