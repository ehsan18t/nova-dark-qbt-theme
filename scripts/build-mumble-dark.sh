#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/build-support.sh"

THEME_DIR="${SRC_ROOT}/mumble-theme"
QSS_SOURCE="${THEME_DIR}/source"

TARGET_THEME="${1:-mumble-dark}"

if [[ "${TARGET_THEME}" != "mumble-dark" ]]; then
  log_error "Unsupported theme: ${TARGET_THEME}"
  exit 1
fi

ensure_dist_dir

# Compile SCSS to QSS
log_info "Compiling Dark.scss..."
pushd "${QSS_SOURCE}" > /dev/null
qtsass -o ../Dark.qss Dark.scss
popd > /dev/null

# Build with recolored icons
rm -rf "${THEME_DIR}/mumble-icons"
python "${SRC_ROOT}/fill-icons.py" nowshed "#4B9CD3" "${THEME_DIR}/mumble-icons"

python "${SRC_ROOT}/make-resource.py" \
  -base-dir "${THEME_DIR}/" \
  -find-files \
  -config "${SRC_ROOT}/dark-config.json" \
  -icons-dir "${THEME_DIR}/mumble-icons" \
  -output "${DIST_DIR}/mumble-dark-nowshed-recolored" \
  -style Dark.qss

rm -rf "${THEME_DIR}/mumble-icons"

# Build with original icons
python "${SRC_ROOT}/make-resource.py" \
  -base-dir "${THEME_DIR}/" \
  -find-files \
  -config "${SRC_ROOT}/dark-config.json" \
  -icons-dir "${THEME_DIR}/icons/nowshed" \
  -output "${DIST_DIR}/mumble-dark-nowshed" \
  -style Dark.qss
