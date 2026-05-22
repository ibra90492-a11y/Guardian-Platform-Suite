from __future__ import annotations

import shutil
import webbrowser
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime

from pydantic import BaseModel

from backend.ai_operator.guardian_ai import GuardianAI
from backend.reporter.pdf_generator import PDFReporter
from backend.scanner.nmap_scanner import nmap_available, nmap_usable, scan_top_ports
from backend.scanner.web_scanner import scan_security_headers


app = FastAPI(
    title="Guardian Cyber Assessment Platform",
    description="Defensive MVP for authorized cyber assessment, Arabic AI planning, safe scans, and reports.",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

guardian = GuardianAI()
reporter = PDFReporter()
LAST_RESULTS: dict = {}
OPERATION_LOG: list[dict] = []


class CommandRequest(BaseModel):
    user_input: str
    approved: bool = False


class TargetRequest(BaseModel):
    target: str


class ReportRequest(BaseModel):
    scan_results: dict = {}
    client_name: str = "Client"
    consultant_name: str = "Guardian Operator"


@app.get("/")
def root() -> dict:
    return {
        "name": "Guardian Cyber Assessment Platform",
        "status": "ready",
        "version": "0.2.0",
        "nmap_available": nmap_available(),
        "nmap_usable": nmap_usable(),
        "features": ["ai_operator", "port_scan", "web_headers", "pdf_reports", "safe_fallback"],
        "security": {
            "password_storage": "No passwords are stored.",
            "dangerous_commands": "Blocked by policy.",
            "execution": "Requires prior approval.",
            "scope": "Authorized and ethical use only with written permission.",
        },
    }


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "timestamp": datetime.now().isoformat(timespec="seconds")}


@app.get("/status")
def status() -> dict:
    return {"status": "online", "nmap_available": nmap_available(), "nmap_usable": nmap_usable()}


@app.post("/understand")
def understand(request: CommandRequest) -> dict:
    return guardian.understand_request(request.user_input)


@app.post("/execute")
async def execute(request: CommandRequest) -> dict:
    plan = guardian.understand_request(request.user_input)
    if plan["type"] == "blocked":
        return {"plan": plan, "execution_results": []}
    if plan.get("requires_approval") and not request.approved:
        return {"plan": plan, "execution_results": [], "message": "Execution requires approval."}

    if plan["type"] == "port_scan":
        result = scan_top_ports(plan["target"])
    elif plan["type"] == "web_scan":
        result = await scan_security_headers(plan["target"])
    else:
        result = {"status": "success", "message": plan["explanation"]}

    command = plan["commands"][0] if plan.get("commands") else plan["type"]
    guardian.record_execution(command, result.get("status", "unknown"))
    explanation = guardian.explain_result(result)
    _record_operation(plan=plan, command=command, result=result, explanation=explanation)
    LAST_RESULTS.clear()
    LAST_RESULTS.update(result)

    return {"plan": plan, "execution_results": [{"command": command, "result": result, "explanation": explanation}]}


@app.post("/scan/ports")
def scan_ports(request: TargetRequest) -> dict:
    result = scan_top_ports(request.target)
    _record_operation(
        plan={"type": "port_scan", "target": request.target, "plan": "Direct port scan"},
        command=f"port-scan {request.target}",
        result=result,
        explanation=guardian.explain_result(result),
    )
    LAST_RESULTS.clear()
    LAST_RESULTS.update(result)
    return result


@app.post("/scan/web")
async def scan_web(request: TargetRequest) -> dict:
    result = await scan_security_headers(request.target)
    _record_operation(
        plan={"type": "web_scan", "target": request.target, "plan": "Direct web headers scan"},
        command=f"security-headers {request.target}",
        result=result,
        explanation=guardian.explain_result(result),
    )
    LAST_RESULTS.clear()
    LAST_RESULTS.update(result)
    return result


@app.post("/generate-report")
def generate_report(request: dict | None = None) -> dict:
    request = request or {}
    if "scan_results" in request:
        payload = request.get("scan_results") or LAST_RESULTS
        client_name = request.get("client_name", "Client")
        consultant_name = request.get("consultant_name", "Guardian Operator")
    else:
        payload = request or LAST_RESULTS or {"summary": "Demo report generated before running a scan.", "risk_score": 30}
        client_name = "Client"
        consultant_name = "Guardian Operator"

    pdf_path = Path(reporter.generate(payload, client_name=client_name, consultant_name=consultant_name))
    return {"status": "success", "report_path": str(pdf_path), "download_url": f"/download/{pdf_path.name}"}


@app.get("/reports/all/pdf")
def download_all_operations_report() -> FileResponse:
    payload = _operations_report_payload()
    pdf_path = Path(reporter.generate(payload, client_name="Guardian Demo", consultant_name="Guardian Operator"))
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=pdf_path.name)


@app.post("/reports/all/pdf/download-open")
def save_and_open_all_operations_report() -> dict:
    payload = _operations_report_payload()
    pdf_path = Path(reporter.generate(payload, client_name="Guardian Demo", consultant_name="Guardian Operator"))
    downloads_path = _copy_to_downloads(pdf_path)
    opened = _open_in_default_browser(downloads_path)
    return {
        "status": "success",
        "message": "Report saved to Downloads.",
        "report_path": str(downloads_path),
        "source_path": str(pdf_path),
        "opened": opened,
        "download_url": f"/download/{pdf_path.name}",
    }


@app.post("/reports/all/pdf/create")
def create_all_operations_report() -> dict:
    payload = _operations_report_payload()
    pdf_path = Path(reporter.generate(payload, client_name="Guardian Demo", consultant_name="Guardian Operator"))
    return {
        "status": "success",
        "message": "Report created.",
        "report_path": str(pdf_path),
        "download_url": f"/download/{pdf_path.name}",
    }


@app.get("/download/{filename}")
def download(filename: str) -> FileResponse:
    path = Path(__file__).resolve().parents[1] / "reports" / "output" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(str(path), media_type="application/pdf", filename=filename)


@app.get("/history")
def history() -> dict:
    return {"history": guardian.command_history[-20:], "operations": OPERATION_LOG[-20:]}


@app.post("/history/clear")
def clear_history() -> dict:
    guardian.command_history.clear()
    OPERATION_LOG.clear()
    return {"status": "cleared"}


@app.get("/stats")
def stats() -> dict:
    total = len(OPERATION_LOG)
    successful = len([item for item in OPERATION_LOG if item.get("status") == "success"])
    return {
        "total_commands": total,
        "successful_commands": successful,
        "success_rate": round((successful / total * 100), 2) if total else 0,
        "nmap_available": nmap_available(),
        "nmap_usable": nmap_usable(),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def _record_operation(plan: dict, command: str, result: dict, explanation: str) -> None:
    OPERATION_LOG.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": plan.get("type", "scan"),
            "target": plan.get("target", result.get("target", "unknown")),
            "command": command,
            "status": result.get("status", "unknown"),
            "risk_score": result.get("risk_score"),
            "explanation": explanation,
            "result": result,
        }
    )


def _operations_report_payload() -> dict:
    operations = OPERATION_LOG[-100:]
    findings: list[dict] = []
    ports: list[dict] = []
    risk_scores: list[int] = []

    for operation in operations:
        result = operation.get("result", {})
        if isinstance(result.get("risk_score"), int):
            risk_scores.append(result["risk_score"])
        findings.extend(result.get("findings", []))
        ports.extend(result.get("ports", []))

    open_ports = [port for port in ports if port.get("state") == "open"]
    missing_headers = [finding for finding in findings if finding.get("present") is False]
    computed_score = max(risk_scores) if risk_scores else min(100, 20 + len(open_ports) * 8 + len(missing_headers) * 10)

    if not operations:
        return {
            "summary": "No scan operations have been executed yet. Run a port scan or web headers scan, then download the report again.",
            "risk_score": 0,
            "operations": [],
            "findings": [],
            "ports": [],
        }

    return {
        "summary": (
            f"Guardian collected {len(operations)} authorized scan operation(s). "
            f"The report includes {len(open_ports)} open port finding(s) and {len(missing_headers)} missing security header finding(s)."
        ),
        "risk_score": computed_score,
        "operations": operations,
        "findings": findings,
        "ports": ports,
    }


def _copy_to_downloads(pdf_path: Path) -> Path:
    downloads_dir = Path.home() / "Downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    destination = downloads_dir / pdf_path.name

    if destination.exists():
        stem = pdf_path.stem
        suffix = pdf_path.suffix
        destination = downloads_dir / f"{stem}_{datetime.now().strftime('%H%M%S')}{suffix}"

    shutil.copy2(pdf_path, destination)
    return destination


def _open_in_default_browser(pdf_path: Path) -> bool:
    try:
        return bool(webbrowser.open(pdf_path.resolve().as_uri(), new=2))
    except Exception:
        return False
