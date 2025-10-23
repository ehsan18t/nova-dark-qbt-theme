#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_ROOT="${ROOT_DIR}/modern-dark"
SRC_DIR="${THEME_ROOT}/source"
DIST_DIR="${ROOT_DIR}/dist"
ICONS_DIR="${THEME_ROOT}/icons/modern"
TEMP_ICONS_DIR="${THEME_ROOT}/.icons-recolored"
TEMP_COMMON_DIR="${ROOT_DIR}/.common-recolored"
CONFIG_FILE="${THEME_ROOT}/modern-dark-config.json"
OUTPUT_PREFIX="nova-dark"
COMMON_DIR="${ROOT_DIR}/common"
DEFINITIONS_FILE="${SRC_DIR}/Imports/Nova Definitions.scss"

mkdir -p "${DIST_DIR}"

if [[ ! -d "${ICONS_DIR}" ]] || [[ -z "$(find "${ICONS_DIR}" -maxdepth 1 -name '*.svg' -print -quit 2>/dev/null)" ]]; then
  cat >&2 <<'EOF'
[warn] No SVG icons detected in Builds/modern-dark/icons/modern
  Copy the Mumble Dark icon set here (or provide your own) before packaging.
EOF
fi

# Compile SCSS
pushd "${SRC_DIR}" > /dev/null
qtsass -o ../ModernDark.qss ModernDark.scss
popd > /dev/null

# Recolor icons based on theme accent color
echo "[info] Recoloring icons based on theme accent color..."
python "${ROOT_DIR}/recolor-icons.py" "${DEFINITIONS_FILE}" "${ICONS_DIR}" "${TEMP_ICONS_DIR}"
python "${ROOT_DIR}/recolor-icons.py" "${DEFINITIONS_FILE}" "${COMMON_DIR}/controls" "${TEMP_COMMON_DIR}/controls"

# Recolor icons based on theme accent color
echo "[info] Recoloring icons based on theme accent color..."
python "${ROOT_DIR}/recolor-icons.py" "${DEFINITIONS_FILE}" "${ICONS_DIR}" "${TEMP_ICONS_DIR}"
python "${ROOT_DIR}/recolor-icons.py" "${DEFINITIONS_FILE}" "${COMMON_DIR}/controls" "${TEMP_COMMON_DIR}/controls"

# Build with recolored icons
python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -icons-dir "${TEMP_ICONS_DIR}" \
  -include-dir "${TEMP_COMMON_DIR}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-modern" \
  -style ModernDark.qss

python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_ROOT}" \
  -find-files \
  -config "${CONFIG_FILE}" \
  -include-dir "${TEMP_COMMON_DIR}" \
  -output "${DIST_DIR}/${OUTPUT_PREFIX}-no-icons" \
  -style ModernDark.qss

# Cleanup temp directories
rm -rf "${TEMP_ICONS_DIR}" "${TEMP_COMMON_DIR}"
