from __future__ import annotations

from datetime import datetime

from backend.security.policy import contains_blocked_term, extract_target


class GuardianAI:
    """Arabic request planner with conservative security controls."""

    def __init__(self) -> None:
        self.command_history: list[dict] = []

    def understand_request(self, user_input: str) -> dict:
        safety = contains_blocked_term(user_input)
        if not safety.allowed:
            return {
                "type": "blocked",
                "risk_level": "blocked",
                "plan": "تم منع الطلب لأنه يحتوي على أمر خطير.",
                "explanation": safety.reason,
                "requires_approval": False,
                "commands": [],
            }

        lowered = user_input.lower()
        target = extract_target(user_input) or "127.0.0.1"

        if "منافذ" in lowered or "nmap" in lowered or "port" in lowered:
            return {
                "type": "port_scan",
                "target": target,
                "risk_level": "medium",
                "plan": f"فحص أعلى 50 منفذًا على الهدف {target}",
                "explanation": "الفحص محدود ومناسب للعرض على مختبر أو شبكة مصرح بها.",
                "requires_approval": True,
                "commands": [f"nmap -sV --top-ports 50 {target}"],
            }

        if "موقع" in lowered or "headers" in lowered or "http" in lowered or "ويب" in lowered:
            return {
                "type": "web_scan",
                "target": target,
                "risk_level": "low",
                "plan": f"فحص رؤوس الأمان للهدف {target}",
                "explanation": "يفحص Security Headers بدون محاولات استغلال.",
                "requires_approval": True,
                "commands": [f"security-headers {target}"],
            }

        if "تقرير" in lowered or "pdf" in lowered:
            return {
                "type": "report",
                "target": target,
                "risk_level": "low",
                "plan": "إنشاء تقرير PDF تنفيذي وفني من آخر النتائج.",
                "explanation": "سيتم إنشاء تقرير تجريبي قابل للتنزيل.",
                "requires_approval": False,
                "commands": [],
            }

        return {
            "type": "guidance",
            "target": target,
            "risk_level": "low",
            "plan": "يمكنني فهم أوامر مثل: افحص منافذ 127.0.0.1 أو افحص موقع http://localhost:8000",
            "explanation": "النسخة الحالية مصممة للعرض الآمن داخل بيئة مصرح بها.",
            "requires_approval": False,
            "commands": [],
        }

    def record_execution(self, command: str, status: str) -> None:
        self.command_history.append(
            {"command": command, "status": status, "timestamp": datetime.now().isoformat(timespec="seconds")}
        )

    def explain_result(self, result: dict) -> str:
        if result.get("status") == "blocked":
            return f"تم منع التنفيذ: {result.get('message')}"
        if result.get("status") != "success":
            return f"لم يكتمل التنفيذ: {result.get('message') or result.get('error') or 'سبب غير معروف'}"
        if "ports" in result:
            open_ports = [port for port in result["ports"] if port.get("state") == "open"]
            return f"تم العثور على {len(open_ports)} منفذ مفتوح."
        if "findings" in result:
            missing = [item for item in result["findings"] if not item.get("present")]
            return f"تم فحص رؤوس الأمان، وعدد العناصر الناقصة {len(missing)}."
        return "تم التنفيذ بنجاح."
