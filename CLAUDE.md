# CLAUDE.md — ANet A8 Marlin Firmware Upgrade Project

## Project Goal

Upgrade the firmware of an ANet A8 3D printer electronics setup.

Target hardware:

- Printer: ANet A8 (heavily modified mechanical frame)
- Controller: RAMPS 1.4
- Main MCU: Arduino Mega 2560
- Firmware target: Marlin 2.1.x
- Development host: Linux (Ubuntu 26 LTS) for repo/source/config work; Windows
  (dual-boot on the same machine) for anything that talks to the boards over serial —
  see "Known Host Limitation" below.
- Connection: USB serial

This project initially targets firmware migration only.
Do NOT add automatic bed leveling, probes, or hardware changes unless explicitly requested.

---

# Hardware Configuration

## Controller

Board:
- RAMPS 1.4

MCU:
- ATmega2560

Expected Marlin environment:
- BOARD_RAMPS_14_EFB or equivalent

Printer type:
- Cartesian
- Bed moves in Y direction
- X carriage moves horizontally
- Z axis uses two motors

Default extruder setup:
- Single extruder
- Heated bed
- Heated nozzle

---

# Firmware Objectives

The firmware upgrade must prioritize:

1. Safety
2. Stability
3. Compatibility
4. Maintainability

Enable:

- Thermal runaway protection
- EEPROM support
- PID temperature control
- Software endstops
- SD card support if available
- Accurate stepper configuration
- Proper acceleration limits

Avoid experimental features unless requested.

---

# Development Workflow

## Repository Setup

Create a clean Marlin workspace.

Expected structure:

```
project/
├── Marlin/
├── config/
├── build/
└── scripts/
```

Keep all custom configuration changes version controlled.

Never directly modify the upstream Marlin source if avoidable.

Use:

- Configuration.h
- Configuration_adv.h
- platformio.ini

---

# Required Tools

Install:

- git
- python3
- python3-pip
- PlatformIO

Preferred build method:

PlatformIO CLI

Example:

```
pio run
```

Upload:

```
pio run -t upload
```

---

# Configuration Strategy

Start from official Marlin example:

```
Marlin/config/examples/Anet/A8/
```

Adapt for:

- RAMPS 1.4 electronics
- ATmega2560
- Existing printer dimensions

Do not blindly copy old ANet firmware configurations.

---

# Initial Configuration Requirements

Before compiling:

Set:

```
MOTHERBOARD BOARD_RAMPS_14_EFB
```

Enable:

```
EEPROM_SETTINGS
```

Enable:

```
THERMAL_PROTECTION_HOTENDS
THERMAL_PROTECTION_BED
```

Enable:

```
PIDTEMP
PIDTEMPBED
```

Disable initially:

- Auto bed leveling
- Probe support
- Advanced motion features
- Sensorless homing

---

# Build Process

For every change:

1. Modify configuration
2. Compile firmware
3. Check compiler warnings/errors
4. Only then upload

Never upload untested firmware to the printer.

---

# Safety Rules

Before flashing:

Confirm:

- Printer is disconnected from mains power except USB
- Heated bed cannot accidentally activate
- Emergency stop method is available

After flashing:

Test in this order:

1. LCD/display communication
2. Endstop direction
3. Motor directions
4. Extruder direction
5. Heater temperature readings
6. Heating elements
7. Full print movement

Never heat the printer before verifying temperature sensors.

---

# Backup Existing Firmware

Before changing anything:

Attempt to document:

- Existing firmware version
- Current EEPROM values
- Steps/mm
- PID values
- Acceleration settings

Useful commands:

```
M115
M503
```

Save output into:

```
backup/
```

---

# Serial Debugging

Expected serial connection:

Linux device examples:

```
/dev/ttyACM0
/dev/ttyUSB0
```

Typical baud rates:

```
115200
250000
```

If communication fails:

Check:

- USB cable
- CH340 driver
- Arduino serial device
- Marlin baud rate

## Known Host Limitation: Ubuntu 26 LTS + CH340

This machine's in-kernel `ch341` driver cannot reliably talk to the RAMPS boards:

- `250000` baud (Marlin's usual default) cannot be opened at all — it requires the
  `TCGETS2`/`TCSETS2` ioctl for arbitrary baud rates, which this driver returns
  `ENOTTY` for. This is a driver limitation, not fixable from userspace/Python.
- Even at baud rates the port will accept (9600–230400), reads returned persistent
  garbage with no board previously power (only USB, no 12V) — worth retrying with
  full power before concluding a given baud doesn't work, but don't assume it will.

Net effect: **do not attempt firmware backup, flashing, or bench serial verification
from this Ubuntu install.** Do that work from the Windows side of this machine's dual
boot instead (its CH340 driver handles this fine). Source/config prep and compiling
(`pio run` without `-t upload`) are unaffected and should stay on Linux — only steps
that open the serial port need Windows. OctoPrint's web UI is also unaffected, since
the actual serial link is between the Raspberry Pi and the board, not this PC.

---

# Future Upgrade Preparation

Leave room for future features:

Possible later additions:

- CR Touch / BLTouch
- Filament sensor
- TMC stepper drivers
- Display upgrade
- Dual Z improvements

Do not enable these until hardware is confirmed.

---

# Documentation Requirements

Maintain:

```
README.md
```

containing:

- Current hardware configuration
- Marlin version
- Build instructions
- Flash procedure
- Known limitations

Every hardware change must update documentation.

---

# Claude Behavior Rules

When assisting:

- Prefer reversible changes.
- Explain hardware assumptions before changing configuration.
- Ask for confirmation before enabling new hardware features.
- Do not assume components are present.
- Avoid replacing the controller unless there is a clear technical reason.
- Treat the printer as experimental hardware.

The goal is a reliable, documented Marlin upgrade on existing RAMPS 1.4 electronics.
