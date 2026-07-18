#!/usr/bin/env bash
set -euo pipefail

WORKSPACE=${WORKSPACE:-/workspace}
BUILD_SCRIPT=${THEME_BUILD_SCRIPT:-build-all.sh}
TARGET="${WORKSPACE}/scripts/${BUILD_SCRIPT}"

if [[ ! -d "${WORKSPACE}/scripts" ]] || [[ ! -d "${WORKSPACE}/src" ]]; then
  cat >&2 <<'EOF'
[error] Expected to find the repository mounted at /workspace with src/ and scripts/ directories.
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

cd "${WORKSPACE}/scripts"
bash "${TARGET}" "$@"
status=$?

# The container runs as root, so anything written into the bind-mounted tree
# lands root-owned and the host user cannot overwrite it on their next build.
# Hand dist/ back to whoever owns the mount.
if [[ -d "${WORKSPACE}/dist" ]]; then
  chown -R "$(stat -c '%u:%g' "${WORKSPACE}")" "${WORKSPACE}/dist" 2>/dev/null || true
fi

exit "${status}"
