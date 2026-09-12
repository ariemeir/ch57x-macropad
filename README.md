# ch57x Macropad

How to set up a low-cost AliExpress 3-key and 1-knob macropad (CH57x-based) on
macOS. The vendor configuration software only runs on Windows, so this repo
replaces it. An open-source flasher writes key codes into the pad, and
Karabiner-Elements turns those key codes into shell scripts.

Device: USB VID:PID `1189:8890` (decimal `4489:34960`).

## The hardware

**[Mini Keyboard 3 Keys 1 Knob RGB](https://www.aliexpress.us/item/3256806659987911.html)**
on AliExpress, about 850 JPY. Any CH57x pad with the same VID:PID should work
the same way. This is the one this setup was built and tested with.

<p align="center">
  <img src="docs/images/aliexpress-listing.png" width="860"
       alt="The AliExpress listing for a 3-key, 1-knob mechanical macropad in black and beige, with the product itself outlined in a blue box.">
  <br>
  <em>The pad used here, outlined in blue: three mechanical keys, one rotary
  knob, USB-C, and RGB backlighting.</em>
</p>

## How it works

Two layers, kept separate:

1. **Firmware layer** — the pad is flashed so its buttons and knob emit
   otherwise-unused function keys (F19–F24), nothing more. Done with
   [`ch57x-keyboard-tool`](https://github.com/kriomant/ch57x-keyboard-tool).
2. **Mac layer** — Karabiner-Elements catches those F-keys, scoped to this
   device only, and runs a script per key.

Because the pad only sends key codes, you change what a key does by editing a
script. You do not need to re-flash the pad.

## Mapping

| Input        | Emits | Script          |
|--------------|-------|-----------------|
| Left button  | F20   | `left.sh`       |
| Middle button| F21   | `middle.sh`     |
| Right button | F22   | `right.sh`      |
| Knob CCW     | F23   | `knob_down.sh`  |
| Knob CW      | F24   | `knob_up.sh`    |
| Knob press   | F19   | `knob_press.sh` |

F19–F24 are used because macOS has no default action bound to them. Avoid
F13–F15: F14 and F15 are legacy brightness keys, and macOS handles them before
Karabiner sees them.

## Flashing the pad

The pad must be connected by USB cable (not wireless) while flashing.

```zsh
# re-download the binary if it's not present (it's gitignored):
#   https://github.com/kriomant/ch57x-keyboard-tool/releases  (universal-apple-darwin)
xattr -dr com.apple.quarantine ch57x-keyboard-tool
chmod +x ch57x-keyboard-tool

./ch57x-keyboard-tool validate < mapping.yaml
sudo ./ch57x-keyboard-tool upload < mapping.yaml
```

`sudo` is required (raw USB). The command exits silently on success. Replug the
pad afterward. All three firmware layers are defined identically in
`mapping.yaml` so the active layer never matters.

## Karabiner rule

`macropad.json` is the rule. It lives here and is symlinked into Karabiner's
assets folder:

```zsh
ln -s "$PWD/macropad.json" \
  ~/.config/karabiner/assets/complex_modifications/macropad.json
```

Enable it once in the UI: Karabiner-Elements → Complex Modifications →
Add predefined rule → "Macropad → scripts" → Enable.

**Important:** the assets folder is only the menu. Enabling copies the rule into
`~/.config/karabiner/karabiner.json`, and that copy is what actually runs.
Editing `macropad.json` here does not auto-apply — either edit
`karabiner.json` directly (it hot-reloads on save) or remove and re-add the
rule in the UI.

## Writing the scripts

Karabiner runs `shell_command` in a minimal environment: no `.zshrc` and a
bare PATH. A script that works in your terminal may do nothing here, with no
error message.

- Use absolute paths for every binary (`/opt/homebrew/bin/...`).
- No shell env vars — read secrets from a file, don't rely on exported creds.
- Debug by adding to the top of a script:
  ```zsh
  exec >> /tmp/macropad.log 2>&1
  ```
  then run `tail -f /tmp/macropad.log` while pressing keys. This tells you
  whether the script never ran, or ran and failed.

## If Karabiner keys are seen but nothing runs

Symptom: EventViewer shows the F-key arriving, the rule is enabled, but the
script never fires, and `~/.local/share/karabiner/log/console_user_server.log`
repeats `connect_failed: No such file or directory`.

Cause: Karabiner's socket tree under
`/Library/Application Support/org.pqrs/tmp/` was never built (only
`karabiner_machine_identifier.json` present, no `user/` or `rootonly/`).

Fix: **reboot.** The socket tree is built on a clean start; a driver activated
by hand after first launch leaves it half-initialized. If a reboot alone
doesn't do it, `brew reinstall --cask karabiner-elements` then reboot.

## Files

- `mapping.yaml` — firmware key map (flashed onto the pad)
- `macropad.json` — Karabiner rule (symlinked into `~/.config/karabiner/...`)
- `*.sh` — one handler per input
- `example-mapping.yaml` — reference map shipped with the tool
- `ch57x-keyboard-tool` — the flasher binary (gitignored; re-download)
