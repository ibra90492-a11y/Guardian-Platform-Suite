# -*- coding: utf-8 -*-
"""إنشاء تقارير PDF بالأوامر المنفذة ونتائجها"""

import os
import time
import socket
import platform
from datetime import datetime


def generate_terminal_report(terminal_history, last_system, protection_active, operation_mode):
    """توليد تقرير PDF بجميع الأوامر المنفذة"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(reports_dir, f"terminal_report_{timestamp}.pdf")
        
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'],
                                      fontSize=24, textColor=colors.HexColor('#0f766e'),
                                      alignment=TA_CENTER, spaceAfter=30)
        
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading3'],
                                        fontSize=16, textColor=colors.HexColor('#1d4ed8'),
                                        spaceAfter=12, spaceBefore=20)
        
        story.append(Paragraph("WiFi Guardian Toolkit - Terminal Report", title_style))
        story.append(Spacer(1, 0.2 * 72))
        
        # معلومات التقرير
        info_data = [
            ["Report Date:", time.strftime("%Y-%m-%d %H:%M:%S")],
            ["Hostname:", socket.gethostname()],
            ["OS:", platform.system()],
        ]
        
        info_table = Table(info_data, colWidths=[2.5 * 72, 4 * 72])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f2fe')),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * 72))
        
        # جمع الأوامر
        all_commands = []
        for system, sessions in terminal_history.items():
            if sessions:
                for session in sessions:
                    all_commands.append((system, session))
        
        if not all_commands:
            story.append(Paragraph("No commands have been executed yet.", section_style))
        else:
            story.append(Paragraph(f"Executed Commands ({len(all_commands)})", section_style))
            story.append(Spacer(1, 0.1 * 72))
            
            for idx, (system, transcript) in enumerate(all_commands, 1):
                lines = transcript.split('\n')
                user_request = ""
                terminal_command = ""
                terminal_output = ""
                
                for line in lines:
                    if line.startswith("User request:"):
                        user_request = line.replace("User request:", "").strip()
                    elif line.startswith("Terminal command:"):
                        terminal_command = line.replace("Terminal command:", "").strip()
                    elif line.startswith("Terminal response:"):
                        terminal_output = line.replace("Terminal response:", "").strip()
                
                system_icon = "Linux" if "kali" in system.lower() else "PS" if "powershell" in system.lower() else "CMD"
                
                story.append(Paragraph(f"{system_icon} Command #{idx} - System: {system}", styles['Heading4']))
                story.append(Spacer(1, 0.05 * 72))
                
                if user_request:
                    story.append(Paragraph(f"<b>User Request:</b> {user_request[:200]}", styles['Normal']))
                if terminal_command:
                    story.append(Paragraph(f"<b>Command:</b> <font color='#0f766e'>{terminal_command[:200]}</font>", styles['Normal']))
                if terminal_output:
                    output_preview = terminal_output[:800]
                    if len(terminal_output) > 800:
                        output_preview += "\n... (truncated)"
                    story.append(Paragraph(f"<b>Output:</b> <font color='#1a1a1a'>{output_preview}</font>", styles['Normal']))
                
                story.append(Spacer(1, 0.1 * 72))
                story.append(Paragraph("-" * 80, styles['Normal']))
                story.append(Spacer(1, 0.1 * 72))
        
        # إحصائيات
        stats_data = [
            ["Total Commands", str(len(all_commands))],
            ["Last System Used", last_system or "None"],
            ["Protection Status", "Active" if protection_active else "Inactive"],
            ["Operation Mode", operation_mode],
        ]
        
        stats_table = Table(stats_data, colWidths=[3 * 72, 3 * 72])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(stats_table)
        
        doc.build(story)
        return pdf_filename, True
        
    except ImportError:
        return "ReportLab not installed. Run: pip install reportlab", False
    except Exception as e:
        return f"PDF generation error: {str(e)}", False
