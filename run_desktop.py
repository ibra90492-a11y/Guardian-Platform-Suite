from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def main() -> int:
    relaunch_inside_venv()
    ensure_desktop_packages()

    from desktop_app import main as desktop_main

    return desktop_main()


def relaunch_inside_venv() -> None:
    if not VENV_PYTHON.exists():
        return

    current = Path(sys.executable).resolve()
    target = VENV_PYTHON.resolve()
    if current == target:
        return

    os.execv(str(target), [str(target), str(Path(__file__).resolve()), *sys.argv[1:]])


def ensure_desktop_packages() -> None:
    if desktop_packages_ready():
        return

    requirements = ROOT / "desktop_requirements.txt"
    print("Installing Guardian desktop dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements)], cwd=ROOT)

    if not desktop_packages_ready():
        raise SystemExit("Desktop dependencies were installed, but PySide6 WebEngine is still unavailable.")


def desktop_packages_ready() -> bool:
    if importlib.util.find_spec("PySide6") is None:
        return False
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
    except Exception:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())