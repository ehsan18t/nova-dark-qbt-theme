#!/usr/bin/env bash
set -euo pipefail

# Colors for output (disabled if not a terminal)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  NC='\033[0m' # No Color
else
  RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPTS_DIR}/.." && pwd)"
SRC_ROOT="${PROJECT_ROOT}/src"
DIST_DIR="${PROJECT_ROOT}/dist"

log_info()  { echo -e "${BLUE}[info]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[warn]${NC} $*" >&2; }
log_error() { echo -e "${RED}[error]${NC} $*" >&2; }
log_ok()    { echo -e "${GREEN}[done]${NC} $*"; }

ensure_dist_dir() {
  mkdir -p "${DIST_DIR}"
}

run_build_script() {
  local script="$1"
  shift || true
  local script_path="${SCRIPTS_DIR}/${script}"

  if [[ ! -f "${script_path}" ]]; then
    log_warn "Skipping missing build script: ${script}"
    return 0
  fi

  if [[ ! -x "${script_path}" ]]; then
    chmod +x "${script_path}"
  fi

  log_info "Running ${script}"
  bash "${script_path}" "$@"
}
