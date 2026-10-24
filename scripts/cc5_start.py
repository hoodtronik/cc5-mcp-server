"""Start Character Creator 5 for agent use and wait until the MCP bridge answers.

  python scripts/cc5_start.py            # launch (if not running) + wait for http://127.0.0.1:5101/health
  python scripts/cc5_start.py --reload   # hot-reload cc5_api.py on a running CC5 (no restart)

# CLAUDE-NOTE (2026-10-24, hoodtronik fork):
# - CC5 shows a modal "Failed to establish a connection ... internet connection" box (OK only) at start;
#   while it is up the OpenPlugin bridge never starts. This script presses OK on THAT box only (read first,
#   exact text match); any other popup is reported, never touched.
# - Launches CC5 with CC5_RELOAD_SECRET (kept in %LOCALAPPDATA%/cc5_reload_secret.txt) so GET /reload
#   works: edits to cc5-plugin/cc5_api.py (incl. EXTRA_* routes) go live in ~1 s instead of a restart.
# - Popup handling reuses mc-iclone8-mcp/scripts/iclone_eyes.py (UI Automation; set ICLONE_MCP_DIR).
"""
import json
import os
import secrets
import subprocess
import sys
import time
import urllib.request

EXE = os.environ.get("CC5_EXE", r"C:\Program Files\Reallusion\Character Creator 5\Bin64\CharacterCreator.exe")
BRIDGE = os.environ.get("CC5_BRIDGE_URL", "http://127.0.0.1:5101")
SECRET_FILE = os.path.join(os.environ.get("LOCALAPPDATA", "."), "cc5_reload_secret.txt")
EYES = os.path.join(os.environ.get("ICLONE_MCP_DIR", r"G:\_AI_Agents\mc-iclone8-mcp"), "scripts", "iclone_eyes.py")
CONNECTION_POPUP = "Failed to establish a connection"


def secret() -> str:
    if not os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "w") as f:
            f.write(secrets.token_hex(16))
    return open(SECRET_FILE).read().strip()


def healthy() -> bool:
    try:
        with urllib.request.urlopen(BRIDGE + "/health", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def running() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CharacterCreator.exe", "/NH"], capture_output=True, text=True).stdout
    return "CharacterCreator.exe" in out


def handle_popups() -> None:
    if not os.path.exists(EYES):
        return
    sys.path.insert(0, os.path.dirname(EYES))
    import iclone_eyes as eyes  # noqa: E402
    for w in eyes.list_windows("CharacterCreator.exe"):
        if not w.get("owned"):
            continue
        info = subprocess.run([sys.executable, EYES, "read", str(w["hwnd"])], capture_output=True, text=True).stdout
        if CONNECTION_POPUP in info and '"OK"' in info:
            subprocess.run([sys.executable, EYES, "press", str(w["hwnd"]), "OK"], capture_output=True)
            print("dismissed CC5 connection popup")
        else:
            print("OTHER CC5 POPUP (left alone):", info[:300].replace("\n", " "))


def reload() -> None:
    req = urllib.request.Request(BRIDGE + "/reload", headers={"X-Reload-Token": secret()})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(json.loads(r.read()))


def main() -> int:
    if "--reload" in sys.argv:
        reload()
        return 0
    if healthy():
        print("bridge already up")
        return 0
    if not running():
        env = dict(os.environ, CC5_RELOAD_SECRET=secret())
        subprocess.Popen([EXE], env=env, close_fds=True)
        print("launched CC5")
    t0 = time.time()
    while time.time() - t0 < 300:
        if healthy():
            print(f"bridge up after {time.time() - t0:.0f}s")
            return 0
        handle_popups()
        time.sleep(4)
    print("bridge did not come up in 300 s")
    return 1


if __name__ == "__main__":
    sys.exit(main())
