from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFReporter:
    def __init__(self, output_dir: str | Path | None = None) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        self.output_dir = Path(output_dir) if output_dir else base_dir / "reports" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, scan_data: dict, client_name: str = "Client", consultant_name: str = "Guardian Operator") -> str:
        filename = f"guardian_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path = self.output_dir / filename

        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="SmallCell",
                parent=styles["Normal"],
                fontSize=8,
                leading=10,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Muted",
                parent=styles["Normal"],
                textColor=colors.HexColor("#5d6b78"),
                fontSize=9,
                leading=12,
            )
        )
        risk_score = int(scan_data.get("risk_score", 45) or 0)
        story = [
            Paragraph("Guardian Cyber Assessment Platform", styles["Title"]),
            Paragraph("Executive Security Assessment Report", styles["Heading2"]),
            Paragraph(f"Client: {client_name}", styles["Normal"]),
            Paragraph(f"Consultant: {consultant_name}", styles["Normal"]),
            Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles["Normal"]),
            Spacer(1, 18),
            Paragraph("Executive Summary", styles["Heading2"]),
            Paragraph(scan_data.get("summary", "MVP security assessment generated from authorized lab scans."), styles["Normal"]),
            Spacer(1, 14),
            _risk_score_table(risk_score),
            Spacer(1, 14),
        ]

        operations = scan_data.get("operations", [])
        if operations:
            story.extend(
                [
                    Paragraph("Scan Operations", styles["Heading2"]),
                    _operations_table(operations, styles),
                    Spacer(1, 16),
                ]
            )

        rows = [["Finding", "Severity", "Recommendation"]]
        for finding in scan_data.get("findings", []):
            rows.append(
                [
                    _cell(str(finding.get("name") or finding.get("header") or "Finding"), styles),
                    _cell(str(finding.get("severity", "info")), styles),
                    _cell(str(finding.get("recommendation", "Review and remediate as needed.")), styles),
                ]
            )

        for port in scan_data.get("ports", []):
            rows.append(
                [
                    _cell(f"Open port {port.get('port')}/{port.get('protocol')}", styles),
                    _cell("medium" if port.get("state") == "open" else "info", styles),
                    _cell(f"Review exposed service: {port.get('service', 'unknown')}", styles),
                ]
            )

        if len(rows) == 1:
            rows.append(["No findings supplied", "info", "Run a lab scan and regenerate the report."])

        story.append(Paragraph("Findings And Recommendations", styles["Heading2"]))
        table = Table(rows, repeatRows=1, colWidths=[155, 70, 245])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324d")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7dde5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fb")]),
                ]
            )
        )
        _apply_severity_colors(table, rows)
        story.append(table)
        story.extend(
            [
                Spacer(1, 18),
                Paragraph("Authorization Notice", styles["Heading2"]),
                Paragraph(
                    "Use this platform only on systems you own or have explicit written permission to assess.",
                    styles["Normal"],
                ),
                Paragraph(
                    "The client remains responsible for approving testing scope and implementing remediation.",
                    styles["Normal"],
                ),
            ]
        )

        doc = SimpleDocTemplate(str(path), pagesize=A4)
        doc.build(story)
        return str(path)


def _cell(text: str, styles: dict) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), styles["SmallCell"])


def _risk_score_table(score: int) -> Table:
    if score >= 80:
        label = "Critical"
        color = colors.HexColor("#c62828")
    elif score >= 60:
        label = "High"
        color = colors.HexColor("#ef7d00")
    elif score >= 35:
        label = "Medium"
        color = colors.HexColor("#b88700")
    else:
        label = "Low"
        color = colors.HexColor("#168a46")

    table = Table([[f"Risk Score: {score} / 100", f"Level: {label}"]], colWidths=[250, 220])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 16),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d7dde5")),
            ]
        )
    )
    return table


def _operations_table(operations: list[dict], styles: dict) -> Table:
    rows = [["Time", "Type", "Target", "Status", "Details"]]
    for operation in operations:
        rows.append(
            [
                _cell(str(operation.get("timestamp", "")), styles),
                _cell(str(operation.get("type", "scan")), styles),
                _cell(str(operation.get("target", "unknown")), styles),
                _cell(str(operation.get("status", "unknown")), styles),
                _cell(str(operation.get("explanation", "")), styles),
            ]
        )

    table = Table(rows, repeatRows=1, colWidths=[95, 70, 105, 60, 140])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#22384f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7dde5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef6ff")]),
            ]
        )
    )

    for index, operation in enumerate(operations, start=1):
        status = str(operation.get("status", "")).lower()
        if status == "success":
            color = colors.HexColor("#e7f6ed")
        elif status in {"blocked", "error", "failed"}:
            color = colors.HexColor("#fdeaea")
        else:
            color = colors.HexColor("#fff7db")
        table.setStyle(TableStyle([("BACKGROUND", (3, index), (3, index), color)]))

    return table


def _apply_severity_colors(table: Table, rows: list[list]) -> None:
    for index, row in enumerate(rows[1:], start=1):
        severity_text = str(row[1]).lower()
        if "critical" in severity_text or "high" in severity_text:
            color = colors.HexColor("#fdeaea")
        elif "medium" in severity_text:
            color = colors.HexColor("#fff2cc")
        else:
            color = colors.HexColor("#e7f6ed")
        table.setStyle(TableStyle([("BACKGROUND", (1, index), (1, index), color)]))
