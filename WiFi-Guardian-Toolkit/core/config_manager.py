import json
import os
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "provider": "cloudflare",
    "refresh_interval_seconds": 20,
    "diagnostics_timeout_seconds": 6,
    "strict_security": False,
    "operation_mode": "defensive",
    "reports_dir": "reports",
    "audit_tail_size": 20,
    "auto_reset_dns_on_start": True,
}


class ConfigManager:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            self.save(DEFAULT_CONFIG)
            return dict(DEFAULT_CONFIG)

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = dict(DEFAULT_CONFIG)
            if isinstance(data, dict):
                merged.update(data)
            return merged
        except Exception:
            return dict(DEFAULT_CONFIG)

    def save(self, data: Dict[str, Any]) -> None:
        folder = os.path.dirname(os.path.abspath(self.path))
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
