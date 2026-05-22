# -*- coding: utf-8 -*-
"""نافذة الحماية - Prevent Tracking"""

import tkinter as tk
from tkinter import messagebox
import threading

from utils.constants import BG, PANEL_BG, GREEN, RED, CYAN, FONT_BUTTON, FONT_NORMAL


class ProtectionWindow:
    """نافذة تفعيل الحماية"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        self.status_label = None
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("DNS Protection")
        self.window.geometry("500x400")
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء الواجهة"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # العنوان
        tk.Label(container, text="DNS Protection",
                fg=GREEN, bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 15))
        
        # إطار المعلومات
        info_frame = tk.Frame(container, bg=PANEL_BG, relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # حالة الحماية
        tk.Label(info_frame, text="Protection Status:",
                fg=CYAN, bg=PANEL_BG, font=("Tahoma", 12, "bold"),
                anchor="w").grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        status_text = "ACTIVE" if self.app.protection_active else "INACTIVE"
        status_color = GREEN if self.app.protection_active else RED
        
        self.status_label = tk.Label(info_frame, text=status_text,
                                      fg=status_color, bg=PANEL_BG,
                                      font=("Tahoma", 12, "bold"))
        self.status_label.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        # معلومات DNS
        tk.Label(info_frame, text="DNS Provider:",
                fg=CYAN, bg=PANEL_BG, font=("Tahoma", 11, "bold"),
                anchor="w").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        tk.Label(info_frame, text="Cloudflare (1.1.1.1)",
                fg="white", bg=PANEL_BG, font=FONT_NORMAL,
                anchor="w").grid(row=1, column=1, padx=15, pady=10, sticky="w")
        
        tk.Label(info_frame, text="Protocol:",
                fg=CYAN, bg=PANEL_BG, font=("Tahoma", 11, "bold"),
                anchor="w").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        tk.Label(info_frame, text="DNS over HTTPS (DoH)",
                fg="white", bg=PANEL_BG, font=FONT_NORMAL,
                anchor="w").grid(row=2, column=1, padx=15, pady=10, sticky="w")
        
        # أزرار
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(fill=tk.X, pady=15)
        
        if not self.app.protection_active:
            tk.Button(btn_frame, text="Activate Protection",
                     command=self._activate,
                     bg="#0f766e", fg="white", font=FONT_BUTTON,
                     relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Deactivate Protection",
                     command=self._deactivate,
                     bg="#991b1b", fg="white", font=FONT_BUTTON,
                     relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
    
    def _activate(self):
        """تفعيل الحماية"""
        def worker():
            self.app.protection_active = True
            if self.window and self.window.winfo_exists():
                self.window.after(0, lambda: self._update_status())
                self.window.after(0, lambda: messagebox.showinfo("Success", "Protection activated"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _deactivate(self):
        """إلغاء الحماية"""
        def worker():
            self.app.protection_active = False
            if self.window and self.window.winfo_exists():
                self.window.after(0, lambda: self._update_status())
                self.window.after(0, lambda: messagebox.showinfo("Success", "Protection deactivated"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _update_status(self):
        """تحديث حالة الحماية"""
        if self.status_label:
            status_text = "ACTIVE" if self.app.protection_active else "INACTIVE"
            status_color = GREEN if self.app.protection_active else RED
            self.status_label.config(text=status_text, fg=status_color)
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
