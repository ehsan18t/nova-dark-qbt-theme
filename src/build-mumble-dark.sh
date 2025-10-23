#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_DIR="${ROOT_DIR}/mumble-theme"
QSS_SOURCE="${THEME_DIR}/source"
DIST_DIR="${ROOT_DIR}/dist"

TARGET_THEME="${1:-mumble-dark}"

if [[ "${TARGET_THEME}" != "mumble-dark" ]]; then
  echo "Unsupported theme: ${TARGET_THEME}" >&2
  exit 1
fi

mkdir -p "${DIST_DIR}"

pushd "${QSS_SOURCE}" > /dev/null
qtsass -o ../Dark.qss Dark.scss
popd > /dev/null

rm -rf "${THEME_DIR}/mumble-icons"
python "${ROOT_DIR}/fill-icons.py" nowshed "#4B9CD3" "${THEME_DIR}/mumble-icons"

python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_DIR}/" \
  -find-files \
  -config "${ROOT_DIR}/dark-config.json" \
  -icons-dir "${THEME_DIR}/mumble-icons" \
  -output "${DIST_DIR}/mumble-dark-nowshed-recolored" \
  -style Dark.qss

rm -rf "${THEME_DIR}/mumble-icons"

python "${ROOT_DIR}/make-resource.py" \
  -base-dir "${THEME_DIR}/" \
  -find-files \
  -config "${ROOT_DIR}/dark-config.json" \
  -icons-dir "${THEME_DIR}/icons/nowshed" \
  -output "${DIST_DIR}/mumble-dark-nowshed" \
  -style Dark.qss
