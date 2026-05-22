import os
from datetime import datetime
from typing import Optional


class RuntimeLogger:
    def __init__(self, log_path: str):
        self.log_path = log_path

    def _write(self, level: str, source: str, details: str) -> None:
        try:
            folder = os.path.dirname(os.path.abspath(self.log_path))
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"[{stamp}] [{level}] {source}\n{details}\n{'-' * 80}\n")
        except Exception:
            pass

    def info(self, source: str, details: str) -> None:
        self._write("INFO", source, details)

    def error(self, source: str, details: str) -> None:
        self._write("ERROR", source, details)

    def exception(self, source: str, exc_text: str, extra: Optional[str] = None) -> None:
        text = exc_text if extra is None else f"{extra}\n{exc_text}"
        self._write("EXCEPTION", source, text)
