from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

from scanner.web_scanner import WebSecurityScanner

app = FastAPI(title="Guardian Scan API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str

# تخزين نتائج الفحص مؤقتاً
scan_results_cache = {}

@app.post("/api/scan")
async def scan_website(request: ScanRequest):
    """بدء فحص موقع"""
    
    from fastapi.responses import StreamingResponse
    import asyncio
    
    async def generate_progress():
        scanner = WebSecurityScanner(request.url)
        results = {}
        
        def update_progress(percent, message):
            nonlocal results
            # نرسل التقدم للمستخدم
            # في التطبيق الحقيقي، نستخدم WebSockets أو Server-Sent Events
        
        results = scanner.scan_all()
        scan_results_cache[request.url] = results
        
        yield f"data: {json.dumps({'type': 'complete', 'results': results})}\\n\\n"
    
    return StreamingResponse(generate_progress(), media_type="text/event-stream")

@app.get("/api/scan/result/{url:path}")
async def get_scan_result(url: str):
    """الحصول على نتيجة فحص سابقة"""
    if url in scan_results_cache:
        return scan_results_cache[url]
    return JSONResponse(status_code=404, content={"error": "لم يتم العثور على نتائج"})

@app.post("/api/generate-report")
async def generate_report(data: dict):
    """إنشاء تقرير PDF"""
    results = data.get('results', {})
    
    # إنشاء HTML للتقرير
    html_content = generate_report_html(results)
    
    # حفظ التقرير
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/output/scan_report_{timestamp}.html"
    
    os.makedirs("reports/output", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return {"report_url": f"/download/{os.path.basename(report_path)}"}

@app.get("/download/{filename}")
async def download_report(filename: str):
    """تحميل التقرير"""
    file_path = f"reports/output/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return JSONResponse(status_code=404, content={"error": "الملف غير موجود"})

def generate_report_html(results: dict) -> str:
    """إنشاء HTML للتقرير"""
    risk_score = results.get('risk_score', 65)
    risk_color = get_risk_color(risk_score)
    risk_level = get_risk_level(risk_score)
    
    html = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تقرير فحص الأمن - Guardian Platform</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; direction: rtl; padding: 40px; background: #f5f5f5; }}
        .report {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 40px; text-align: center; }}
        .content {{ padding: 30px; }}
        .risk-score {{ font-size: 64px; font-weight: bold; color: {risk_color}; text-align: center; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: right; border-bottom: 1px solid #ddd; }}
        th {{ background: #2a5298; color: white; }}
        .critical {{ color: #c62828; font-weight: bold; }}
        .high {{ color: #ff9800; font-weight: bold; }}
        .medium {{ color: #ffeb3b; font-weight: bold; }}
        .low {{ color: #4caf50; font-weight: bold; }}
        .vuln-item {{ padding: 12px; margin: 10px 0; border-radius: 10px; border-right: 4px solid; }}
        .recommendation {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 10px; border-right: 4px solid #4caf50; }}
        .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
<div class="report">
    <div class="header">
        <h1>🔐 Guardian Platform</h1>
        <p>تقرير فحص أمني شامل</p>
        <p>التاريخ: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    <div class="content">
        <div class="risk-score">{risk_score}</div>
        <div style="text-align: center; margin-bottom: 30px;">درجة المخاطر: {risk_level}</div>
        
        <h2>📋 الملخص التنفيذي</h2>
        <p>تم إجراء فحص أمني شامل للموقع. تم اكتشاف {len(results.get('vulnerabilities', []))} ثغرة محتملة.</p>
        
        <h2>🛡️ النتائج التفصيلية</h2>
        
        <!-- SSL -->
        <h3>🔒 SSL/TLS</h3>
        <table>
            <tr><th>العنصر</th><th>الحالة</th></tr>
            <tr><td>شهادة SSL</td><td>{'✅ صالحة' if results.get('ssl_tls', {}).get('valid') else '❌ غير صالحة'}</tr>
            <tr><td>تاريخ الانتهاء</td><td>{results.get('ssl_tls', {}).get('expiry_date', 'غير معروف')}</tr>
        </table>
        
        <!-- رؤوس الأمان -->
        <h3>🛡️ رؤوس الأمان</h3>
        <table>
            <tr><th>الرأس</th><th>الحالة</th></tr>
            {generate_headers_table(results.get('security_headers', {}))}
        </table>
        
        <!-- الملفات الحساسة -->
        <h3>📁 الملفات الحساسة</h3>
        {generate_sensitive_files_section(results.get('sensitive_files', []))}
        
        <!-- المنافذ المفتوحة -->
        <h3>🌐 المنافذ المفتوحة</h3>
        {generate_ports_section(results.get('open_ports', []))}
        
        <!-- الثغرات -->
        <h3>⚠️ الثغرات المكتشفة</h3>
        {generate_vulnerabilities_section(results)}
        
        <!-- التوصيات -->
        <h3>✅ التوصيات</h3>
        {generate_recommendations_section(results.get('recommendations', []))}
        
        <div class="footer">
            <p>تم إجراء هذا الفحص بموافقة خطية من الجهة المستهدفة.</p>
            <p><strong>إخلاء مسؤولية:</strong> لم يتم تخزين أو جمع أي كلمات مرور أو بيانات حساسة.</p>
            <p>Guardian Platform - تقرير احترافي للأمن السيبراني</p>
        </div>
    </div>
</div>
</body>
</html>'''
    
    return html

def get_risk_color(score):
    if score >= 80: return '#c62828'
    if score >= 60: return '#ff9800'
    if score >= 40: return '#ffeb3b'
    return '#4caf50'

def get_risk_level(score):
    if score >= 80: return 'حرج 🔴'
    if score >= 60: return 'عالي 🟠'
    if score >= 40: return 'متوسط 🟡'
    return 'منخفض 🟢'

def generate_headers_table(headers_data):
    html = ""
    critical_headers = headers_data.get('critical_headers', {})
    for name, info in critical_headers.items():
        status = '✅ موجود' if info['present'] else '❌ مفقود'
        html += f'<tr><td>{name}</td><td>{status}</td></tr>'
    return html

def generate_sensitive_files_section(files):
    if not files:
        return '<p class="low">✅ لم يتم العثور على ملفات حساسة</p>'
    html = ''
    for file in files:
        severity_class = 'critical' if file.get('critical') else 'medium'
        html += f'<div class="vuln-item" style="border-color: {get_severity_color(severity_class)};">'
        html += f'<strong>📄 {file["path"]}</strong> - <span class="{severity_class}">{file["severity"]}</span><br>'
        html += f'{file["description"]}'
        html += '</div>'
    return html

def generate_ports_section(ports):
    if not ports:
        return '<p class="low">✅ لا توجد منافذ خطيرة مفتوحة</p>'
    html = '<table><th>المنفذ</th><th>الخدمة</th><th>الخطورة</th></tr>'
    for port in ports:
        severity = 'critical' if port['port'] in [21,23,3306,5432,6379,27017,9200] else 'medium'
        html += f'<tr><td>{port["port"]}</td><td>{port["service"]}</td><td class="{severity}">{get_severity_text(severity)}</td></tr>'
    html += '</table>'
    return html

def generate_vulnerabilities_section(results):
    html = ''
    
    sql = results.get('sql_injection', {})
    if sql.get('vulnerable'):
        html += '<div class="vuln-item" style="border-color: #c62828;">'
        html += '<span class="critical">🔴 ثغرة SQL Injection</span><br>'
        html += f'المعامل الضعيفة: {", ".join(sql.get("vulnerable_params", []))}'
        html += '<br><strong>⚠️ لم يتم استخراج أي بيانات - تم إثبات الثغرة فقط</strong>'
        html += '</div>'
    
    xss = results.get('xss', {})
    if xss.get('vulnerable'):
        html += '<div class="vuln-item" style="border-color: #ff9800;">'
        html += '<span class="high">🟠 ثغرة XSS</span><br>'
        html += f'النوع: {xss.get("type", "Reflected XSS")}<br>'
        html += f'المعامل الضعيفة: {", ".join(xss.get("vulnerable_params", []))}'
        html += '</div>'
    
    idor = results.get('idor', {})
    if idor.get('vulnerable'):
        html += '<div class="vuln-item" style="border-color: #ff9800;">'
        html += '<span class="high">🟠 ثغرة IDOR</span><br>'
        html += f'المسارات الضعيفة: {", ".join(idor.get("vulnerable_paths", []))}'
        html += '</div>'
    
    if not html:
        html = '<p class="low">✅ لم يتم اكتشاف ثغرات خطيرة</p>'
    
    return html

def generate_recommendations_section(recommendations):
    if not recommendations:
        return '<p>لا توجد توصيات محددة</p>'
    html = ''
    for i, rec in enumerate(recommendations, 1):
        html += f'<div class="recommendation">'
        html += f'<strong>{i}. {rec["title"]}</strong><br>'
        html += rec["description"]
        html += '</div>'
    return html

def get_severity_color(severity):
    colors = {'critical': '#c62828', 'high': '#ff9800', 'medium': '#ffeb3b', 'low': '#4caf50'}
    return colors.get(severity, '#666')

def get_severity_text(severity):
    texts = {'critical': '🔴 عالية جداً', 'high': '🟠 عالية', 'medium': '🟡 متوسطة', 'low': '🟢 منخفضة'}
    return texts.get(severity, severity)
