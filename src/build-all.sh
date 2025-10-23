#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_builder() {
  local script="$1"
  if [[ ! -x "${ROOT_DIR}/${script}" ]]; then
    if [[ -f "${ROOT_DIR}/${script}" ]]; then
      chmod +x "${ROOT_DIR}/${script}"
    else
      echo "[warn] Skipping missing build script: ${script}" >&2
      return
    fi
  fi

  echo "[info] Running ${script}"
  bash "${ROOT_DIR}/${script}"
}

run_builder "build-mumble-dark.sh"
run_builder "build-nova-dark.sh"
