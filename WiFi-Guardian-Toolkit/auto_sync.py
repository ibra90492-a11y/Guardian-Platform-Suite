#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex compatibility bridge for WiFi Guardian Toolkit.

This module replaces the old external AI sync popup with a small local bridge
that stores requests and optionally notifies callbacks. The live app sends
requests directly to the Codex desktop window from main.py.
"""

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List


PROJECT_DIR = Path(__file__).parent
REQUESTS_DIR = PROJECT_DIR / "ai_requests"
HISTORY_DIR = REQUESTS_DIR / "history"
RESPONSES_DIR = REQUESTS_DIR / "responses"

for directory in (REQUESTS_DIR, HISTORY_DIR, RESPONSES_DIR):
    directory.mkdir(exist_ok=True)

PENDING_FILE = REQUESTS_DIR / "pending.json"


class CodexSyncManager:
    """Small compatibility manager for Codex request bookkeeping."""

    def __init__(self, use_gui=True):
        self.use_gui = use_gui
        self.callbacks: List[Callable[[str, Dict], None]] = []

    def send_request(self, user_message: str, target_file: str = "", change_type: str = "") -> str:
        request_id = hashlib.md5(f"{time.time()}{user_message}".encode("utf-8")).hexdigest()[:8]
        request = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "message": user_message,
            "target_file": target_file,
            "change_type": change_type,
            "status": "sent_to_codex",
        }

        requests = self._load_pending()
        requests.append(request)
        self._save_pending(requests)
        (HISTORY_DIR / f"{request_id}.json").write_text(
            json.dumps(request, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return request_id

    def receive_response(self, request_id: str, response_data: Dict) -> bool:
        response_file = RESPONSES_DIR / f"{request_id}.json"
        response_data["received_at"] = datetime.now().isoformat()
        response_file.write_text(json.dumps(response_data, indent=2, ensure_ascii=False), encoding="utf-8")

        requests = self._load_pending()
        for request in requests:
            if request.get("id") == request_id:
                request["status"] = "responded"
                request["response"] = response_data
                break
        self._save_pending(requests)

        for callback in self.callbacks:
            callback(request_id, response_data)
        return True

    def get_pending_requests(self) -> List[Dict]:
        return self._load_pending()

    def cancel_request(self, request_id: str) -> bool:
        requests = self._load_pending()
        for request in requests:
            if request.get("id") == request_id:
                request["status"] = "cancelled"
                self._save_pending(requests)
                return True
        return False

    def on_response(self, callback):
        self.callbacks.append(callback)
        return callback

    def _load_pending(self) -> List[Dict]:
        if PENDING_FILE.exists():
            return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        return []

    def _save_pending(self, data):
        PENDING_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    manager = CodexSyncManager(use_gui=False)
    print("Codex compatibility bridge is ready.")
