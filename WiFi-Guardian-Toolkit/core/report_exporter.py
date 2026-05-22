import json
import os
from datetime import datetime
from typing import Dict, Tuple


def export_security_report(reports_dir: str, payload: Dict) -> Tuple[str, str]:
    os.makedirs(reports_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"security_report_{stamp}"
    json_path = os.path.join(reports_dir, base_name + ".json")
    txt_path = os.path.join(reports_dir, base_name + ".txt")

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(payload, jf, ensure_ascii=False, indent=2)

    lines = [
        "WiFi Guardian Toolkit - Security Report",
        "=" * 44,
        f"GeneratedAt: {payload.get('generated_at', 'N/A')}",
        f"Mode: {payload.get('mode', 'N/A')}",
        f"ProtectionActive: {payload.get('protection_active', False)}",
        f"SecurityScore: {payload.get('security_score', 0)} ({payload.get('security_level', 'RISK')})",
        "",
        "Snapshot:",
    ]

    snapshot = payload.get("snapshot", {})
    for key in ["doh", "dot", "warp", "conn_111", "ip_address", "state"]:
        lines.append(f"- {key}: {snapshot.get(key, 'N/A')}")

    lines.append("")
    lines.append("Diagnostics:")
    diagnostics = payload.get("diagnostics", {})
    for k, v in diagnostics.items():
        lines.append(f"- {k}: {v}")

    lines.append("")
    lines.append("Recent Audit Events:")
    for item in payload.get("audit_tail", []):
        lines.append(f"- [{item.get('timestamp', 'N/A')}] [{item.get('level', 'INFO')}] {item.get('event', '')} :: {item.get('details', '')}")

    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write("\n".join(lines) + "\n")

    return json_path, txt_path
