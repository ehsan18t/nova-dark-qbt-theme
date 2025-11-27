#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/build-support.sh"

SCRIPTS=("$@")
if [[ ${#SCRIPTS[@]} -eq 0 ]]; then
  SCRIPTS=(
    "build-mumble-dark.sh"
    "build-nova-dark.sh"
  )
fi

START_TIME=$(date +%s)

for script in "${SCRIPTS[@]}"; do
  run_build_script "${script}"
done

END_TIME=$(date +%s)
echo ""
echo "[done] All themes built in $((END_TIME - START_TIME))s → ${DIST_DIR}/"
