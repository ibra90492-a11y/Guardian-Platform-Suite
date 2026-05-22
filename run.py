from __future__ import annotations

import importlib.util
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
REPORTS_DIR = ROOT / "reports" / "output"
LOGS_DIR = ROOT / "logs"

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"

FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
NODE_CANDIDATES = (
    Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin" / "node.exe",
    Path.home() / "AppData" / "Local" / "Programs" / "nodejs" / "node.exe",
    Path("C:/Program Files/nodejs/node.exe"),
)


def create_structure() -> None:
    """Create the folders the desktop app expects."""
    for path in (BACKEND_DIR, FRONTEND_DIR, REPORTS_DIR, LOGS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def ensure_backend_packages() -> None:
    """Make sure the backend app can import its runtime dependencies."""
    if _backend_runtime_ready():
        return
    requirements = ROOT / "requirements.txt"
    if not requirements.exists():
        raise FileNotFoundError(f"Missing backend requirements file: {requirements}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements)], cwd=ROOT)
    if not _backend_runtime_ready():
        raise RuntimeError("Backend dependencies are still unavailable after installation.")


def ensure_frontend_packages() -> None:
    """Make sure the Vite frontend dependencies are present."""
    if _frontend_runtime_ready():
        return

    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if npm is None:
        raise RuntimeError("Frontend dependencies are missing and npm is not available.")

    subprocess.check_call([npm, "install"], cwd=FRONTEND_DIR)
    if not _frontend_runtime_ready():
        raise RuntimeError("Frontend dependencies are still unavailable after installation.")


def check_nmap() -> bool:
    """Return True when Nmap is installed and usable."""
    try:
        from backend.scanner.nmap_scanner import nmap_available, nmap_usable
    except Exception:
        return False
    return bool(nmap_available() and nmap_usable())


def port_is_open(port: int, host: str = BACKEND_HOST) -> bool:
    """Check whether a TCP port is already listening."""
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def start_backend() -> subprocess.Popen[str] | None:
    """Start the FastAPI backend unless it is already running."""
    if port_is_open(BACKEND_PORT):
        return None
    if not _backend_runtime_ready():
        ensure_backend_packages()

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        BACKEND_HOST,
        "--port",
        str(BACKEND_PORT),
        "--reload",
    ]
    return _launch_process(command, ROOT, LOGS_DIR / "backend.log")


def start_frontend() -> subprocess.Popen[str] | None:
    """Start the Vite dev server unless it is already running."""
    if port_is_open(FRONTEND_PORT, host=FRONTEND_HOST):
        return None
    if not _frontend_runtime_ready():
        ensure_frontend_packages()

    vite_cmd = FRONTEND_DIR / "node_modules" / ".bin" / "vite.cmd"
    vite_js = FRONTEND_DIR / "node_modules" / "vite" / "bin" / "vite.js"
    node = _find_node()

    if node and vite_js.exists():
        command = [
            node,
            str(vite_js),
            "--host",
            FRONTEND_HOST,
            "--port",
            str(FRONTEND_PORT),
            "--strictPort",
        ]
    elif vite_cmd.exists():
        command = [
            str(vite_cmd),
            "--host",
            FRONTEND_HOST,
            "--port",
            str(FRONTEND_PORT),
            "--strictPort",
        ]
    else:
        npm = shutil.which("npm") or shutil.which("npm.cmd")
        if npm is None:
            raise RuntimeError("Could not locate a frontend launcher for Vite.")
        command = [
            npm,
            "run",
            "dev",
            "--",
            "--host",
            FRONTEND_HOST,
            "--port",
            str(FRONTEND_PORT),
            "--strictPort",
        ]

    return _launch_process(command, FRONTEND_DIR, LOGS_DIR / "frontend.log")


def stop_process(process: subprocess.Popen[str] | None) -> None:
    """Stop a background process launched by this module."""
    if process is None:
        return
    if process.poll() is not None:
        return

    try:
        process.terminate()
        process.wait(timeout=8)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


def _backend_runtime_ready() -> bool:
    required = (
        "fastapi",
        "uvicorn",
        "pydantic",
        "reportlab",
        "httpx",
        "requests",
        "openai",
        "tiktoken",
    )
    return all(importlib.util.find_spec(name) is not None for name in required)


def _frontend_runtime_ready() -> bool:
    vite_cmd = FRONTEND_DIR / "node_modules" / ".bin" / "vite.cmd"
    vite_js = FRONTEND_DIR / "node_modules" / "vite" / "bin" / "vite.js"
    return vite_cmd.exists() or vite_js.exists()


def _find_node() -> str | None:
    for candidate in NODE_CANDIDATES:
        if candidate.exists():
            return str(candidate)

    node = shutil.which("node") or shutil.which("node.exe")
    if node and "WindowsApps" not in node:
        return node
    return None


def _launch_process(command: list[str], cwd: Path, log_path: Path) -> subprocess.Popen[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = open(log_path, "a", encoding="utf-8")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    startupinfo = None
    if os.name == "nt" and hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        return subprocess.Popen(
            command,
            cwd=cwd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
            startupinfo=startupinfo,
            text=True,
        )
    finally:
        log_file.close()
