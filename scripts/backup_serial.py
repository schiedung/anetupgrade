#!/usr/bin/env python3
"""Capture M115 (firmware info) and M503 (EEPROM settings) from a Marlin
board over serial, and save the raw responses to backup/<prefix>-M115.txt
and backup/<prefix>-M503.txt.

Usage:
    scripts/backup_serial.py <prefix> [--port /dev/ttyUSB0] [--baud 250000]

Example:
    scripts/backup_serial.py spare-board
    scripts/backup_serial.py production-board --port /dev/ttyACM0 --baud 115200
"""
import argparse
import datetime
import pathlib
import sys
import time

import serial

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
BACKUP_DIR = REPO_ROOT / "backup"


def query(ser: serial.Serial, command: str, settle_s: float = 2.0) -> str:
    ser.reset_input_buffer()
    ser.write((command + "\n").encode("ascii"))
    ser.flush()
    time.sleep(settle_s)
    chunks = []
    while ser.in_waiting:
        chunks.append(ser.read(ser.in_waiting))
        time.sleep(0.1)
    return b"".join(chunks).decode("ascii", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prefix", help="Output filename prefix, e.g. 'spare-board'")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=250000)
    parser.add_argument("--boot-wait", type=float, default=3.0,
                         help="Seconds to wait after opening the port for the "
                              "board to finish its auto-reset/boot sequence")
    args = parser.parse_args()

    BACKUP_DIR.mkdir(exist_ok=True)

    print(f"Opening {args.port} @ {args.baud}...")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"ERROR: could not open {args.port}: {e}", file=sys.stderr)
        return 1

    # Opening the port toggles DTR on most Arduino-compatible boards, which
    # resets the Mega2560 and restarts Marlin. Give it time to boot and print
    # its startup banner before sending commands.
    time.sleep(args.boot_wait)
    ser.reset_input_buffer()

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    header = f"# Captured {timestamp} from {args.port} @ {args.baud}\n\n"

    m115 = query(ser, "M115")
    m503 = query(ser, "M503")
    ser.close()

    if not m115.strip():
        print("WARNING: M115 returned no data — board may not have booted "
              "Marlin, or the baud rate is wrong.", file=sys.stderr)
    if not m503.strip():
        print("WARNING: M503 returned no data — EEPROM may be empty/unset, "
              "or the baud rate is wrong.", file=sys.stderr)

    m115_path = BACKUP_DIR / f"{args.prefix}-M115.txt"
    m503_path = BACKUP_DIR / f"{args.prefix}-M503.txt"
    m115_path.write_text(header + m115)
    m503_path.write_text(header + m503)

    print(f"Wrote {m115_path}")
    print(f"Wrote {m503_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
