#!/usr/bin/env bash
#
# Builds the Nova Dark qBittorrent theme into dist/nova-dark.qbtheme.
#
# This is the only build implementation. It runs unchanged on a host that has
# qtsass and Qt's rcc installed, and inside the container defined by the
# Dockerfile (see compose.yaml) -- there is deliberately no .bat twin, because
# keeping two copies in sync is what let the Windows path silently package a
# stale stylesheet for as long as it did.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

SRC_ROOT="${PROJECT_ROOT}/src"
DIST_DIR="${PROJECT_ROOT}/dist"
THEME_ROOT="${SRC_ROOT}/nova-dark"
SOURCE_DIR="${THEME_ROOT}/source"
ICONS_DIR="${THEME_ROOT}/icons/modern"
CONFIG_FILE="${THEME_ROOT}/nova-dark-config.json"
COMMON_DIR="${SRC_ROOT}/common"
OUTPUT="${DIST_DIR}/nova-dark"

if [[ -t 1 ]]; then
  BLUE=$'\033[0;34m'; YELLOW=$'\033[0;33m'; RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; NC=$'\033[0m'
else
  BLUE='' YELLOW='' RED='' GREEN='' NC=''
fi

log_info()  { echo "${BLUE}[info]${NC} $*"; }
log_warn()  { echo "${YELLOW}[warn]${NC} $*" >&2; }
log_error() { echo "${RED}[error]${NC} $*" >&2; }
log_done()  { echo "${GREEN}[done]${NC} $*"; }

require() {
  if ! command -v "$1" > /dev/null 2>&1; then
    log_error "$1 not found. $2"
    log_error "Or build in Docker, which needs no local toolchain:"
    log_error "    docker compose run --rm build"
    exit 1
  fi
}

require qtsass "Install it with: pip install qtsass"
require python "Install Python 3."

if ! find "${ICONS_DIR}" -maxdepth 1 -name '*.svg' -print -quit 2>/dev/null | grep -q .; then
  log_warn "No SVG icons found in src/nova-dark/icons/modern"
  log_warn "Fetch them with: python src/nova-dark/scripts/download_phosphor_icons.py"
fi

mkdir -p "${DIST_DIR}"

log_info "Compiling NovaDark.scss"
(cd "${SOURCE_DIR}" && qtsass -o ../NovaDark.qss NovaDark.scss)

log_info "Packing nova-dark.qbtheme"
python "${SRC_ROOT}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -icons-dir "${ICONS_DIR}" \
  -include-dir "${COMMON_DIR}" \
  -output "${OUTPUT}" \
  -style NovaDark.qss

# In Docker the build runs as root, so artifacts written into the bind-mounted
# tree land root-owned and the host user cannot overwrite them on the next
# build. No-op for an ordinary non-root host build.
if [[ "$(id -u)" -eq 0 ]]; then
  chown -R "$(stat -c '%u:%g' "${PROJECT_ROOT}")" "${DIST_DIR}" 2> /dev/null || true
fi

log_done "${OUTPUT}.qbtheme"
