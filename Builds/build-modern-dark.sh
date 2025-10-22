#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_ROOT="${ROOT_DIR}/modern-dark"
SRC_DIR="${THEME_ROOT}/source"
DIST_DIR="${ROOT_DIR}/dist"
ICONS_DIR="${THEME_ROOT}/icons/modern"
CONFIG_FILE="${THEME_ROOT}/modern-dark-config.json"
OUTPUT_PREFIX="nova-dark"

mkdir -p "${DIST_DIR}"

if [[ ! -d "${ICONS_DIR}" ]] || [[ -z "$(find "${ICONS_DIR}" -maxdepth 1 -name '*.svg' -print -quit 2>/dev/null)" ]]; then
  cat >&2 <<'EOF'
[warn] No SVG icons detected in Builds/modern-dark/icons/modern
  Copy the Mumble Dark icon set here (or provide your own) before packaging.
EOF
fi

pushd "${SRC_DIR}" > /dev/null
qtsass -o ../ModernDark.qss ModernDark.scss
popd > /dev/null

python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -icons-dir "${ICONS_DIR}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-modern" \
  -style ModernDark.qss

python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-no-icons" \
  -style ModernDark.qss
