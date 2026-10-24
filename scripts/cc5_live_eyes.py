"""REAL-TIME CC5 eyes: live view of the Character Creator 5 window + an event stream, running OUTSIDE CC5 (keeps
working when a modal popup freezes CC5 or stops the MCP bridge from starting).

  python scripts/cc5_live_eyes.py                 # live page http://127.0.0.1:8768 + EVENT lines on stdout
  python scripts/cc5_live_eyes.py state           # one JSON status line from a running watcher
  python scripts/cc5_live_eyes.py clip 10 out.mp4 # last 10 s as mp4

Events: started / iclone_running (= CC5 running) / iclone_exited / hung / responsive / bridge_up / bridge_down /
popup_opened {title, texts, buttons, png} / popup_closed / view_changed / view_still / view_blank.
Files: %TEMP%/cc5_live_eyes/latest.png, ring/*.png, state.json, popup_<hwnd>.png.

# CLAUDE-NOTE (2026-10-24): Ilyas: "make eyes for yourself in cc5 so you can see whats blocking you". Thin wrapper
# over mc-iclone8-mcp/scripts/iclone_live_eyes.py (same Reallusion Qt app family; generalized with --process /
# --health-url). Port 8768 so it can run beside the iClone eyes on 8767. The bridge check is the CC5-specific part:
# measured 2026-10-24 that CC5's startup "Failed to establish a connection" box keeps the plugin down while the main
# window looks normal - bridge_down + popup_opened together name the blocker.
"""
import os
import sys
import tempfile

ICLONE_MCP = os.environ.get("ICLONE_MCP_DIR", r"G:\_AI_Agents\mc-iclone8-mcp")
sys.path.insert(0, os.path.join(ICLONE_MCP, "scripts"))
import iclone_live_eyes  # noqa: E402

DEFAULTS = ["--process", "CharacterCreator.exe", "--port", "8768", "--title", "CC5 live eyes",
            "--health-url", os.environ.get("CC5_BRIDGE_URL", "http://127.0.0.1:5101") + "/health",
            "--out", os.path.join(tempfile.gettempdir(), "cc5_live_eyes")]

if __name__ == "__main__":
    user = sys.argv[1:]
    flags = {a for a in user if a.startswith("--")}
    extra = []
    for i in range(0, len(DEFAULTS), 2):
        if DEFAULTS[i] not in flags:
            extra += DEFAULTS[i:i + 2]
    sys.argv = [sys.argv[0]] + user + extra
    iclone_live_eyes.main()
