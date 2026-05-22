import json
import os
from datetime import datetime
from typing import Dict, List


class AuditTrail:
    def __init__(self, file_path: str, max_items: int = 500):
        self.file_path = file_path
        self.max_items = max_items

    def add_event(self, event: str, level: str = "INFO", details: str = "") -> Dict[str, str]:
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event,
            "level": level,
            "details": details,
        }
        folder = os.path.dirname(os.path.abspath(self.file_path))
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def read_recent(self, limit: int = 20) -> List[Dict[str, str]]:
        if not os.path.exists(self.file_path):
            return []
        entries: List[Dict[str, str]] = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        if isinstance(item, dict):
                            entries.append(item)
                    except Exception:
                        continue
        except Exception:
            return []
        if len(entries) > self.max_items:
            entries = entries[-self.max_items:]
        return entries[-max(1, limit):]
