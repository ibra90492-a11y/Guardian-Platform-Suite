# -*- coding: utf-8 -*-
"""الثوابت والألوان والإعدادات العامة للمشروع"""

import os
from pathlib import Path

# ============================================================
# الألوان
# ============================================================
BG = "#0d0d0d"
PANEL_BG = "#1a1a1a"
GREEN = "#00ff00"
RED = "#ff4444"
CYAN = "#00ffff"
ORANGE = "#ffaa00"
MUTED = "#888888"

# ============================================================
# الخطوط
# ============================================================
FONT_TITLE = ("Arial", 20, "bold")
FONT_BUTTON = ("Tahoma", 12, "bold")
FONT_NORMAL = ("Tahoma", 10)
FONT_MONO = ("Consolas", 10)

# ============================================================
# مسارات الملفات
# ============================================================
BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = str(BASE_DIR / "codex_scripts")
REPORTS_DIR = str(BASE_DIR / "reports")
CODEX_SHORTCUT = str(BASE_DIR / "Codex.lnk")

# إنشاء المجلدات
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ============================================================
# إعدادات الطرفية
# ============================================================
KALI_TMUX_SESSION = "wifi_guardian_terminal"
KALI_PROJECT_DIR = str(BASE_DIR)
KALI_TERMINAL_TITLE = "WiFi Guardian Kali"
TERMINAL_WINDOW_SIZE = (560, 760)

# ============================================================
# الأوامر الصالحة للتنفيذ
# ============================================================
VALID_COMMANDS = [
    'ip', 'ping', 'nslookup', 'hostname', 'whoami', 'ls', 'cat', 'echo',
    'ifconfig', 'iw', 'arp', 'route', 'dig', 'curl', 'wget', 'netstat',
    'ss', 'traceroute', 'tracepath', 'mtr', 'tcpdump', 'sudo', 'wsl',
    'ipconfig', 'netsh', 'powershell', 'Get-', 'Set-', 'Test-'
]

# ============================================================
# الأنماط التي يتم تجاهلها في استخراج الأوامر
# ============================================================
SKIP_PATTERNS = [
    'تم إنشاء', 'تم حفظ', 'فشل', 'خطأ', 'تم نسخ', 'تم لصق',
    'طلب المستخدم', 'أمر الطرفية', 'رد الطرفية', 'نظام التشغيل',
    'python', '#!/usr', 'import', 'def ', 'class ', 'if __name__'
]
