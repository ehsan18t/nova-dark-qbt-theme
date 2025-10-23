#!/usr/bin/env bash
set -euo pipefail

WORKSPACE=${WORKSPACE:-/workspace}
BUILD_SCRIPT=${THEME_BUILD_SCRIPT:-build-all.sh}
TARGET="${WORKSPACE}/Builds/${BUILD_SCRIPT}"

if [[ ! -d "${WORKSPACE}/Builds" ]]; then
  cat >&2 <<'EOF'
[error] Expected to find the repository mounted at /workspace.
        Run the container with -v ${PWD}:/workspace.
EOF
  exit 1
fi

if [[ ! -f "${TARGET}" ]]; then
  cat >&2 <<EOF
[error] Build script ${TARGET} not found.
        Set THEME_BUILD_SCRIPT or mount the project root to /workspace.
EOF
  exit 2
fi

mkdir -p "${WORKSPACE}/Builds/tools"
ln -sf "$(command -v rcc)" "${WORKSPACE}/Builds/tools/rcc"

cd "${WORKSPACE}/Builds"
exec bash "${TARGET}" "$@"
