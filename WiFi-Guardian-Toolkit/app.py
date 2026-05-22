# -*- coding: utf-8 -*-
"""التطبيق الرئيسي - WiFi Guardian Toolkit"""

import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import webbrowser

from HackingTools import HackingToolsWindow
from utils.constants import BG, GREEN, CYAN, FONT_TITLE
from windows import (
    LinkingCodexWindow,
    NetworkInfoWindow,
    SettingsWindow,
    ToolsWindow,
    KaliCommandsWindow,
    DNSInfoWindow,
    ProtectionWindow,
    ReportsWindow
)


class PreventTrackingApp:
    """التطبيق الرئيسي"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.system = "Windows"
        self._force_foreground = os.environ.get("WIFI_GUARDIAN_FORCE_FOREGROUND") == "1"
        
        # متغيرات الحالة
        self.protection_active = False
        self.operation_mode = "defensive"
        self._terminal_sessions_history = {
            "kali-linux windows": [],
            "PowerShell": [],
            "CMD": [],
        }
        self._last_terminal_system = ""
        
        # تهيئة النوافذ
        self.linking_codex_window = LinkingCodexWindow(self.root, self)
        self.network_info_window = NetworkInfoWindow(self.root, self)
        self.settings_window = SettingsWindow(self.root, self)
        self.tools_window = ToolsWindow(self.root, self)
        self.kali_commands_window = KaliCommandsWindow(self.root, self)
        self.dns_info_window = DNSInfoWindow(self.root, self)
        self.protection_window = ProtectionWindow(self.root, self)
        self.reports_window = ReportsWindow(self.root, self)
        self.hacking_tools_window = HackingToolsWindow(self.root, self)
        
        self._build_ui()

        if self._force_foreground:
            self.root.after(200, self._raise_to_foreground)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # لا يتم فتح أي نافذة إضافية تلقائياً عند تشغيل التطبيق.
    
    def _build_ui(self):
        """بناء الواجهة الرئيسية"""
        self.root.title("WiFi Guardian Toolkit")
        self.root.geometry("1380x860")
        self.root.minsize(1260, 780)
        self.root.configure(bg=BG)
        
        main_container = tk.Frame(self.root, bg=BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=22, pady=16)
        
        # العنوان
        tk.Label(main_container, text="WiFi Guardian Toolkit",
                fg=GREEN, bg=BG, font=FONT_TITLE,
                anchor="center").pack(fill=tk.X, pady=(0, 12))
        
        # أزرار الاختصار السريع
        shortcuts_frame = tk.Frame(main_container, bg=BG)
        shortcuts_frame.pack(fill=tk.X, pady=(0, 14))
        for column in range(3):
            shortcuts_frame.grid_columnconfigure(column, weight=1, uniform="quick")
        
        quick_buttons = [
            ("Linking Codex", self._open_linking_codex, "#0f766e"),
            ("Terminal", self._open_terminal, "#3f3f3f"),
            ("Chrome", self._open_chrome, "#1d4ed8"),
        ]
        
        quick_font = ("Tahoma", 14, "bold")
        for column, (text, cmd, color) in enumerate(quick_buttons):
            tk.Button(shortcuts_frame, text=text, command=cmd,
                     bg=color, fg="white", font=quick_font,
                     relief=tk.FLAT, cursor="hand2",
                     width=18, height=2).grid(row=0, column=column, sticky="nsew", padx=8)

        tk.Label(
            main_container,
            text="الأزرار مرتبة في 3 أعمدة من اليسار إلى اليمين.",
            fg=CYAN,
            bg=BG,
            font=("Tahoma", 12, "bold"),
            anchor="center",
        ).pack(fill=tk.X, pady=(2, 10))

        # الشبكة الرئيسية للأزرار
        nav_grid = tk.Frame(main_container, bg=BG)
        nav_grid.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        nav_buttons = [
            ("Network Info", self._open_network_info, "#3f3f3f"),
            ("Settings", self._open_settings, "#1d4ed8"),
            ("Tools", self._open_tools, "#1a4d5c"),
            ("Kali Commands", self._open_kali_commands, "#0f766e"),
            ("DNS Info", self._open_dns_info, "#7c2d12"),
            ("Protection", self._open_protection, "#334155"),
            ("Reports", self._open_reports, "#0f766e"),
            ("Hacking Tools / أدوات الاختراق", self._open_hacking_tools, "#111827"),
            ("فحص الثغرات / Vulnerability Scan", self._vulnerability_scan, "#164e63"),
            ("اختبار الاختراق / Penetration Test", self._penetration_test, "#374151"),
            ("محاكاة هجوم / Attack Simulation", self._attack_simulation, "#4c1d95"),
            ("تحليل المخاطر / Risk Assessment", self._risk_assessment, "#075985"),
            ("فحص الحماية / Security Audit", self._security_audit, "#166534"),
            ("كشف الاختراق / Breach Detection", self._breach_detection, "#7f1d1d"),
            ("🔍 Port Scanner", self._port_scan, "#0f766e"),
            ("🔐 Password Strength", self._check_password_strength, "#1d4ed8"),
            ("🌐 DNS Spoof Test", self._test_dns_security, "#7c2d12"),
            ("📡 MITM Simulation", self._simulate_mitm, "#334155"),
            ("🔓 SQL Injection Test", self._test_sql_injection, "#581c87"),
            ("📧 Phishing Simulator", self._simulate_phishing, "#92400e"),
        ]

        nav_font = ("Tahoma", 13, "bold")
        for column in range(3):
            nav_grid.grid_columnconfigure(column, weight=1, uniform="nav")

        row_count = (len(nav_buttons) + 2) // 3
        for row in range(row_count):
            nav_grid.grid_rowconfigure(row, weight=1)

        for index, (text, cmd, color) in enumerate(nav_buttons):
            row, column = divmod(index, 3)
            tk.Button(nav_grid, text=text, command=cmd,
                     bg=color, fg="white", font=nav_font,
                     relief=tk.FLAT, cursor="hand2", anchor="center",
                     justify=tk.CENTER, wraplength=250,
                     width=28, height=3).grid(
                         row=row,
                         column=column,
                         sticky="nsew",
                         padx=8,
                         pady=8,
                     )
        
        # شريط الحالة
        self.status_var = tk.StringVar(value="STATUS: READY")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              fg=CYAN, bg=BG, font=("Consolas", 11, "bold"),
                              anchor="w")
        status_bar.pack(fill=tk.X, padx=18, pady=(10, 10))
    
    # ============== دوال فتح النوافذ ==============
    
    def _open_linking_codex(self):
        self.linking_codex_window.open()
    
    def _open_network_info(self):
        self.network_info_window.open()
    
    def _open_settings(self):
        self.settings_window.open()
    
    def _open_tools(self):
        self.tools_window.open()
    
    def _open_kali_commands(self):
        self.kali_commands_window.open()
    
    def _open_dns_info(self):
        self.dns_info_window.open()
    
    def _open_protection(self):
        self.protection_window.open()
    
    def _open_reports(self):
        self.reports_window.open()

    def _open_hacking_tools(self):
        self.hacking_tools_window.open()

    # ============== أزرار الفحص الدفاعي ==============

    def _show_defensive_action(self, title, usage):
        """عرض وصف آمن للأزرار الدفاعية بدون تنفيذ تلقائي."""
        self._set_status(title.upper())
        messagebox.showinfo(
            title,
            f"{usage}\n\nيستخدم هذا الخيار داخل بيئة تملكها أو لديك تصريح صريح لاختبارها فقط."
        )

    def _vulnerability_scan(self):
        self._show_defensive_action("Vulnerability Scan", "فحص نقاط الضعف في نظامك.")

    def _penetration_test(self):
        self._show_defensive_action("Penetration Test", "اختبار أمان بترخيص مسبق.")

    def _attack_simulation(self):
        self._show_defensive_action("Attack Simulation", "محاكاة مضبوطة داخل بيئة اختبار.")

    def _risk_assessment(self):
        self._show_defensive_action("Risk Assessment", "تقييم المخاطر الأمنية.")

    def _security_audit(self):
        self._show_defensive_action("Security Audit", "تدقيق أمني شامل.")

    def _breach_detection(self):
        self._show_defensive_action("Breach Detection", "اكتشاف محاولات الاختراق ومؤشرات الخطر.")

    def _port_scan(self):
        self._show_defensive_action("Port Scanner", "فحص المنافذ المفتوحة على أجهزتك المصرح بها.")

    def _check_password_strength(self):
        self._show_defensive_action("Password Strength", "تحليل قوة كلمات المرور بدون حفظها.")

    def _test_dns_security(self):
        self._show_defensive_action("DNS Spoof Test", "اختبار مقاومة إعدادات DNS للتلاعب في بيئة مرخصة.")

    def _simulate_mitm(self):
        self._show_defensive_action("MITM Simulation", "محاكاة تعليمية مضبوطة لاختبار دفاعات الشبكة.")

    def _test_sql_injection(self):
        self._show_defensive_action("SQL Injection Test", "اختبار تطبيقاتك المرخصة ضد حقن SQL.")

    def _simulate_phishing(self):
        self._show_defensive_action("Phishing Simulator", "تدريب توعوي داخلي على رسائل التصيد بدون استهداف خارجي.")
    
    # ============== دوال مساعدة ==============

    def _raise_to_foreground(self):
        """رفع نافذة WiFi Toolkit إلى المقدمة عند تشغيلها من الفورم الرئيسي."""
        try:
            self.root.update_idletasks()
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.root.attributes("-topmost", True)
            self.root.after(300, lambda: self.root.attributes("-topmost", False))
        except tk.TclError:
            pass
    
    def _open_terminal(self):
        """فتح Windows Terminal"""
        try:
            subprocess.Popen(["wt"], shell=False)
        except Exception:
            subprocess.Popen(["cmd"], shell=False)
    
    def _open_chrome(self):
        """فتح Chrome"""
        webbrowser.open("https://www.google.com")
    
    def _set_status(self, status):
        """تحديث شريط الحالة"""
        self.status_var.set(f"STATUS: {status}")
    
    def _on_close(self):
        """إغلاق التطبيق"""
        self.root.destroy()
    
    def run(self):
        """تشغيل التطبيق"""
        self.root.mainloop()
