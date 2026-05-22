from __future__ import annotations

import os
import shutil
import socket
import subprocess
from dataclasses import dataclass

from backend.security.policy import hostname_from_target, validate_authorized_target


@dataclass(frozen=True)
class PortFinding:
    port: str
    protocol: str
    state: str
    service: str
    version: str = ""


def nmap_available() -> bool:
    return _nmap_enabled() and shutil.which("nmap") is not None


def nmap_usable() -> bool:
    if not _nmap_enabled():
        return False

    nmap_path = shutil.which("nmap")
    if not nmap_path:
        return False
    try:
        completed = subprocess.run(
            [nmap_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def scan_top_ports(target: str) -> dict:
    policy = validate_authorized_target(target)
    if not policy.allowed:
        return {"status": "blocked", "message": policy.reason, "ports": []}

    if not nmap_usable():
        fallback = _socket_fallback_scan(hostname_from_target(target))
        fallback["message"] = "Guardian used the safe socket fallback."
        return fallback

    host = hostname_from_target(target)
    command = [shutil.which("nmap") or "nmap", "-sV", "--top-ports", "50", host]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except OSError as exc:
        fallback = _socket_fallback_scan(host)
        fallback["message"] = "Nmap could not start, so Guardian used the safe socket fallback."
        fallback["nmap_error"] = str(exc)
        return fallback
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "message": "Nmap scan timed out after 60 seconds.", "ports": []}

    ports = _parse_nmap_output(completed.stdout)
    if completed.returncode != 0 and not ports:
        fallback = _socket_fallback_scan(host)
        fallback["message"] = f"Nmap failed with code {completed.returncode}; Guardian used the safe socket fallback."
        fallback["nmap_error"] = completed.stderr
        return fallback

    return {
        "status": "success" if completed.returncode == 0 else "error",
        "scanner": "nmap",
        "target": host,
        "command": " ".join(command),
        "ports": [finding.__dict__ for finding in ports],
        "raw_output": completed.stdout,
        "error": completed.stderr,
        "return_code": completed.returncode,
    }


def _parse_nmap_output(output: str) -> list[PortFinding]:
    findings: list[PortFinding] = []
    for line in output.splitlines():
        if "/tcp" not in line and "/udp" not in line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        port_proto = parts[0]
        if "/" not in port_proto:
            continue
        port, protocol = port_proto.split("/", 1)
        state = parts[1]
        service = parts[2]
        version = " ".join(parts[3:]) if len(parts) > 3 else ""
        findings.append(PortFinding(port=port, protocol=protocol, state=state, service=service, version=version))
    return findings


def _nmap_enabled() -> bool:
    """Keep Nmap opt-in so a broken Windows install cannot show system DLL popups."""
    return os.environ.get("GUARDIAN_ENABLE_NMAP", "").strip().lower() in {"1", "true", "yes", "on"}


def _socket_fallback_scan(host: str) -> dict:
    common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389, 5432, 6379, 8000, 8080, 8443]
    findings: list[PortFinding] = []
    for port in common_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.35)
            state = "open" if sock.connect_ex((host, port)) == 0 else "closed"
        if state == "open":
            findings.append(
                PortFinding(
                    port=str(port),
                    protocol="tcp",
                    state="open",
                    service=_guess_service(port),
                    version="socket fallback",
                )
            )

    return {
        "status": "success",
        "scanner": "socket-fallback",
        "target": host,
        "ports": [finding.__dict__ for finding in findings],
        "raw_output": "",
        "error": "",
        "return_code": 0,
    }


def _guess_service(port: int) -> str:
    services = {
        21: "ftp",
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "dns",
        80: "http",
        110: "pop3",
        135: "msrpc",
        139: "netbios",
        143: "imap",
        443: "https",
        445: "smb",
        3306: "mysql",
        3389: "rdp",
        5432: "postgresql",
        6379: "redis",
        8000: "http-alt",
        8080: "http-proxy",
        8443: "https-alt",
    }
    return services.get(port, "unknown")
