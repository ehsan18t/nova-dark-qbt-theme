#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/build-support.sh"

THEME_ROOT="${SRC_ROOT}/nova-dark"
SRC_DIR="${THEME_ROOT}/source"
ICONS_DIR="${THEME_ROOT}/icons/modern"
CONFIG_FILE="${THEME_ROOT}/nova-dark-config.json"
OUTPUT_PREFIX="nova-dark"
COMMON_DIR="${SRC_ROOT}/common"

ensure_dist_dir

# Check for icons
if [[ ! -d "${ICONS_DIR}" ]] || [[ -z "$(find "${ICONS_DIR}" -maxdepth 1 -name '*.svg' -print -quit 2>/dev/null)" ]]; then
  log_warn "No SVG icons detected in src/nova-dark/icons/modern"
fi

# Compile SCSS to QSS
log_info "Compiling NovaDark.scss..."
pushd "${SRC_DIR}" > /dev/null
qtsass -o ../NovaDark.qss NovaDark.scss
popd > /dev/null

# Build theme with icons
python "${SRC_ROOT}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -icons-dir "${ICONS_DIR}" \
  -include-dir "${COMMON_DIR}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-modern" \
  -style NovaDark.qss

# Build theme without icons
python "${SRC_ROOT}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -include-dir "${COMMON_DIR}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-no-icons" \
  -style NovaDark.qss
