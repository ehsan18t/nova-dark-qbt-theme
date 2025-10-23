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

for script in "${SCRIPTS[@]}"; do
  run_build_script "${script}"
done
