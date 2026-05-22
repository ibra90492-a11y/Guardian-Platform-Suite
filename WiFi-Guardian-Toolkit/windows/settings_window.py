# -*- coding: utf-8 -*-
"""نافذة الإعدادات - Settings"""

import tkinter as tk
from tkinter import ttk, messagebox

from utils.constants import BG, PANEL_BG, GREEN, CYAN, FONT_BUTTON


class SettingsWindow:
    """نافذة الإعدادات"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        self.mode_var = None
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("450x400")
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء الواجهة"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # العنوان
        tk.Label(container, text="Settings",
                fg=GREEN, bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 15))
        
        # إطار الإعدادات
        settings_frame = tk.Frame(container, bg=PANEL_BG, relief=tk.RIDGE, bd=2)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # وضع التشغيل
        tk.Label(settings_frame, text="Operation Mode:",
                fg=CYAN, bg=PANEL_BG, font=("Tahoma", 12, "bold"),
                anchor="w").grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.mode_var = tk.StringVar(value=self.app.operation_mode)
        mode_frame = tk.Frame(settings_frame, bg=PANEL_BG)
        mode_frame.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        tk.Radiobutton(mode_frame, text="Defensive", variable=self.mode_var,
                      value="defensive", bg=PANEL_BG, fg="white",
                      selectcolor=PANEL_BG).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Lab", variable=self.mode_var,
                      value="lab", bg=PANEL_BG, fg="white",
                      selectcolor=PANEL_BG).pack(side=tk.LEFT, padx=5)
        
        # فصل
        separator = ttk.Separator(settings_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        
        # معلومات
        tk.Label(settings_frame, text="Application Info:",
                fg=CYAN, bg=PANEL_BG, font=("Tahoma", 12, "bold"),
                anchor="w").grid(row=2, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")
        
        info_text = f"""
Version: 1.0.0
Python: {__import__('sys').version.split()[0]}
Platform: {__import__('platform').system()}
        """
        tk.Label(settings_frame, text=info_text,
                fg="white", bg=PANEL_BG, font=("Tahoma", 10),
                anchor="w", justify=tk.LEFT).grid(row=3, column=0, columnspan=2, padx=15, pady=5, sticky="w")
        
        # أزرار
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(fill=tk.X, pady=15)
        
        tk.Button(btn_frame, text="Save",
                 command=self._save_settings,
                 bg="#0f766e", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel",
                 command=self._close,
                 bg="#991b1b", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
    
    def _save_settings(self):
        """حفظ الإعدادات"""
        new_mode = self.mode_var.get()
        self.app.operation_mode = new_mode
        messagebox.showinfo("Settings", f"Settings saved.\nOperation Mode: {new_mode}")
        self._close()
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
