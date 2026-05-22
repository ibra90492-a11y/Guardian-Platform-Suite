import importlib
import platform
import socket
import subprocess
from typing import Dict


def _run_quick(command, timeout: int = 5) -> bool:
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=timeout)
        return True
    except Exception:
        return False


def run_diagnostics(timeout_seconds: int = 6) -> Dict[str, str]:
    out: Dict[str, str] = {
        "platform": platform.system(),
        "python": platform.python_version(),
        "wsl": "No",
        "kali": "No",
        "network": "No",
        "dns_module": "No",
    }

    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout_seconds)
        out["network"] = "Yes"
    except Exception:
        out["network"] = "No"

    try:
        importlib.import_module("dns.resolver")
        out["dns_module"] = "Yes"
    except Exception:
        out["dns_module"] = "No"

    if platform.system() == "Windows":
        if _run_quick(["wsl", "-l", "-q"], timeout=timeout_seconds):
            out["wsl"] = "Yes"
        if _run_quick(["wsl", "-d", "kali-linux", "--", "uname", "-a"], timeout=timeout_seconds):
            out["kali"] = "Yes"

    return out
