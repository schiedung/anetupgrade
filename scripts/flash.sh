#!/usr/bin/env bash
# Flash the built firmware to the board. Run scripts/build.sh first and
# review it for warnings/errors — this script does not rebuild.
#
# Safety: confirm before running (see CLAUDE.md pre-flash checklist):
#   - printer is disconnected from mains power except USB
#   - heated bed cannot accidentally activate
#   - an emergency-stop method (e.g. pulling USB) is available
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d Marlin ]; then
    echo "ERROR: Marlin/ not found — run Phase 2 (fetch Marlin source) first." >&2
    exit 1
fi

port="${1:-/dev/ttyUSB0}"
cd Marlin
pio run -e mega2560 -t upload --upload-port "$port"
