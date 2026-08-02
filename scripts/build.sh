#!/usr/bin/env bash
# Build the firmware for the RAMPS 1.4 / Mega2560 target and archive the
# resulting binary into build/ with a timestamped name.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d Marlin ]; then
    echo "ERROR: Marlin/ not found — run Phase 2 (fetch Marlin source) first." >&2
    exit 1
fi

cd Marlin
pio run -e mega2560
cd ..

timestamp="$(date +%Y%m%d-%H%M%S)"
hex_src="Marlin/.pio/build/mega2560/firmware.hex"
if [ -f "$hex_src" ]; then
    cp "$hex_src" "build/firmware-${timestamp}.hex"
    echo "Archived: build/firmware-${timestamp}.hex"
else
    echo "WARNING: expected firmware.hex not found at $hex_src" >&2
fi
