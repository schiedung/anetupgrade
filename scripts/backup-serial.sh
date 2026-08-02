#!/usr/bin/env bash
# Thin wrapper around backup_serial.py — see that file for details.
# Usage: scripts/backup-serial.sh <prefix> [port] [baud]
set -euo pipefail
cd "$(dirname "$0")/.."

prefix="${1:?Usage: $0 <prefix> [port] [baud]}"
port="${2:-/dev/ttyUSB0}"
baud="${3:-250000}"

python3 scripts/backup_serial.py "$prefix" --port "$port" --baud "$baud"
