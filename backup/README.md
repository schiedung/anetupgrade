# backup/

Pre-upgrade firmware/EEPROM captures, kept so the prior configuration is recoverable.

## spare-board-M115.txt / spare-board-M503.txt — not yet captured

Attempted from the Ubuntu host on 2026-08-02, connected via `/dev/ttyUSB0`. No usable
data was obtained:

- The board was USB-powered only (no 12V), which alone can cause unstable serial
  behavior.
- Independently, this host's `ch341` kernel driver cannot open Marlin's usual
  `250000` baud at all (missing `TCGETS2`/`TCSETS2` ioctl support for arbitrary baud
  rates — see `CLAUDE.md` → "Known Host Limitation: Ubuntu 26 LTS + CH340").
- At every baud rate the port *would* accept, reads returned only noise and `M115`/
  `M503` got no reply.

This capture is deferred to the Windows track (see the plan's Phase 1b) — connect the
spare board there with full 12V power and re-run `scripts/backup-serial.sh
spare-board <PORT> 250000` (e.g. `scripts/backup-serial.sh spare-board COM3 250000`).
Not blocking: the authoritative reference values for this modified frame come from
`production-board-M503.txt` (below), not from the spare board's own EEPROM.

## production-board-M115.txt / production-board-M503.txt — not yet captured

To be pulled via OctoPrint's Terminal tab (or REST API) from the currently-operating
board, without interrupting the running printer. This is the authoritative source for
steps/mm, PID, and acceleration values used in Phase 3/4 of the plan.
