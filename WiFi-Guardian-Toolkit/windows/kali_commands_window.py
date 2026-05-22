# -*- coding: utf-8 -*-
"""نافذة أوامر Kali Linux"""

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import threading

from utils.constants import BG, PANEL_BG, GREEN, CYAN, FONT_BUTTON, FONT_NORMAL
from core.terminal_executor import TerminalExecutor


class KaliCommandsWindow:
    """نافذة تنفيذ أوامر Kali"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        self.output_text = None
        self.command_entry = None
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Kali Linux Commands")
        self.window.geometry("650x600")
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء الواجهة"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # العنوان
        tk.Label(container, text="Kali Linux Commands",
                fg=GREEN, bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 15))
        
        # حقل إدخال الأمر
        tk.Label(container, text="Enter Command:",
                fg=CYAN, bg=BG, font=("Tahoma", 11, "bold"),
                anchor="w").pack(fill=tk.X)
        
        input_frame = tk.Frame(container, bg=BG)
        input_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.command_entry = tk.Entry(input_frame, bg=PANEL_BG, fg="white",
                                       font=FONT_NORMAL, relief=tk.FLAT)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.command_entry.bind("<Return>", lambda e: self._execute_command())
        
        tk.Button(input_frame, text="Run",
                 command=self._execute_command,
                 bg="#0f766e", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=15).pack(side=tk.RIGHT, padx=5)
        
        # أوامر سريعة
        quick_frame = tk.Frame(container, bg=BG)
        quick_frame.pack(fill=tk.X, pady=5)
        
        quick_commands = ["ip addr", "ping google.com", "whoami", "pwd", "ls -la"]
        for cmd in quick_commands:
            tk.Button(quick_frame, text=cmd,
                     command=lambda c=cmd: self._set_command(c),
                     bg="#334155", fg="white", font=("Tahoma", 9),
                     relief=tk.FLAT, cursor="hand2", padx=8, pady=3).pack(side=tk.LEFT, padx=3)
        
        # حقل الإخراج
        tk.Label(container, text="Output:",
                fg=CYAN, bg=BG, font=("Tahoma", 11, "bold"),
                anchor="w").pack(fill=tk.X, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            container, bg=PANEL_BG, fg="#00ff00",
            font=("Consolas", 10), wrap=tk.WORD,
            relief=tk.FLAT, height=15
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def _set_command(self, command):
        """تعيين الأمر في حقل الإدخال"""
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, command)
    
    def _execute_command(self):
        """تنفيذ الأمر"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        self.output_text.insert(tk.END, f"\n$ {command}\n")
        self.output_text.see(tk.END)
        
        def execute():
            output = TerminalExecutor.execute_kali_command(command)
            if self.window and self.window.winfo_exists():
                self.window.after(0, lambda: self.output_text.insert(tk.END, f"{output}\n"))
                self.window.after(0, lambda: self.output_text.see(tk.END))
        
        threading.Thread(target=execute, daemon=True).start()
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
