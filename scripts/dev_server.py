"""Reload the development HTTP process after Python source edits."""

import os
from pathlib import Path
import signal
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
stopping = False


def stop(signum, frame):
    global stopping
    stopping = True


def snapshot():
    return {
        str(path): path.stat().st_mtime_ns
        for path in ROOT.rglob("*.py")
        if not {".git", ".venv", "__pycache__"}.intersection(path.relative_to(ROOT).parts)
    }


def terminate(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    previous = snapshot()
    child = subprocess.Popen([sys.executable, "-u", "app.py"], cwd=ROOT)
    try:
        while not stopping:
            time.sleep(0.5)
            if Path("/workspace/.syncing").exists():
                continue
            current = snapshot()
            if current != previous:
                terminate(child)
                previous = current
                child = subprocess.Popen([sys.executable, "-u", "app.py"], cwd=ROOT)
    finally:
        terminate(child)


if __name__ == "__main__":
    main()
