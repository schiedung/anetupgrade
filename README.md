# ANet A8 — Marlin 2.1.2.8 Firmware Upgrade

Firmware migration for a heavily modified ANet A8 from its original firmware to
Marlin 2.1.2.8, on the existing RAMPS 1.4 / Mega2560 electronics. See `CLAUDE.md` for
the full project brief, hardware assumptions, and behavior rules this project follows.

## Current Hardware Configuration

| | |
|---|---|
| Printer | ANet A8, heavily modified frame |
| Controller | RAMPS 1.4 |
| MCU | Arduino Mega2560 (`BOARD_RAMPS_14_EFB`) |
| Stepper drivers | FYSETC TMC2100, standalone STEP/DIR mode (no UART/SPI) — current set via onboard trimpot, microstepping via MS jumpers |
| Z axis | Two Z motors wired **in parallel to a single Z driver** — not `Z_DUAL_STEPPER_DRIVERS`, Marlin sees one Z axis |
| Display | RepRapDiscount Full Graphic Smart Controller (`REPRAP_DISCOUNT_FULL_GRAPHIC_SMART_CONTROLLER`) |
| SD card | Used, in addition to OctoPrint (`SDSUPPORT` enabled) |
| Extruder | Single extruder, heated bed, heated nozzle |
| Host control | OctoPrint on a Raspberry Pi, over USB, driving the **production** board |
| This project's target | A second, **identical spare board** — built/flashed/bench-verified independently, then physically swapped in to replace the production board |

Endstops are assumed stock (3x mechanical, X/Y/Z min) — **not yet physically
reconfirmed** on the modified frame; verify before relying on it.

## Marlin Version

**2.1.2.8** — latest stable release as of 2026-08-02 (2.1.3 only exists as beta tags,
not used). Vendored into `Marlin/` from `MarlinFirmware/Marlin` at git tag `2.1.2.8`.

Config baseline: `MarlinFirmware/Configurations` branch `release-2.1.2.8`, path
`config/examples/Anet/A8/` — the Anet A8 example is used as documented starting point
(per `CLAUDE.md`), then adapted for RAMPS 1.4 / TMC2100 / this frame's actual hardware.

## Repository Layout

```
Marlin/                    Vendored Marlin 2.1.2.8 source (de-nested — this repo
                            tracks it directly, not as a git submodule). This is also
                            the PlatformIO project root; platformio.ini and
                            Marlin/Marlin/Configuration*.h live here and are the
                            files actually built/flashed.
config/
  anet-a8-baseline/        Pristine Anet/A8 example config, untouched, for diffing.
  customized/              Synced snapshot of the working Configuration.h /
                            Configuration_adv.h / _Statusscreen.h for review outside
                            the vendored tree — always copy changes here too after
                            editing Marlin/Marlin/Configuration*.h.
build/                     Archived .hex builds, timestamped (gitignored — binaries).
backup/                    Pre-upgrade firmware/EEPROM captures (see backup/README.md).
scripts/
  backup_serial.py         Captures M115/M503 from a board over serial.
  backup-serial.sh         Wrapper: scripts/backup-serial.sh <prefix> [port] [baud]
  build.sh                 pio run -e mega2560, archives the resulting .hex into build/
  flash.sh                 pio run -e mega2560 -t upload [port]
```

## Build Instructions

```
pip3 install --user platformio   # one-time
./scripts/build.sh
```

Builds the `mega2560` PlatformIO environment and copies the resulting
`firmware-<timestamp>.hex` into `build/`. Current build: RAM 56.3% (4611/8192 B),
Flash 45.4% (115210/253952 B), zero compiler warnings.

Compiling does **not** require serial/USB access to a board, so it works fine from
either OS (see "Known Limitations" below for why flashing does not).

## Flash Procedure

1. Run through the pre-flash safety checklist (mains power disconnected, bed can't
   accidentally heat, e-stop available).
2. `./scripts/flash.sh [port]` (defaults to `/dev/ttyUSB0`; pass a `COM*` port on
   Windows and run the equivalent `pio run -e mega2560 -t upload --upload-port COMx`
   if not using Git Bash/WSL).
3. Bench-verify in this order before trusting the board: LCD comms → endstop
   direction → motor directions → extruder direction → temperature readings → heating
   elements → full print movement. **Never heat before temperature readings are
   verified.**
4. Only after bench verification passes: power off the printer, swap this board in to
   replace the production board, reconnect to the Raspberry Pi, and update OctoPrint's
   serial port/baud settings to match.

## Known Limitations

- **This project's spare board is a fresh Marlin config, not yet flashed or
  bench-tested.** Steps/mm (`DEFAULT_AXIS_STEPS_PER_UNIT`), bed size, and travel
  limits in `Marlin/Marlin/Configuration.h` are still the **stock Anet A8 example
  values**, marked `TODO: UNVERIFIED` in the source — the production board's real
  tuned values (via `M503`) were not captured yet (skipped by choice during setup).
  **Do not flash this to replace the production board without correcting these
  first**, either from a fresh `M503` capture off the production board via OctoPrint,
  or by direct measurement.
- **Ubuntu 26 LTS on this machine cannot reliably do direct serial I/O with these
  boards.** Two distinct causes found:
  1. The in-kernel `ch341` driver here doesn't support the ioctl needed for
     arbitrary baud rates, so Marlin's usual `250000` baud can't be opened at all
     from this port on this OS (not fixable from userspace).
  2. Reads returned persistent noise at every baud the port *would* accept, with the
     board only USB-powered (no 12V) — try again with full power before assuming a
     given rate doesn't work.

  **Net effect: do all firmware backup, flashing, and bench serial verification from
  the Windows side of this machine's dual boot instead** (see `CLAUDE.md` → "Known
  Host Limitation" for detail). Source/config editing and compiling are unaffected
  and were done on Linux. OctoPrint's web UI is also unaffected, since the actual
  serial link is between the Raspberry Pi and the board, not this PC.
- Endstop count/type on the modified frame is assumed stock (not yet physically
  reconfirmed).
- Auto bed leveling, probes, sensorless homing, and other advanced motion features
  are intentionally left disabled, per `CLAUDE.md` — this is a firmware migration
  only, no hardware changes.

## Rollback

The original production board is kept aside, untouched, after the physical swap —
an instant rollback if the new board misbehaves. Its firmware/EEPROM state should be
captured to `backup/production-board-M115.txt` / `-M503.txt` via OctoPrint's Terminal
tab before the swap (see `backup/README.md`); this had not been done as of this
writing.
