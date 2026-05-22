# -*- coding: utf-8 -*-
"""نافذة معلومات DNS"""

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import threading

from utils.constants import BG, PANEL_BG, GREEN, CYAN, FONT_BUTTON, FONT_NORMAL
from utils.network_utils import test_doh_query, probe_host


class DNSInfoWindow:
    """نافذة عرض معلومات DNS"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        self.info_text = None
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("DNS Information")
        self.window.geometry("600x500")
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        self._refresh()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء الواجهة"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # العنوان
        tk.Label(container, text="DNS Information",
                fg=GREEN, bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 15))
        
        # حقل المعلومات
        self.info_text = scrolledtext.ScrolledText(
            container, bg=PANEL_BG, fg="#00ff00",
            font=("Consolas", 11), wrap=tk.WORD,
            relief=tk.FLAT, height=15
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # أزرار
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(fill=tk.X, pady=15)
        
        tk.Button(btn_frame, text="Refresh",
                 command=self._refresh,
                 bg="#0f766e", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Copy",
                 command=self._copy,
                 bg="#1d4ed8", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
    
    def _refresh(self):
        """تحديث المعلومات"""
        def worker():
            doh = test_doh_query()
            dot = probe_host("1.1.1.1", 853)
            
            info = f"""
DNS Status Report
{'=' * 50}

Cloudflare DNS (1.1.1.1):
  - DoH (DNS over HTTPS): {doh}
  - DoT (DNS over TLS): {dot}

Test Results:
  - DoH Query to cloudflare.com: {'Success' if doh == 'Yes' else 'Failed'}
  - DoT Connection to 1.1.1.1: {'Success' if dot == 'Yes' else 'Failed'}

Recommendations:
  - Use DoH for better privacy
  - Use DoT for secure DNS queries
  - Cloudflare DNS offers both protocols
"""
            if self.window and self.window.winfo_exists():
                self.window.after(0, lambda: self._update_text(info))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _update_text(self, text):
        """تحديث النص"""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
    
    def _copy(self):
        """نسخ النص"""
        text = self.info_text.get(1.0, tk.END)
        self.window.clipboard_clear()
        self.window.clipboard_append(text)
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
