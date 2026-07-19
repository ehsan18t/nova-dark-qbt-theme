#!/usr/bin/env bash
#
# Thin launcher for build.py, which is the actual build. Kept so that
# ./scripts/build.sh and any existing habit or CI invocation still work.
#
# The build moved to Python because Python was never optional here --
# make-resource.py and generate-config.py are the build, and the toolchain image
# is python:3.11-slim -- whereas a shell script made Windows depend on Git Bash
# for nothing. Add logic to build.py, not to this file or to build.bat.
set -euo pipefail

# Execute each candidate rather than just locating it: on Windows `python` is
# frequently the Store alias stub, which satisfies `command -v` and then
# refuses to run.
for candidate in python3 python py; do
  if command -v "${candidate}" > /dev/null 2>&1 && "${candidate}" -c '' > /dev/null 2>&1; then
    exec "${candidate}" "$(dirname "${BASH_SOURCE[0]}")/build.py" "$@"
  fi
done

echo "[error] No working Python 3 found (tried python3, python, py)." >&2
echo "[error] Or build in Docker, which needs no local toolchain:" >&2
echo "[error]     docker compose run --rm build" >&2
exit 1
