#!/usr/bin/env bash
set -euo pipefail

SRC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
PROJECT_ROOT="$(cd "${SRC_ROOT}/.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"

ensure_dist_dir() {
  mkdir -p "${DIST_DIR}"
}

run_build_script() {
  local script="$1"
  shift || true
  local script_path="${SRC_ROOT}/${script}"

  if [[ ! -f "${script_path}" ]]; then
    echo "[warn] Skipping missing build script: ${script}" >&2
    return 0
  fi

  if [[ ! -x "${script_path}" ]]; then
    chmod +x "${script_path}"
  fi

  echo "[info] Running ${script}"
  bash "${script_path}" "$@"
}
