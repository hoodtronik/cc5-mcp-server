# hoodtronik fork: operating notes (CC5 5.05.1305 on Ilyas's PC)

Fork of MorphoCore-Pty-Ltd/cc5-mcp-server, adopted 2026-10-24. Upstream is the `upstream` remote.
Rule (Wan2GPHelper STARTUP_RULES 17b): if this MCP lacks something, add it here, verify live, push.

## Run it

```
python scripts/cc5_start.py          # launch CC5 if needed, dismiss its connection popup, wait for :5101
python scripts/cc5_start.py --reload # hot-reload cc5-plugin/cc5_api.py into the running CC5 (~1 s)
python scripts/live_smoke_test.py    # live check, mutates the scene (scratch only)
npm run build && npx vitest run      # TS layer
```

The plugin is installed as a junction: `C:\Program Files\Reallusion\Character Creator 5\Bin64\OpenPlugin\CC5_MCP_Bridge`
-> `cc5-plugin/` here (`install-plugin.ps1`, one UAC prompt). Repo edits are what CC5 loads.

## Eyes (see what is blocking CC5)

`python scripts/cc5_live_eyes.py` (run under a stream monitor) = live page http://127.0.0.1:8768 + EVENT lines:
popup_opened {texts, buttons, png}, hung/responsive, bridge_up/bridge_down, view_changed/still/blank.
`python scripts/cc5_live_eyes.py state` = one status line. Frames in `%TEMP%/cc5_live_eyes/` (latest.png = whole CC5 UI).
Wraps mc-iclone8-mcp/scripts/iclone_live_eyes.py (out of process, keeps working when CC5 is frozen).
Measured 2026-10-24: with CC5's "Unsaved project data found ... update your project?" box open, bridge commands
still run (Qt modal loop keeps the plugin's QTimer alive); the startup "Failed to establish a connection" box,
by contrast, stops the plugin from starting at all.

## Adding a tool (no CC5 restart)

Put the function in `cc5-plugin/cc5_api.py` and register it in `EXTRA_ACTIONS` + `EXTRA_GET_ROUTES` /
`EXTRA_POST_ROUTES` at the bottom of that file, then `cc5_start.py --reload`. Edits to `server.py` or `main.py`
still need a CC5 restart. Then add a bridge method (`src/cc5-bridge.ts`) and tool (`src/tools/*.ts`), update the
tool-count test, `npm run build`. The MCP client picks up new TS tools after an MCP restart (new session).

## Learned live (2026-10-24, newest first)

- **Preview Camera cannot be aimed from Python on 5.05.** No `ECameraLocationType_*`/`SetCameraLocation`
  (so upstream `frame_camera` always fails), `GetControl("Transform")` and every `GetDataBlock` key return None,
  and `AlignTo(helper prop, any EAlignAxis)` returns Failure. Loading a `.ccCam` preset DOES move it (it replaces
  the preview camera) -> `camera_preset` tool uses the shipped Headshot Ref presets (left/right profiles).
  Front face close-up = open: needs a writer for `.ccCam` (`_RLZeus` container) or a camera that has a transform.
- Camera axes: `WorldTransform().R().ToRotationMatrix()` rows = right, up, back (looks down -back). Avatar faces -Y, Z up, cm.
- **CC5's virtual `$/Cloth/...` folders list nothing** although `F:/iCLONE/Reallusion Templates/Cloth` holds ~230
  garments; `$` is a merged view (its `$/Actor/Character` subfolders differ from the F: folder). `browse_content`
  now recurses subfolders and falls back to walking the real Templates + Custom folders on disk.
  Content roots: Templates `F:/iCLONE/Reallusion Templates`, Custom `F:/iCLONE/Reallusion Custom`.
- **Startup popup blocks the plugin:** "Failed to establish a connection due to unknown error" (OK only). Until
  it is dismissed the bridge never starts. With it handled, CC5 is ready in ~25 s.
- Loading garments onto an empty scene works (`.ccCloth`, `.ccShoes` via `load_asset`); CC5 supplies the
  CC3_Base_Plus avatar. Viewport capture works with no one at the screen (as long as Windows is unlocked).
- `capture_viewport` returns the PNG as base64 in the response (~1.5 MB); pass `output_path` and ignore it.
