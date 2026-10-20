# DOIO macropad (KB16)

DOIO KB16 (https://www.amazon.co.jp/dp/B0CXXY4JP8), USB vendor 53264 (0xd010),
product 5633 (0x1601). Sibling of `../ch57x-macropad`. Stock firmware, no flashing:
Karabiner-Elements catches the stock key codes, scoped to this device only, and runs a
script per input. Other KB16 keys keep their stock behavior.

## Mapping (2026-10-20)

| Input (big dial)  | Stock emits      | Script                | Action              |
|-------------------|------------------|-----------------------|---------------------|
| Dial CW           | Ctrl+Shift+Z     | `dial_cw.sh`          | `light2 brighten`   |
| Dial CCW          | Ctrl+Z           | `dial_ccw.sh`         | `light2 dim`        |
| Dial press        | Ctrl+S           | `dial_press.sh`       | `light2 toggle`     |
| Bottom-left key   | `y`              | (none, key remap)     | dictation: Hyper+F13, same as the foot pedal |
| Bottom-right key  | `t`              | `key_bottom_right.sh` | `laser toggle` (xtool laser plug), logs to `/tmp/kb16-laser.log` |

Step is light2's default, 5 per event. The dial sends about 2 events per detent, so
one detent moves roughly 10%. Pass a step (`light2 brighten 3`) in the scripts to change it.

## Karabiner rule

`kb16.json` is the rule, symlinked into `~/dev/config/karabiner/assets/complex_modifications/`.
The live copy is in `~/dev/config/karabiner/karabiner.json` ("DOIO KB16 → scripts"); edit
both, then reload (see `~/dev/config/karabiner/README.md`). The KB16 must stay listed under
`devices` with `ignore: false` (keys arrive on its keyboard+pointing interface).

## Finding key codes

EventViewer works, but modifiers are easy to miss. What worked: a temporary Karabiner rule
scoped to the KB16 with one manipulator per key and per mandatory modifier combo, each
running `echo <name> >> /tmp/kb16-keys.log`. Don't also map bare modifier keys in that
logger, or they get eaten and every combo logs as the bare key.
