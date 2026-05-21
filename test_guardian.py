from __future__ import annotations

import json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8000"


def request_json(method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    print("اختبار Guardian Platform")

    status = request_json("GET", "/status")
    print("status:", status)
    assert status["status"] == "online"

    plan = request_json("POST", "/understand", {"user_input": "افحص منافذ 127.0.0.1", "approved": False})
    print("understand:", plan)
    assert plan["type"] == "port_scan"

    execution = request_json("POST", "/execute", {"user_input": "افحص موقع http://127.0.0.1:8000", "approved": True})
    print("execute:", execution)
    assert execution["execution_results"]

    report = request_json(
        "POST",
        "/generate-report",
        {
            "scan_results": {"summary": "اختبار تلقائي لمنصة Guardian", "risk_score": 35},
            "client_name": "Demo Client",
            "consultant_name": "Guardian Operator",
        },
    )
    print("report:", report)
    assert report["status"] == "success"

    stats = request_json("GET", "/stats")
    print("stats:", stats)
    assert "total_commands" in stats

    print("تمت الاختبارات بنجاح")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())