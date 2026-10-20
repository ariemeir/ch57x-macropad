# Keyboards handoff

Repo: https://github.com/ariemeir/ch57x-macropad (public; holds both pads despite the name).
Device docs: `ch57x-macropad/README.md`, `doio-macropad/README.md`.
Live Karabiner config: `~/dev/config/karabiner/` (tracked in the private config repo; `~/.config/karabiner` symlinks to it).

## State (2026-10-21)

- ch57x pad: unchanged behavior; moved from `diy/gadgets/macropad` to `keyboards/ch57x-macropad`.
  All path references updated (live karabiner.json, dictation config, portfolio handoff, projects.json).
- DOIO KB16: stock firmware, Karabiner rule "DOIO KB16 → scripts" (source `doio-macropad/kb16.json`).
  - Big dial CW / CCW / press (Ctrl+Shift+Z / Ctrl+Z / Ctrl+S) → light2 brighten / dim / toggle. Tested by user.
  - Bottom-left key (`y`) → Hyper+F13, dictation like the foot pedal. Not yet confirmed by user.
  - Top-right key (`delete_forward`) → `cornerlight toggle` (2026-10-21). Tested: ~1 s.
    Script: `~/dev/diy/gadgets/tapo-cameras/cornerlight on|off|toggle|state` (P105 at 192.168.1.12,
    direct kasa KLAP, no Shortcuts needed unlike the laser). Shell alias in `~/dev/config/dotfiles/.zshrc`.
  - Bottom-right key (`t`) → `laser toggle`, logs to `/tmp/kb16-laser.log`. Tested: ~7 s per press.
- KB16 RGB: turn off via VIA (usevia.app in Chrome) → Lighting → brightness 0 or effect off.
  Stored on the keyboard. May need DOIO's KB16 VIA JSON loaded via the Design tab. Not done yet.

## Open

- KB16 stickers (2026-10-21): `doio-macropad/stickers/` has `sticker_test.xcs` and `stickers.xcs`.
  Run the test first, then set ENGRAVE/CUT in `make_stickers.py` and regenerate. Not run yet.

- Dial step: ~2 events per detent, so ~10% per click. Halve the step in `dial_cw.sh`/`dial_ccw.sh` if 5% wanted.
- Laser key: no Accessibility or Local Network change needed (all steps verified from Karabiner).
  Earlier 20-40 s delays were likely a slow plug plus overlapping presses; press once and wait.
- Rotate the Tapo account password (it was printed in a debug trace on 2026-10-20).
- Consider renaming the GitHub repo to `keyboards`.

## How to find KB16 key codes

Temporary Karabiner rule scoped to the KB16 with one manipulator per key and per mandatory modifier
combo, each `echo <name> >> /tmp/kb16-keys.log`. Don't map bare modifier keys in it. Details in
`doio-macropad/README.md`.
