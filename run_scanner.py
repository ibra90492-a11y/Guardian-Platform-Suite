#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guardian Web Security Scanner - نظام التشغيل
ماسح المواقع الأمني الشامل
"""

import os
import sys
import subprocess
import webbrowser
import time

def setup_and_run():
    """إعداد وتشغيل النظام"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🔐 Guardian Web Security Scanner 🔐                       ║
║        ماسح المواقع الأمني الشامل                               ║
║                                                                  ║
║   يفحص: SSL | رؤوس الأمان | ثغرات | منافذ | وأكثر              ║
║                                                                  ║
║   النسخة: 2.0.0 | الدعم: اللغة العربية                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print("\\n📂 إنشاء المجلدات الأساسية...")
    os.makedirs("frontend", exist_ok=True)
    os.makedirs("reports/output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    print("✅ تم إنشاء المجلدات")
    
    print("\\n🔧 التحقق من المكتبات المطلوبة...")
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("requests", "Requests"),
        ("jinja2", "Jinja2"),
        ("pydantic", "Pydantic"),
    ]
    
    for package, display_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {display_name} موجود")
        except ImportError:
            print(f"📥 تثبيت {display_name}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "-q"],
                capture_output=True
            )
            print(f"✅ تم تثبيت {display_name}")
    
    print("\\n" + "="*65)
    print("🚀 تشغيل النظام...")
    print("="*65)
    print("\\n📍 رابط الواجهة الرئيسية:")
    print("   🔗 http://localhost:8000")
    print("\\n📖 توثيق API:")
    print("   🔗 http://localhost:8000/docs")
    print("\\n⚠️  لإيقاف الخادم: اضغط Ctrl+C")
    print("="*65 + "\\n")
    
    time.sleep(1)
    
    print("⏳ فتح المتصفح...")
    try:
        webbrowser.open("http://localhost:8000")
    except:
        print("⚠️  تعذر فتح المتصفح تلقائياً. افتح: http://localhost:8000")
    
    time.sleep(2)
    
    # تشغيل FastAPI
    print("\\n▶️  تشغيل خادم FastAPI...\\n")
    print("-" * 65)
    
    try:
        os.system("uvicorn backend.api.scan_api:app --host 0.0.0.0 --port 8000 --reload")
    except KeyboardInterrupt:
        print("\\n\\n⛔ تم إيقاف الخادم من قبل المستخدم")
        sys.exit(0)

if __name__ == "__main__":
    try:
        setup_and_run()
    except Exception as e:
        print(f"\\n❌ خطأ: {str(e)}")
        sys.exit(1)
