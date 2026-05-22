# -*- coding: utf-8 -*-
"""نافذة معلومات الشبكة - Network Information"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from utils.constants import BG, PANEL_BG, GREEN, CYAN, FONT_NORMAL, FONT_BUTTON
from utils.network_utils import get_ssid, get_local_ip, collect_cf_snapshot


class NetworkInfoWindow:
    """نافذة عرض معلومات الشبكة"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        self.info_vars = {}
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Network Information")
        self.window.geometry("550x600")
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        self._refresh_data()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء الواجهة"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # العنوان
        tk.Label(container, text="Network Information",
                fg=GREEN, bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 15))
        
        # إطار المعلومات
        info_frame = tk.Frame(container, bg=PANEL_BG, relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # حقول المعلومات
        fields = [
            ("SSID", "ssid"),
            ("IP Address", "ip_address"),
            ("DNS (DoH)", "doh"),
            ("DNS (DoT)", "dot"),
            ("WARP Status", "warp"),
            ("Location", "state"),
            ("Data Center", "cf_dc"),
            ("AS Name", "as_name"),
            ("AS Number", "as_number"),
        ]
        
        for i, (label, key) in enumerate(fields):
            tk.Label(info_frame, text=f"{label}:", fg=CYAN, bg=PANEL_BG,
                    font=("Tahoma", 11, "bold"), anchor="w").grid(row=i, column=0, padx=15, pady=8, sticky="w")
            
            self.info_vars[key] = tk.StringVar(value="Loading...")
            tk.Label(info_frame, textvariable=self.info_vars[key],
                    fg="white", bg=PANEL_BG, font=FONT_NORMAL,
                    anchor="w").grid(row=i, column=1, padx=15, pady=8, sticky="w")
        
        # أزرار التحكم
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(fill=tk.X, pady=15)
        
        tk.Button(btn_frame, text="Refresh",
                 command=self._refresh_data,
                 bg="#0f766e", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Copy All",
                 command=self._copy_all,
                 bg="#1d4ed8", fg="white", font=FONT_BUTTON,
                 relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
    
    def _refresh_data(self):
        """تحديث البيانات"""
        def worker():
            ssid = get_ssid()
            ip = get_local_ip()
            snapshot = collect_cf_snapshot()
            
            if not self.window or not self.window.winfo_exists():
                return

            self.window.after(0, lambda: self.info_vars["ssid"].set(ssid))
            self.window.after(0, lambda: self.info_vars["ip_address"].set(ip))
            self.window.after(0, lambda: self.info_vars["doh"].set(snapshot.get("doh", "No")))
            self.window.after(0, lambda: self.info_vars["dot"].set(snapshot.get("dot", "No")))
            self.window.after(0, lambda: self.info_vars["warp"].set(snapshot.get("warp", "No")))
            self.window.after(0, lambda: self.info_vars["state"].set(snapshot.get("state", "Unknown")))
            self.window.after(0, lambda: self.info_vars["cf_dc"].set(snapshot.get("cf_dc", "Unknown")))
            self.window.after(0, lambda: self.info_vars["as_name"].set(snapshot.get("as_name", "Unknown")))
            self.window.after(0, lambda: self.info_vars["as_number"].set(snapshot.get("as_number", "Unknown")))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _copy_all(self):
        """نسخ جميع المعلومات"""
        text = "Network Information Report\n"
        text += "=" * 40 + "\n"
        for key, var in self.info_vars.items():
            text += f"{key}: {var.get()}\n"
        
        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        messagebox.showinfo("Copied", "Information copied to clipboard")
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
