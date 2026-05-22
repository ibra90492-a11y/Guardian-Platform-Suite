# -*- coding: utf-8 -*-
"""
live_sync.py
نظام ربط منظم بين مجلد محلي ومستودع GitHub، مع تقرير اختياري بالذكاء الاصطناعي.

الأوامر:
    python live_sync.py check
    python live_sync.py once
    python live_sync.py once --ai
    python live_sync.py upload-local
    python live_sync.py loop

مهم:
- لا تضع GitHub Token داخل هذا الملف.
- ضع التوكن داخل .env فقط.
- لا ترفع .env إلى GitHub.
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


CONFIG_FILE = "sync_config.json"
GITHUB_API = "https://api.github.com"
OPENAI_RESPONSES_API = "https://api.openai.com/v1/responses"


# ---------------------------------------------------------------------
# أدوات عامة
# ---------------------------------------------------------------------

def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_env(path: str = ".env") -> None:
    """
    قارئ بسيط لملف .env بدون مكتبات خارجية.
    لا يطبع التوكن ولا يغيّر متغيرًا موجودًا مسبقًا في النظام.
    """
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def resolve_env_value(value: Any) -> Any:
    """
    يحول ${NAME} إلى قيمة متغير البيئة NAME.
    """
    if not isinstance(value, str):
        return value

    value = os.path.expandvars(value)

    if value.startswith("${") and value.endswith("}"):
        env_name = value[2:-1]
        return os.getenv(env_name, "")

    return value


def read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"ملف JSON غير صالح: {path}\n"
            f"السبب غالبًا وجود مسار ويندوز مكتوب بشرطة واحدة مثل C:\\Users.\n"
            f"استخدم ${'{'}LOCAL_PATH{'}'} أو اكتب الشرطة هكذا: C:\\\\Users\\\\...\n"
            f"تفاصيل الخطأ: {exc}"
        ) from exc


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")


def extract_repo_name(repo_url: str) -> str:
    """
    يقبل:
    https://github.com/owner/repo
    https://github.com/owner/repo.git
    owner/repo
    """
    text = repo_url.strip().rstrip("/")
    if "github.com/" in text:
        text = text.split("github.com/", 1)[1]

    text = text.replace(".git", "").strip("/")
    parts = text.split("/")
    if len(parts) < 2:
        raise ValueError(f"رابط المستودع غير صحيح: {repo_url}")

    return f"{parts[0]}/{parts[1]}"


def safe_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def git_blob_sha1(data: bytes) -> str:
    """
    GitHub tree API يعرض SHA الخاص بالـ Git blob.
    هذه الطريقة تجعل مقارنة الملف المحلي مع GitHub صحيحة.
    """
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def short_hash(value: str) -> str:
    return value[:10] if value else "-"


def http_json(
    method: str,
    url: str,
    headers: Dict[str, str],
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> Tuple[int, Dict[str, Any]]:
    data = None

    req_headers = dict(headers)
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req_headers["Content-Type"] = "application/json; charset=utf-8"

    request = urllib.request.Request(
        url=url,
        data=data,
        headers=req_headers,
        method=method.upper(),
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(body) if body.strip() else {}
            return response.status, parsed
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body.strip() else {"message": body}
        except Exception:
            parsed = {"message": body}
        return exc.code, parsed


def ensure_ok(status: int, body: Dict[str, Any], action: str) -> None:
    if 200 <= status < 300:
        return

    message = body.get("message", "Unknown error")
    errors = body.get("errors")
    details = f"\nDetails: {errors}" if errors else ""
    raise RuntimeError(f"فشل أثناء: {action}\nHTTP {status}: {message}{details}")


# ---------------------------------------------------------------------
# الإعدادات
# ---------------------------------------------------------------------

@dataclass
class SyncConfig:
    repo_url: str
    repo_name: str
    local_path: Path
    github_token: str
    branch: str
    interval: int
    auto_push: bool
    auto_pull: bool
    max_file_size: int
    tracked_patterns: List[str]
    excluded_patterns: List[str]
    ai_enabled: bool
    openai_api_key: str
    openai_model: str
    commit_template: str


def load_config(config_path: str = CONFIG_FILE) -> SyncConfig:
    load_env()

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"ملف الإعدادات غير موجود: {path}")

    raw = read_json(path)

    sync_settings = raw.get("sync_settings", {})
    ai_settings = raw.get("ai", {})

    repo_url = str(resolve_env_value(raw.get("repo_url", ""))).strip()
    local_path_text = str(resolve_env_value(raw.get("local_path", "${LOCAL_PATH}"))).strip()
    github_token = str(resolve_env_value(raw.get("github_token", "${GITHUB_TOKEN}"))).strip()
    branch = str(resolve_env_value(raw.get("branch", ""))).strip()

    if not repo_url:
        raise ValueError("repo_url غير موجود في sync_config.json")

    if not local_path_text:
        raise ValueError("LOCAL_PATH غير موجود. ضعه داخل ملف .env")

    if not github_token or github_token == "PUT_YOUR_EXISTING_GITHUB_TOKEN_HERE":
        raise ValueError("GITHUB_TOKEN غير موجود أو ما زال قيمة افتراضية داخل .env")

    local_path = Path(local_path_text).expanduser().resolve()
    if not local_path.exists():
        raise FileNotFoundError(f"المسار المحلي غير موجود: {local_path}")

    openai_api_key = str(resolve_env_value(ai_settings.get("api_key", "${OPENAI_API_KEY}"))).strip()
    openai_model = str(resolve_env_value(ai_settings.get("model", "${OPENAI_MODEL}"))).strip() or "gpt-4.1-mini"

    return SyncConfig(
        repo_url=repo_url,
        repo_name=extract_repo_name(repo_url),
        local_path=local_path,
        github_token=github_token,
        branch=branch,
        interval=int(sync_settings.get("interval", int(os.getenv("SYNC_INTERVAL", "30") or 30))),
        auto_push=bool(sync_settings.get("auto_push", False)),
        auto_pull=bool(sync_settings.get("auto_pull", False)),
        max_file_size=int(sync_settings.get("max_file_size", 1_000_000)),
        tracked_patterns=list(sync_settings.get("tracked_patterns", ["*.py", "*.json", "*.txt", "*.md"])),
        excluded_patterns=list(sync_settings.get("excluded_patterns", [".git/*", "__pycache__/*", ".env", "*.log"])),
        ai_enabled=bool(ai_settings.get("enabled", True)),
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        commit_template=str(raw.get("commit_message_template", "[Auto-Sync] {action} {files_count} files at {timestamp}")),
    )


# ---------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------

class GitHubClient:
    def __init__(self, config: SyncConfig) -> None:
        self.config = config

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Guardian-Platform-Live-Sync",
        }

    def repo_url(self, path: str = "") -> str:
        return f"{GITHUB_API}/repos/{self.config.repo_name}{path}"

    def repo_info(self) -> Dict[str, Any]:
        status, body = http_json("GET", self.repo_url(""), self.headers)
        ensure_ok(status, body, "اختبار الاتصال بالمستودع")
        return body

    def default_branch(self) -> str:
        if self.config.branch:
            return self.config.branch

        info = self.repo_info()
        return info.get("default_branch", "main")

    def tree(self, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        branch = branch or self.default_branch()
        url = self.repo_url(f"/git/trees/{urllib.parse.quote(branch)}?recursive=1")
        status, body = http_json("GET", url, self.headers)
        ensure_ok(status, body, "قراءة شجرة المستودع")
        return list(body.get("tree", []))

    def get_content(self, repo_path: str, branch: Optional[str] = None) -> Optional[Dict[str, Any]]:
        branch = branch or self.default_branch()
        encoded_path = urllib.parse.quote(repo_path.strip("/"))
        url = self.repo_url(f"/contents/{encoded_path}?ref={urllib.parse.quote(branch)}")
        status, body = http_json("GET", url, self.headers)

        if status == 404:
            return None

        ensure_ok(status, body, f"قراءة ملف من GitHub: {repo_path}")
        return body

    def upload_file(self, repo_path: str, content: bytes, commit_message: str, branch: Optional[str] = None) -> Dict[str, Any]:
        branch = branch or self.default_branch()
        existing = self.get_content(repo_path, branch=branch)

        payload: Dict[str, Any] = {
            "message": commit_message,
            "content": base64.b64encode(content).decode("ascii"),
            "branch": branch,
        }

        if existing and existing.get("sha"):
            payload["sha"] = existing["sha"]

        encoded_path = urllib.parse.quote(repo_path.strip("/"))
        url = self.repo_url(f"/contents/{encoded_path}")
        status, body = http_json("PUT", url, self.headers, payload=payload)
        ensure_ok(status, body, f"رفع/تحديث ملف: {repo_path}")
        return body


# ---------------------------------------------------------------------
# تقرير AI اختياري
# ---------------------------------------------------------------------

class AIReporter:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def summarize(self, report_text: str) -> str:
        if not self.api_key:
            return "لم يتم إنشاء تقرير AI لأن OPENAI_API_KEY غير موجود في .env."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Guardian-Platform-Live-Sync",
        }

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": "You are a safe software assistant. Summarize repository changes. Do not reveal tokens or secrets."
                },
                {
                    "role": "user",
                    "content": "لخص تقرير تغييرات المستودع التالي بالعربية، واقترح الخطوة التالية بأمان:\n\n" + report_text
                }
            ],
        }

        status, body = http_json("POST", OPENAI_RESPONSES_API, headers, payload=payload, timeout=90)
        if not (200 <= status < 300):
            return f"تعذر إنشاء تقرير AI. HTTP {status}: {body.get('message', body)}"

        if isinstance(body.get("output_text"), str):
            return body["output_text"].strip()

        chunks: List[str] = []
        for item in body.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in ("output_text", "text"):
                    text = content.get("text", "")
                    if text:
                        chunks.append(text)

        return "\n".join(chunks).strip() if chunks else json.dumps(body, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------
# نظام الربط
# ---------------------------------------------------------------------

class GitHubLiveSync:
    def __init__(self, config_path: str = CONFIG_FILE) -> None:
        self.config_path = config_path
        self.config = load_config(config_path)
        self.github = GitHubClient(self.config)

        self.watchlist_path = self.config.local_path / "sync_watchlist.json"
        self.log_path = self.config.local_path / "sync_log.txt"
        self.report_path = self.config.local_path / "sync_report.md"
        self.notifications_path = self.config.local_path / "sync_notifications.json"

        self.ensure_watchlist()
        self.log("تم تهيئة نظام الربط.")
        self.log(f"المستودع: {self.config.repo_name}")
        self.log(f"المسار المحلي: {self.config.local_path}")

    def log(self, message: str) -> None:
        line = f"[{now_text()}] {message}"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)

    def ensure_watchlist(self) -> None:
        if self.watchlist_path.exists():
            return

        data = {
            "tracked_patterns": self.config.tracked_patterns,
            "excluded_patterns": self.config.excluded_patterns,
            "interval": self.config.interval,
            "max_file_size": self.config.max_file_size,
        }
        write_json(self.watchlist_path, data)

    def load_watchlist(self) -> Dict[str, Any]:
        if not self.watchlist_path.exists():
            self.ensure_watchlist()

        data = read_json(self.watchlist_path)
        self.config.tracked_patterns = list(data.get("tracked_patterns", self.config.tracked_patterns))
        self.config.excluded_patterns = list(data.get("excluded_patterns", self.config.excluded_patterns))
        self.config.interval = int(data.get("interval", self.config.interval))
        self.config.max_file_size = int(data.get("max_file_size", self.config.max_file_size))
        return data

    def matches_any(self, repo_path: str, patterns: Iterable[str]) -> bool:
        repo_path = repo_path.replace("\\", "/")
        return any(fnmatch.fnmatch(repo_path, pattern) for pattern in patterns)

    def is_excluded(self, repo_path: str) -> bool:
        return self.matches_any(repo_path, self.config.excluded_patterns)

    def is_tracked(self, repo_path: str) -> bool:
        if self.is_excluded(repo_path):
            return False
        return self.matches_any(repo_path, self.config.tracked_patterns)

    def scan_local(self) -> Dict[str, Dict[str, Any]]:
        self.load_watchlist()
        files: Dict[str, Dict[str, Any]] = {}

        for path in self.config.local_path.rglob("*"):
            if not path.is_file():
                continue

            repo_path = safe_rel(path, self.config.local_path)
            if not self.is_tracked(repo_path):
                continue

            size = path.stat().st_size
            if size > self.config.max_file_size:
                continue

            content = path.read_bytes()
            files[repo_path] = {
                "path": str(path),
                "sha": git_blob_sha1(content),
                "size": size,
                "modified": path.stat().st_mtime,
                "source": "local",
            }

        return files

    def scan_github(self) -> Dict[str, Dict[str, Any]]:
        self.load_watchlist()
        files: Dict[str, Dict[str, Any]] = {}

        for item in self.github.tree():
            if item.get("type") != "blob":
                continue

            repo_path = str(item.get("path", ""))
            if not repo_path or not self.is_tracked(repo_path):
                continue

            size = int(item.get("size") or 0)
            if size > self.config.max_file_size:
                continue

            files[repo_path] = {
                "path": repo_path,
                "sha": str(item.get("sha", "")),
                "size": size,
                "source": "github",
            }

        return files

    def detect_changes(self, local_files: Dict[str, Dict[str, Any]], github_files: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        changes: Dict[str, List[Dict[str, Any]]] = {
            "local_only": [],
            "github_only": [],
            "modified": [],
            "same": [],
        }

        local_set = set(local_files)
        github_set = set(github_files)

        for repo_path in sorted(local_set - github_set):
            changes["local_only"].append({"file": repo_path, "info": local_files[repo_path]})

        for repo_path in sorted(github_set - local_set):
            changes["github_only"].append({"file": repo_path, "info": github_files[repo_path]})

        for repo_path in sorted(local_set & github_set):
            local_sha = local_files[repo_path]["sha"]
            github_sha = github_files[repo_path]["sha"]

            if local_sha == github_sha:
                changes["same"].append({"file": repo_path, "sha": local_sha})
            else:
                changes["modified"].append({
                    "file": repo_path,
                    "local_sha": local_sha,
                    "github_sha": github_sha,
                    "local_info": local_files[repo_path],
                    "github_info": github_files[repo_path],
                })

        return changes

    def generate_report(self, changes: Dict[str, List[Dict[str, Any]]]) -> str:
        lines: List[str] = [
            "# تقرير الربط بين GitHub والمجلد المحلي",
            "",
            f"- الوقت: `{now_iso()}`",
            f"- المستودع: `{self.config.repo_name}`",
            f"- المسار المحلي: `{self.config.local_path}`",
            "",
            "## الملخص",
            "",
            f"- ملفات محلية غير مرفوعة: **{len(changes['local_only'])}**",
            f"- ملفات في GitHub وليست محلية: **{len(changes['github_only'])}**",
            f"- ملفات مختلفة: **{len(changes['modified'])}**",
            f"- ملفات متطابقة: **{len(changes['same'])}**",
            "",
        ]

        if changes["local_only"]:
            lines += ["## ملفات محلية غير مرفوعة", ""]
            for item in changes["local_only"]:
                lines.append(f"- `{item['file']}` - {item['info']['size']} bytes")
            lines.append("")

        if changes["github_only"]:
            lines += ["## ملفات موجودة في GitHub وليست محلية", ""]
            for item in changes["github_only"]:
                lines.append(f"- `{item['file']}` - {item['info']['size']} bytes")
            lines.append("")

        if changes["modified"]:
            lines += ["## ملفات مختلفة بين المحلي و GitHub", ""]
            for item in changes["modified"]:
                lines.append(
                    f"- `{item['file']}` | "
                    f"Local: `{short_hash(item['local_sha'])}` | "
                    f"GitHub: `{short_hash(item['github_sha'])}`"
                )
            lines.append("")

        if not changes["local_only"] and not changes["github_only"] and not changes["modified"]:
            lines.append("✅ لا توجد تغييرات تحتاج مزامنة.")
            lines.append("")

        return "\n".join(lines)

    def save_notification(self, changes: Dict[str, List[Dict[str, Any]]], report_text: str) -> None:
        self.report_path.write_text(report_text, encoding="utf-8")

        item = {
            "time": now_iso(),
            "repo": self.config.repo_name,
            "local_path": str(self.config.local_path),
            "summary": {
                "local_only": len(changes["local_only"]),
                "github_only": len(changes["github_only"]),
                "modified": len(changes["modified"]),
                "same": len(changes["same"]),
            },
            "report_path": str(self.report_path),
        }

        if self.notifications_path.exists():
            try:
                data = json.loads(self.notifications_path.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    data = []
            except Exception:
                data = []
        else:
            data = []

        data.append(item)
        write_json(self.notifications_path, data)

    def run_once(self, use_ai: bool = False, upload_local: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        self.log("بدء فحص مرة واحدة...")

        local_files = self.scan_local()
        github_files = self.scan_github()
        changes = self.detect_changes(local_files, github_files)

        report_text = self.generate_report(changes)

        if use_ai and self.config.ai_enabled:
            ai_text = AIReporter(self.config.openai_api_key, self.config.openai_model).summarize(report_text)
            report_text += "\n\n## تحليل الذكاء الاصطناعي\n\n" + ai_text.strip() + "\n"

        self.save_notification(changes, report_text)
        self.log(f"تم حفظ التقرير: {self.report_path}")

        total_changes = len(changes["local_only"]) + len(changes["github_only"]) + len(changes["modified"])
        if total_changes:
            self.log(
                f"تم العثور على تغييرات: محلي فقط={len(changes['local_only'])}, "
                f"GitHub فقط={len(changes['github_only'])}, مختلف={len(changes['modified'])}"
            )
        else:
            self.log("لا توجد تغييرات.")

        if upload_local:
            self.upload_local_changes(changes)

        return changes

    def upload_local_changes(self, changes: Dict[str, List[Dict[str, Any]]]) -> None:
        targets = changes["local_only"] + changes["modified"]

        if not targets:
            self.log("لا توجد ملفات محلية جديدة أو معدلة للرفع.")
            return

        for item in targets:
            repo_path = item["file"]
            local_file = self.config.local_path / repo_path

            if not local_file.exists() or not local_file.is_file():
                self.log(f"تخطي ملف غير موجود محليًا: {repo_path}")
                continue

            if self.is_excluded(repo_path):
                self.log(f"تخطي ملف مستبعد: {repo_path}")
                continue

            content = local_file.read_bytes()
            message = self.config.commit_template.format(
                action="update",
                files_count=1,
                timestamp=now_iso(),
            )

            self.github.upload_file(repo_path, content, message)
            self.log(f"تم رفع/تحديث: {repo_path}")

    def loop(self, use_ai: bool = False, upload_local: bool = False) -> None:
        self.log("بدء المراقبة المستمرة. للإيقاف اضغط Ctrl + C")

        while True:
            try:
                self.run_once(use_ai=use_ai, upload_local=upload_local)
                time.sleep(self.config.interval)
            except KeyboardInterrupt:
                self.log("تم إيقاف المراقبة بواسطة المستخدم.")
                raise
            except Exception as exc:
                self.log(f"خطأ في حلقة المراقبة: {exc}")
                time.sleep(60)


# ---------------------------------------------------------------------
# واجهة الأوامر
# ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guardian Platform GitHub Live Sync")
    parser.add_argument("--config", default=CONFIG_FILE, help="مسار ملف sync_config.json")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="اختبار الاتصال بالمستودع والمسار المحلي")

    once = sub.add_parser("once", help="فحص مرة واحدة وحفظ تقرير")
    once.add_argument("--ai", action="store_true", help="إضافة تحليل AI للتقرير")

    upload = sub.add_parser("upload-local", help="رفع الملفات المحلية الجديدة أو المعدلة إلى GitHub")
    upload.add_argument("--ai", action="store_true", help="إضافة تحليل AI للتقرير قبل الرفع")

    loop = sub.add_parser("loop", help="تشغيل المراقبة المستمرة")
    loop.add_argument("--ai", action="store_true", help="إضافة تحليل AI في كل تقرير")
    loop.add_argument("--upload-local", action="store_true", help="رفع المحلي تلقائيًا أثناء المراقبة")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        sync = GitHubLiveSync(args.config)

        if args.command == "check":
            info = sync.github.repo_info()
            print("✅ تم الاتصال بالمستودع بنجاح.")
            print(f"Repository: {info.get('full_name')}")
            print(f"Private: {info.get('private')}")
            print(f"Default branch: {info.get('default_branch')}")
            print(f"Local path: {sync.config.local_path}")
            print(f"Report path: {sync.report_path}")
            if sync.config.openai_api_key:
                print("✅ OPENAI_API_KEY موجود.")
            else:
                print("ℹ️ OPENAI_API_KEY غير موجود، سيعمل فحص GitHub بدون AI.")
            return 0

        if args.command == "once":
            sync.run_once(use_ai=args.ai, upload_local=False)
            return 0

        if args.command == "upload-local":
            sync.run_once(use_ai=args.ai, upload_local=True)
            return 0

        if args.command == "loop":
            sync.loop(use_ai=args.ai, upload_local=args.upload_local)
            return 0

        parser.print_help()
        return 1

    except KeyboardInterrupt:
        print("\nتم الإيقاف.")
        return 130
    except Exception as exc:
        print(f"❌ خطأ: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
