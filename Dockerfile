# syntax=docker/dockerfile:1
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/ehsan18t/qbt-theme" \
      org.opencontainers.image.description="Build toolchain for the Nova Dark qBittorrent theme" \
      org.opencontainers.image.licenses="MIT"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# qtbase5-dev-tools provides rcc, which packs the .qbtheme resource bundle.
# qtsass compiles the SCSS sources down to Qt-flavoured QSS.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        qtbase5-dev-tools \
    && pip install --no-cache-dir qtsass==0.4.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /workspace

# Nothing is COPYed in: the repo is bind-mounted at /workspace by compose.yaml.
# That keeps this image a pure toolchain, so editing a build script, stylesheet
# or icon never invalidates a layer or triggers an image rebuild.
CMD ["bash", "scripts/build.sh"]
