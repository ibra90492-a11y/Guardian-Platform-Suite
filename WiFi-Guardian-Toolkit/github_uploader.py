# -*- coding: utf-8 -*-
"""Upload a selected local folder to GitHub and produce a PDF summary report."""

from __future__ import annotations

import base64
import configparser
import fnmatch
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


GITHUB_API = "https://api.github.com"
DEFAULT_REPO_URL = "https://github.com/ibra90492-a11y/Guardian-Platform-Suite.git"
MAX_GITHUB_FILE_SIZE = 95 * 1024 * 1024

ProgressCallback = Callable[[int, str], None]

HARD_EXCLUDED_PATTERNS = [
    ".git/",
    ".git/**",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "*.key",
    "*.pem",
    "*.p12",
    "*.crt",
    "*.cert",
    "secrets.json",
    "token.enc",
    "*Token*.txt",
    "*token*.txt",
    "*Personal Access Token*.txt",
    "github_pat*.txt",
    "__pycache__/",
    "__pycache__/**",
    "**/__pycache__/",
    "**/__pycache__/**",
    ".venv/",
    ".venv/**",
    "**/.venv/",
    "**/.venv/**",
    "venv/",
    "venv/**",
    "env/",
    "env/**",
    "node_modules/",
    "node_modules/**",
    "**/node_modules/",
    "**/node_modules/**",
    "dist/",
    "dist/**",
    "**/dist/",
    "**/dist/**",
    "build/",
    "build/**",
    "**/.pytest_cache/",
    "**/.pytest_cache/**",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.log",
    "logs/",
    "logs/**",
    "reports/github_upload/",
    "reports/github_upload/**",
    "**/reports/github_upload/",
    "**/reports/github_upload/**",
    "sync_log.txt",
    "sync_report.md",
    "sync_notifications.json",
    "sync_watchlist.json",
    ".sync_state.json",
]


@dataclass
class LocalFile:
    repo_path: str
    full_path: Path
    size: int
    git_sha: str


@dataclass
class UploadSummary:
    project_name: str
    project_path: Path
    repo_name: str
    branch: str
    project_file_count: int
    repo_file_count: int
    new_files_count: int
    updated_files_count: int
    unchanged_files_count: int
    skipped_files: List[Tuple[str, str]]
    files: List[LocalFile]
    commit_url: str
    report_path: Path


def load_env_values(env_path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def load_github_token(env_path: Path) -> str:
    return load_env_values(env_path).get("GITHUB_TOKEN", "").strip()


def extract_repo_name(repo_url: str) -> str:
    text = repo_url.strip().rstrip("/")
    if "github.com/" in text:
        text = text.split("github.com/", 1)[1]

    text = text.replace(".git", "").strip("/")
    parts = text.split("/")
    if len(parts) < 2:
        raise ValueError(f"GitHub repository URL is invalid: {repo_url}")

    return f"{parts[0]}/{parts[1]}"


def repo_url_from_git_config(folder: Path) -> str:
    for candidate in (folder / ".git" / "config", folder.parent / ".git" / "config"):
        if not candidate.exists():
            continue

        parser = configparser.ConfigParser()
        parser.read(candidate, encoding="utf-8")
        section = 'remote "origin"'
        if parser.has_section(section) and parser.has_option(section, "url"):
            return parser.get(section, "url")

    return ""


def resolve_repo_url(folder: Path, env_path: Path) -> str:
    env_values = load_env_values(env_path)
    for key in ("GITHUB_REPO_URL", "GITHUB_REPOSITORY_URL", "REPO_URL"):
        value = env_values.get(key, "").strip()
        if value:
            return value

    from_git = repo_url_from_git_config(folder)
    return from_git or DEFAULT_REPO_URL


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def safe_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_gitignore_patterns(folder: Path) -> List[str]:
    gitignore = folder / ".gitignore"
    if not gitignore.exists():
        return []

    patterns: List[str] = []
    for raw_line in gitignore.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _pattern_matches(repo_path: str, pattern: str) -> bool:
    pattern = pattern.replace("\\", "/").strip()
    if not pattern:
        return False

    pattern = pattern.lstrip("/")
    if pattern.endswith("/"):
        directory = pattern.rstrip("/")
        return repo_path == directory or repo_path.startswith(directory + "/") or fnmatch.fnmatch(repo_path, f"**/{directory}/*")

    if "/" not in pattern:
        return fnmatch.fnmatch(Path(repo_path).name, pattern) or fnmatch.fnmatch(repo_path, f"**/{pattern}")

    return fnmatch.fnmatch(repo_path, pattern) or fnmatch.fnmatch(repo_path, f"**/{pattern}")


def is_hard_excluded(repo_path: str) -> bool:
    repo_path = repo_path.replace("\\", "/")
    return any(_pattern_matches(repo_path, pattern) for pattern in HARD_EXCLUDED_PATTERNS)


def is_gitignore_excluded(repo_path: str, patterns: Iterable[str]) -> bool:
    excluded = False
    for pattern in patterns:
        negated = pattern.startswith("!")
        clean_pattern = pattern[1:] if negated else pattern
        if _pattern_matches(repo_path, clean_pattern):
            excluded = not negated
    return excluded


def scan_local_files(folder: Path) -> Tuple[List[LocalFile], List[Tuple[str, str]]]:
    patterns = read_gitignore_patterns(folder)
    files: List[LocalFile] = []
    skipped: List[Tuple[str, str]] = []

    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue

        repo_path = safe_rel(path, folder)
        if is_hard_excluded(repo_path) or is_gitignore_excluded(repo_path, patterns):
            continue

        size = path.stat().st_size
        if size > MAX_GITHUB_FILE_SIZE:
            skipped.append((repo_path, "File is larger than GitHub API upload limit."))
            continue

        content = path.read_bytes()
        files.append(LocalFile(repo_path=repo_path, full_path=path, size=size, git_sha=git_blob_sha1(content)))

    return files, skipped


def http_json(
    method: str,
    url: str,
    headers: Dict[str, str],
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 90,
) -> Tuple[int, Dict[str, Any]]:
    data = None
    request_headers = dict(headers)
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json; charset=utf-8"

    request = urllib.request.Request(url=url, data=data, headers=request_headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body.strip() else {"message": body}
        except json.JSONDecodeError:
            parsed = {"message": body}
        return exc.code, parsed


def ensure_ok(status: int, body: Dict[str, Any], action: str) -> None:
    if 200 <= status < 300:
        return

    message = body.get("message", "Unknown error")
    details = body.get("errors")
    raise RuntimeError(f"{action} failed. HTTP {status}: {message}" + (f" Details: {details}" if details else ""))


class GitHubApi:
    def __init__(self, token: str, repo_name: str) -> None:
        self.repo_name = repo_name
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Guardian-GitHub-Uploader",
        }

    def url(self, suffix: str = "") -> str:
        return f"{GITHUB_API}/repos/{self.repo_name}{suffix}"

    def request(self, method: str, suffix: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        status, body = http_json(method, self.url(suffix), self.headers, payload=payload)
        ensure_ok(status, body, f"GitHub {method} {suffix}")
        return body

    def default_branch(self) -> str:
        return str(self.request("GET", "").get("default_branch") or "main")

    def ref(self, branch: str) -> Dict[str, Any]:
        return self.request("GET", f"/git/ref/heads/{urllib.parse.quote(branch, safe='')}")

    def commit(self, sha: str) -> Dict[str, Any]:
        return self.request("GET", f"/git/commits/{sha}")

    def recursive_tree(self, tree_or_branch: str) -> List[Dict[str, Any]]:
        body = self.request("GET", f"/git/trees/{urllib.parse.quote(tree_or_branch, safe='')}?recursive=1")
        return list(body.get("tree", []))

    def create_blob(self, content: bytes) -> str:
        body = self.request(
            "POST",
            "/git/blobs",
            {
                "content": base64.b64encode(content).decode("ascii"),
                "encoding": "base64",
            },
        )
        return str(body["sha"])

    def create_tree(self, base_tree: str, entries: List[Dict[str, Any]]) -> str:
        body = self.request("POST", "/git/trees", {"base_tree": base_tree, "tree": entries})
        return str(body["sha"])

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        body = self.request("POST", "/git/commits", {"message": message, "tree": tree_sha, "parents": [parent_sha]})
        return str(body["sha"])

    def update_ref(self, branch: str, commit_sha: str) -> None:
        self.request("PATCH", f"/git/refs/heads/{urllib.parse.quote(branch, safe='')}", {"sha": commit_sha, "force": False})


def upload_folder_to_github(folder: Path, token: str, env_path: Path, progress: ProgressCallback) -> UploadSummary:
    folder = folder.resolve()
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Selected folder does not exist: {folder}")

    progress(3, "جاري فحص ملفات المجلد المحلي")
    local_files, skipped = scan_local_files(folder)

    repo_url = resolve_repo_url(folder, env_path)
    repo_name = extract_repo_name(repo_url)
    github = GitHubApi(token, repo_name)

    progress(10, "جاري قراءة معلومات مستودع GitHub")
    branch = github.default_branch()
    current_ref = github.ref(branch)
    parent_sha = str(current_ref["object"]["sha"])
    parent_commit = github.commit(parent_sha)
    base_tree_sha = str(parent_commit["tree"]["sha"])

    progress(16, "جاري مقارنة الملفات المحلية مع ملفات المستودع")
    remote_items = github.recursive_tree(base_tree_sha)
    remote_files = {
        str(item.get("path")): str(item.get("sha"))
        for item in remote_items
        if item.get("type") == "blob" and item.get("path")
    }

    changed_files = [item for item in local_files if remote_files.get(item.repo_path) != item.git_sha]
    new_files_count = sum(1 for item in changed_files if item.repo_path not in remote_files)
    updated_files_count = len(changed_files) - new_files_count
    unchanged_files_count = len(local_files) - len(changed_files)

    if not changed_files:
        progress(92, "لا توجد ملفات جديدة أو معدلة للرفع")
        report_path = generate_pdf_report(
            folder=folder,
            repo_name=repo_name,
            branch=branch,
            files=local_files,
            repo_file_count=len(remote_files),
            new_files_count=0,
            updated_files_count=0,
            unchanged_files_count=unchanged_files_count,
            skipped_files=skipped,
            commit_url="No new commit was required.",
        )
        progress(100, "اكتملت العملية وتم إنشاء تقرير PDF")
        return UploadSummary(
            project_name=folder.name,
            project_path=folder,
            repo_name=repo_name,
            branch=branch,
            project_file_count=len(local_files),
            repo_file_count=len(remote_files),
            new_files_count=0,
            updated_files_count=0,
            unchanged_files_count=unchanged_files_count,
            skipped_files=skipped,
            files=local_files,
            commit_url="No new commit was required.",
            report_path=report_path,
        )

    tree_entries: List[Dict[str, Any]] = []
    total = len(changed_files)
    for index, item in enumerate(changed_files, start=1):
        percent = 20 + int((index / total) * 60)
        progress(percent, f"جاري رفع وتحديث ملفات مستودع GitHub ({index}/{total})")
        blob_sha = github.create_blob(item.full_path.read_bytes())
        tree_entries.append({"path": item.repo_path, "mode": "100644", "type": "blob", "sha": blob_sha})

    progress(84, "جاري إنشاء commit في مستودع GitHub")
    tree_sha = github.create_tree(base_tree_sha, tree_entries)
    message = f"Upload and update {len(changed_files)} files from {folder.name}"
    commit_sha = github.create_commit(message, tree_sha, parent_sha)

    progress(90, "جاري تحديث الفرع الرئيسي في GitHub")
    github.update_ref(branch, commit_sha)

    final_files = github.recursive_tree(tree_sha)
    final_repo_count = sum(1 for item in final_files if item.get("type") == "blob")
    commit_url = f"https://github.com/{repo_name}/commit/{commit_sha}"

    progress(95, "جاري إنشاء تقرير PDF للعملية")
    report_path = generate_pdf_report(
        folder=folder,
        repo_name=repo_name,
        branch=branch,
        files=local_files,
        repo_file_count=final_repo_count,
        new_files_count=new_files_count,
        updated_files_count=updated_files_count,
        unchanged_files_count=unchanged_files_count,
        skipped_files=skipped,
        commit_url=commit_url,
    )

    progress(100, "اكتملت العملية وتم إنشاء تقرير PDF")
    return UploadSummary(
        project_name=folder.name,
        project_path=folder,
        repo_name=repo_name,
        branch=branch,
        project_file_count=len(local_files),
        repo_file_count=final_repo_count,
        new_files_count=new_files_count,
        updated_files_count=updated_files_count,
        unchanged_files_count=unchanged_files_count,
        skipped_files=skipped,
        files=local_files,
        commit_url=commit_url,
        report_path=report_path,
    )


def _report_font() -> Tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    regular_candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/tahoma.ttf"),
    ]
    bold_candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/tahomabd.ttf"),
    ]

    regular = next((path for path in regular_candidates if path.exists()), None)
    bold = next((path for path in bold_candidates if path.exists()), None)
    if regular:
        pdfmetrics.registerFont(TTFont("GuardianRegular", str(regular)))
    if bold:
        pdfmetrics.registerFont(TTFont("GuardianBold", str(bold)))

    return ("GuardianRegular" if regular else "Helvetica", "GuardianBold" if bold else "Helvetica-Bold")


def _table_rows(files: List[LocalFile]) -> List[List[str]]:
    rows = [["#", "File name / اسم الملف", "Size / الحجم"]]
    for index, item in enumerate(files, start=1):
        rows.append([str(index), item.repo_path, f"{item.size:,} bytes"])
    return rows


def generate_pdf_report(
    folder: Path,
    repo_name: str,
    branch: str,
    files: List[LocalFile],
    repo_file_count: int,
    new_files_count: int,
    updated_files_count: int,
    unchanged_files_count: int,
    skipped_files: List[Tuple[str, str]],
    commit_url: str,
) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    regular_font, bold_font = _report_font()
    reports_dir = folder / "reports" / "github_upload"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"github_upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(report_path),
        pagesize=A4,
        rightMargin=1.1 * cm,
        leftMargin=1.1 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "GuardianTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#14532d"),
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "GuardianSubtitle",
        parent=styles["Normal"],
        fontName=regular_font,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        alignment=1,
    )
    normal_style = ParagraphStyle(
        "GuardianNormal",
        parent=styles["Normal"],
        fontName=regular_font,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )
    section_style = ParagraphStyle(
        "GuardianSection",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#166534"),
    )

    story: List[Any] = [
        Paragraph("GitHub Upload and Update Report", title_style),
        Paragraph("تقرير الرفع والتحديث الى GitHub", subtitle_style),
        Spacer(1, 0.35 * cm),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style),
        Spacer(1, 0.45 * cm),
    ]

    project_summary = [
        ["Project folder / مجلد المشروع", folder.name],
        ["Project path / مسار المشروع", str(folder)],
        ["Local files in folder / عدد الملفات في المجلد", f"{len(files):,}"],
        ["Repository / المستودع", repo_name],
        ["Branch / الفرع", branch],
        ["Commit / رابط التحديث", commit_url],
    ]
    story.append(Paragraph("Project Summary / ملخص المشروع", section_style))
    story.append(_styled_table(project_summary, regular_font, bold_font, [5.0 * cm, 12.0 * cm], header=False))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Folder Files / ملفات المجلد", section_style))
    file_rows = _table_rows(files)
    story.append(_styled_table(file_rows, regular_font, bold_font, [1.1 * cm, 12.0 * cm, 3.5 * cm], header=True))
    story.append(Spacer(1, 0.45 * cm))

    upload_summary = [
        ["Metric / البيان", "Count / العدد"],
        ["Files currently in repository / عدد الملفات الموجودة في المستودع", f"{repo_file_count:,}"],
        ["New uploaded files / عدد الملفات الجديدة التي تم رفعها", f"{new_files_count:,}"],
        ["Updated existing files / عدد الملفات القديمة التي تم تحديثها", f"{updated_files_count:,}"],
        ["Unchanged local files / ملفات محلية لم تتغير", f"{unchanged_files_count:,}"],
        ["Skipped files / ملفات تم تخطيها", f"{len(skipped_files):,}"],
    ]
    story.append(Paragraph("Upload Summary / ملخص الرفع", section_style))
    story.append(_styled_table(upload_summary, regular_font, bold_font, [12.8 * cm, 3.8 * cm], header=True))

    if skipped_files:
        story.append(Spacer(1, 0.35 * cm))
        skipped_rows = [["File / الملف", "Reason / السبب"], *[[name, reason] for name, reason in skipped_files]]
        story.append(Paragraph("Skipped Files / الملفات المتخطاة", section_style))
        story.append(_styled_table(skipped_rows, regular_font, bold_font, [11.0 * cm, 5.6 * cm], header=True))

    doc.build(story)
    return report_path


def _styled_table(
    rows: List[List[str]],
    regular_font: str,
    bold_font: str,
    col_widths: List[float],
    header: bool,
) -> Any:
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Table, TableStyle

    cell_style = ParagraphStyle("Cell", fontName=regular_font, fontSize=8, leading=10)
    header_style = ParagraphStyle("HeaderCell", fontName=bold_font, fontSize=8.5, leading=11, textColor=colors.white)
    data = []
    for row_index, row in enumerate(rows):
        style = header_style if header and row_index == 0 else cell_style
        data.append([Paragraph(str(cell), style) for cell in row])

    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), regular_font),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#166534")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ]
        )
    else:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#dcfce7")),
                ("FONTNAME", (0, 0), (0, -1), bold_font),
            ]
        )
    table.setStyle(TableStyle(commands))
    return table


def open_report_pdf(report_path: Path) -> None:
    if os.name == "nt":
        os.startfile(str(report_path))  # type: ignore[attr-defined]
    else:
        import subprocess

        subprocess.Popen(["xdg-open", str(report_path)])
