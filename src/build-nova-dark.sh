#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_ROOT="${ROOT_DIR}/nova-dark"
SRC_DIR="${THEME_ROOT}/source"
DIST_DIR="${ROOT_DIR}/dist"
ICONS_DIR="${THEME_ROOT}/icons/modern"
CONFIG_FILE="${THEME_ROOT}/nova-dark-config.json"
OUTPUT_PREFIX="nova-dark"
COMMON_DIR="${ROOT_DIR}/common"

mkdir -p "${DIST_DIR}"

if [[ ! -d "${ICONS_DIR}" ]] || [[ -z "$(find "${ICONS_DIR}" -maxdepth 1 -name '*.svg' -print -quit 2>/dev/null)" ]]; then
  cat >&2 <<'EOF'
[warn] No SVG icons detected in src/nova-dark/icons/modern
  Copy the Mumble Dark icon set here (or provide your own) before packaging.
EOF
fi

pushd "${SRC_DIR}" > /dev/null
qtsass -o ../NovaDark.qss NovaDark.scss
popd > /dev/null

python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -icons-dir "${ICONS_DIR}" \
  -include-dir "${COMMON_DIR}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-modern" \
  -style NovaDark.qss

python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -include-dir "${COMMON_DIR}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-no-icons" \
  -style NovaDark.qss
