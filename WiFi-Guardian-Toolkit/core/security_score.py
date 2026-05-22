from typing import Dict


def calculate_security_score(snapshot: Dict[str, str], diagnostics: Dict[str, str]) -> int:
    """Return a simple deterministic security score from 0 to 100."""
    score = 0

    if snapshot.get("doh") == "Yes":
        score += 40
    if snapshot.get("dot") == "Yes":
        score += 20
    if snapshot.get("warp") == "Yes":
        score += 10
    if snapshot.get("conn_111") == "Yes":
        score += 10

    if diagnostics.get("wsl") == "Yes":
        score += 5
    if diagnostics.get("kali") == "Yes":
        score += 5
    if diagnostics.get("network") == "Yes":
        score += 5
    if diagnostics.get("dns_module") == "Yes":
        score += 5

    return max(0, min(100, score))


def score_level(score: int) -> str:
    if score >= 85:
        return "HARDENED"
    if score >= 60:
        return "GOOD"
    if score >= 35:
        return "BASIC"
    return "RISK"
