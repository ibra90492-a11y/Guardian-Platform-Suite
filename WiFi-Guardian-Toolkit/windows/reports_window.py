# -*- coding: utf-8 -*-
"""نافذة التقارير - Reports"""

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import os

from utils.constants import BG, PANEL_BG, GREEN, CYAN, FONT_BUTTON, FONT_NORMAL
from utils.pdf_generator import generate_terminal_report


class ReportsWindow:
    """نافذة عرض وإنشاء التقارير"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        self.report_text = None
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Reports")
        self.window.geometry("650x600")
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        self._show_summary()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء الواجهة"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # العنوان
        tk.Label(container, text="Reports",
                fg=GREEN, bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 15))
        
        # حقل عرض التقرير
        self.report_text = scrolledtext.ScrolledText(
            container, bg=PANEL_BG, fg="#00ff00",
            font=("Consolas", 10), wrap=tk.WORD,
            relief=tk.FLAT, height=15
        )
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # أزرار
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(fill=tk.X, pady=15)
        
        tk.Button(btn_frame, text="Generate PDF Report",
                 command=self._generate_pdf,
                 bg="#0f766e", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Refresh",
                 command=self._show_summary,
                 bg="#1d4ed8", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Copy",
                 command=self._copy,
                 bg="#334155", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
    
    def _show_summary(self):
        """عرض ملخص الأوامر المنفذة"""
        total_commands = 0
        for sessions in self.app._terminal_sessions_history.values():
            total_commands += len(sessions)
        
        summary = f"""
Terminal Commands Summary
{'=' * 50}

Total Commands Executed: {total_commands}

Commands by System:
"""
        for system, sessions in self.app._terminal_sessions_history.items():
            summary += f"  - {system}: {len(sessions)} command(s)\n"
        
        summary += f"""
Last System Used: {self.app._last_terminal_system or 'None'}
Protection Status: {'Active' if self.app.protection_active else 'Inactive'}
Operation Mode: {self.app.operation_mode}

{'=' * 50}
To generate a detailed PDF report, click the button above.
"""
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, summary)
    
    def _generate_pdf(self):
        """إنشاء تقرير PDF"""
        result, success = generate_terminal_report(
            self.app._terminal_sessions_history,
            self.app._last_terminal_system,
            self.app.protection_active,
            self.app.operation_mode
        )
        
        if success:
            try:
                os.startfile(result)
            except AttributeError:
                pass
            self.report_text.insert(tk.END, f"\n\nPDF report saved to:\n{result}")
            self.report_text.see(tk.END)
        else:
            self.report_text.insert(tk.END, f"\n\nError: {result}")
    
    def _copy(self):
        """نسخ النص"""
        text = self.report_text.get(1.0, tk.END)
        self.window.clipboard_clear()
        self.window.clipboard_append(text)
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
