from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlparse


BLOCKED_TERMS = (
    "rm -rf",
    "del ",
    "format",
    "drop database",
    "--password",
    "shadow",
    "passwd",
    "chmod 777",
    "powershell -enc",
    "mimikatz",
    "hydra",
    "sqlmap",
)


PRIVATE_HOSTNAMES = {"localhost"}


@dataclass(frozen=True)
class PolicyResult:
    allowed: bool
    reason: str


def contains_blocked_term(text: str) -> PolicyResult:
    lowered = text.lower()
    for term in BLOCKED_TERMS:
        if term in lowered:
            return PolicyResult(False, f"Blocked dangerous term: {term}")
    return PolicyResult(True, "Allowed")


def extract_target(text: str) -> str | None:
    url_match = re.search(r"https?://[^\s]+", text, flags=re.IGNORECASE)
    if url_match:
        return url_match.group(0).rstrip(".,;")

    ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
    if ip_match:
        return ip_match.group(0)

    host_match = re.search(r"\b(?:localhost|[a-z0-9.-]+\.[a-z]{2,})\b", text, flags=re.IGNORECASE)
    if host_match:
        return host_match.group(0).rstrip(".,;")

    return None


def hostname_from_target(target: str) -> str:
    parsed = urlparse(target if "://" in target else f"http://{target}")
    return parsed.hostname or target


def normalize_url(target: str) -> str:
    if target.startswith(("http://", "https://")):
        return target
    return f"http://{target}"


def validate_authorized_target(target: str, allow_public: bool = False) -> PolicyResult:
    host = hostname_from_target(target).lower()
    if host in PRIVATE_HOSTNAMES:
        return PolicyResult(True, "Local target allowed")

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        if allow_public:
            return PolicyResult(True, "Public hostname allowed by explicit setting")
        return PolicyResult(
            False,
            "Public hostnames are disabled in MVP mode. Use localhost or a private lab IP.",
        )

    if ip.is_private or ip.is_loopback or ip.is_link_local:
        return PolicyResult(True, "Private/lab IP allowed")

    if allow_public:
        return PolicyResult(True, "Public IP allowed by explicit setting")

    return PolicyResult(
        False,
        "Public IP scanning is disabled in MVP mode. Use an authorized lab target.",
    )
