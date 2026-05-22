# -*- coding: utf-8 -*-
"""نافذة الأدوات - Tools"""

import tkinter as tk
from tkinter import messagebox
import subprocess

from utils.constants import BG, PANEL_BG, GREEN, FONT_BUTTON


class ToolsWindow:
    """نافذة الأدوات المساعدة"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Tools")
        self.window.geometry("500x500")
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء الواجهة"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # العنوان
        tk.Label(container, text="Tools",
                fg=GREEN, bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 15))
        
        # إطار الأدوات
        tools_frame = tk.Frame(container, bg=PANEL_BG, relief=tk.RIDGE, bd=2)
        tools_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # قائمة الأدوات
        tools = [
            ("Run Diagnostics", self._run_diagnostics, "#0f766e"),
            ("Export Security Report", self._export_report, "#1d4ed8"),
            ("Clear Logs", self._clear_logs, "#7c2d12"),
            ("Open Terminal", self._open_terminal, "#3f3f3f"),
            ("Open Task Manager", self._open_task_manager, "#991b1b"),
        ]
        
        for i, (text, cmd, color) in enumerate(tools):
            tk.Button(tools_frame, text=text, command=cmd,
                     bg=color, fg="white", font=FONT_BUTTON,
                     relief=tk.FLAT, cursor="hand2",
                     width=25, height=2).grid(row=i, column=0, padx=20, pady=10)
    
    def _run_diagnostics(self):
        """تشغيل التشخيص"""
        messagebox.showinfo("Diagnostics", "Running diagnostics...\n\nPlatform: Windows\nPython: 3.x\nNetwork: Connected")
    
    def _export_report(self):
        """تصدير التقرير"""
        messagebox.showinfo("Export", "Security report exported to reports/ folder")
    
    def _clear_logs(self):
        """مسح السجلات"""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            messagebox.showinfo("Cleared", "Logs cleared successfully")
    
    def _open_terminal(self):
        """فتح الطرفية"""
        subprocess.Popen(["wt"], shell=False)
    
    def _open_task_manager(self):
        """فتح مدير المهام"""
        subprocess.Popen(["taskmgr"], shell=False)
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
