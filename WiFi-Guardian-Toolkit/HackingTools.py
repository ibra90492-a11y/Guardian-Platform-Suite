#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hacking Tools Module - Ethical Penetration Testing Tools
   Usage: These tools are for educational and authorized testing only.
"""

import json
import os
import platform
import re
import socket
import subprocess
import threading
import time
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from datetime import datetime
from tkinter import filedialog, messagebox

from core.terminal_executor import TerminalExecutor


class HackingTools:
    """أدوات اختبار الاختراق الأخلاقي - للأغراض التعليمية والاختبار المصرح به فقط"""
    
    def __init__(self):
        self.system = platform.system()
        self.results = {}
    
    # ============================================================
    # أدوات فحص الشبكة (Network Scanning)
    # ============================================================
    
    def port_scan(self, target, ports="20-100", timeout=1):
        """
        فحص المنافذ المفتوحة على هدف محدد
        الاستخدام: port_scan("192.168.1.1", "22,80,443", timeout=1)
        """
        open_ports = []
        port_list = self._parse_port_range(ports)
        
        for port in port_list:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                pass
        
        result = {
            "target": target,
            "open_ports": open_ports,
            "total_scanned": len(port_list),
            "timestamp": datetime.now().isoformat()
        }
        self.results["port_scan"] = result
        return result
    
    def _parse_port_range(self, ports):
        """تحويل نطاق المنافذ إلى قائمة"""
        if isinstance(ports, list):
            return ports
        
        if "-" in ports:
            start, end = map(int, ports.split("-"))
            return list(range(start, end + 1))
        elif "," in ports:
            return [int(p.strip()) for p in ports.split(",")]
        else:
            return [int(ports)]
    
    def ping_sweep(self, network_prefix, start=1, end=254, timeout=0.5):
        """
        فحص الأجهزة الحية في الشبكة (Ping Sweep)
        الاستخدام: ping_sweep("192.168.1", 1, 254)
        """
        active_hosts = []
        
        for i in range(start, end + 1):
            ip = f"{network_prefix}.{i}"
            if self.system == "Windows":
                cmd = ["ping", "-n", "1", "-w", str(max(int(timeout * 1000), 1)), ip]
            else:
                cmd = ["ping", "-c", "1", "-W", str(max(int(timeout), 1)), ip]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=max(timeout + 1, 2)
                )
                if result.returncode == 0:
                    active_hosts.append(ip)
            except Exception:
                pass
        
        result = {
            "network": f"{network_prefix}.0/24",
            "active_hosts": active_hosts,
            "count": len(active_hosts),
            "timestamp": datetime.now().isoformat()
        }
        self.results["ping_sweep"] = result
        return result
    
    # ============================================================
    # أدوات DNS (DNS Tools)
    # ============================================================
    
    def dns_lookup(self, domain, record_type="A"):
        """
        استعلام DNS لأنواع مختلفة من السجلات
        الأنواع: A, AAAA, MX, NS, TXT, CNAME
        """
        try:
            import dns.resolver
            answers = dns.resolver.resolve(domain, record_type)
            records = [str(answer) for answer in answers]
            result = {
                "domain": domain,
                "record_type": record_type,
                "records": records,
                "status": "success"
            }
        except Exception as e:
            result = {
                "domain": domain,
                "record_type": record_type,
                "records": [],
                "status": "failed",
                "error": str(e)
            }
        self.results["dns_lookup"] = result
        return result
    
    def reverse_dns(self, ip):
        """الحصول على اسم المضيف من عنوان IP (Reverse DNS)"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            result = {
                "ip": ip,
                "hostname": hostname,
                "status": "success"
            }
        except Exception:
            result = {
                "ip": ip,
                "hostname": None,
                "status": "failed"
            }
        self.results["reverse_dns"] = result
        return result
    
    # ============================================================
    # أدوات الويب (Web Tools)
    # ============================================================
    
    def check_headers(self, url):
        """فحص رؤوس HTTP لموقع معين"""
        try:
            import httpx
            response = httpx.get(url, timeout=10, follow_redirects=True)
            headers = dict(response.headers)
            
            security_headers = [
                "X-Frame-Options",
                "X-Content-Type-Options",
                "Strict-Transport-Security",
                "Content-Security-Policy",
                "X-XSS-Protection"
            ]
            
            missing_headers = [h for h in security_headers if h not in headers]
            
            result = {
                "url": url,
                "status_code": response.status_code,
                "missing_security_headers": missing_headers,
                "all_headers": headers,
                "status": "success"
            }
        except Exception as e:
            result = {
                "url": url,
                "status": "failed",
                "error": str(e)
            }
        self.results["check_headers"] = result
        return result
    
    def subdomain_enum(self, domain, wordlist=None):
        """
        تعداد النطاقات الفرعية (Subdomain Enumeration)
        الاستخدام: subdomain_enum("example.com", ["www", "mail", "admin"])
        """
        if wordlist is None:
            wordlist = [
                "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop",
                "ns1", "webdisk", "ns2", "cpanel", "whm", "autodiscover",
                "autoconfig", "api", "blog", "admin", "dev", "test", "staging"
            ]
        
        found_subdomains = []
        
        for sub in wordlist:
            subdomain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(subdomain)
                found_subdomains.append(subdomain)
            except Exception:
                pass
        
        result = {
            "domain": domain,
            "found_subdomains": found_subdomains,
            "count": len(found_subdomains),
            "timestamp": datetime.now().isoformat()
        }
        self.results["subdomain_enum"] = result
        return result
    
    # ============================================================
    # أدوات النظام (System Tools)
    # ============================================================
    
    def get_system_info(self):
        """جمع معلومات عن النظام"""
        info = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.system == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "os", "get", "Caption,Version,InstallDate,LastBootUpTime"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                info["windows_info"] = result.stdout.strip()
            except Exception:
                pass
        else:
            try:
                result = subprocess.run(
                    ["uname", "-a"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                info["uname"] = result.stdout.strip()
            except Exception:
                pass
        
        self.results["system_info"] = info
        return info
    
    def get_network_interfaces(self):
        """الحصول على معلومات واجهات الشبكة"""
        if self.system == "Windows":
            try:
                result = subprocess.run(
                    ["ipconfig", "/all"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                data = {
                    "status": "success",
                    "data": result.stdout[:5000],
                    "system": self.system
                }
                self.results["network_interfaces"] = data
                return data
            except Exception:
                pass
        else:
            try:
                result = subprocess.run(
                    ["ip", "addr", "show"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                data = {
                    "status": "success",
                    "data": result.stdout,
                    "system": self.system
                }
                self.results["network_interfaces"] = data
                return data
            except Exception:
                pass
        
        return {"status": "failed", "error": "Could not retrieve interfaces"}
    
    def get_routing_table(self):
        """الحصول على جدول التوجيه"""
        if self.system == "Windows":
            cmd = ["route", "print"]
        else:
            cmd = ["route", "-n"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            data = {
                "status": "success",
                "routing_table": result.stdout[:3000],
                "system": self.system
            }
        except Exception as e:
            data = {"status": "failed", "error": str(e)}
        self.results["routing_table"] = data
        return data
    
    # ============================================================
    # أدوات المراقبة (Monitoring Tools)
    # ============================================================
    
    def traceroute(self, target, max_hops=30):
        """
        تتبع مسار الحزم إلى الهدف
        الاستخدام: traceroute("google.com")
        """
        if self.system == "Windows":
            cmd = ["tracert", "-d", "-h", str(max_hops), target]
        else:
            cmd = ["traceroute", "-n", "-m", str(max_hops), target]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            data = {
                "target": target,
                "hops": result.stdout,
                "status": "success"
            }
        except Exception as e:
            data = {
                "target": target,
                "status": "failed",
                "error": str(e)
            }
        self.results["traceroute"] = data
        return data
    
    def whois_lookup(self, domain):
        """استعلام WHOIS لنطاق معين"""
        try:
            import whois
            w = whois.whois(domain)
            
            data = {
                "domain": domain,
                "registrar": w.registrar,
                "creation_date": str(w.creation_date),
                "expiration_date": str(w.expiration_date),
                "name_servers": w.name_servers,
                "status": "success"
            }
        except ImportError:
            data = {
                "domain": domain,
                "status": "failed",
                "error": "whois library not installed. Run: pip install python-whois"
            }
        except Exception as e:
            data = {
                "domain": domain,
                "status": "failed",
                "error": str(e)
            }
        self.results["whois_lookup"] = data
        return data
    
    # ============================================================
    # أدوات التشفير (Encryption Tools)
    # ============================================================
    
    @staticmethod
    def hash_string(text, algorithm="sha256"):
        """
        حساب هاش لنص معين
        الخوارزميات: md5, sha1, sha256, sha512
        """
        import hashlib
        
        text_bytes = text.encode('utf-8')
        
        if algorithm == "md5":
            result = hashlib.md5(text_bytes).hexdigest()
        elif algorithm == "sha1":
            result = hashlib.sha1(text_bytes).hexdigest()
        elif algorithm == "sha256":
            result = hashlib.sha256(text_bytes).hexdigest()
        elif algorithm == "sha512":
            result = hashlib.sha512(text_bytes).hexdigest()
        else:
            result = hashlib.sha256(text_bytes).hexdigest()
        
        return {
            "input": text,
            "algorithm": algorithm,
            "hash": result,
            "length": len(result)
        }
    
    @staticmethod
    def base64_encode(text):
        """تشفير نص إلى Base64"""
        import base64
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return {"original": text, "encoded": encoded, "method": "base64"}
    
    @staticmethod
    def base64_decode(encoded):
        """فك تشفير Base64"""
        import base64
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            return {"encoded": encoded, "decoded": decoded, "status": "success"}
        except Exception:
            return {"encoded": encoded, "status": "failed", "error": "Invalid base64"}
    
    # ============================================================
    # أدوات توليد البيانات (Data Generation)
    # ============================================================
    
    @staticmethod
    def generate_password(length=12, use_symbols=True):
        """
        توليد كلمة مرور عشوائية قوية
        """
        import random
        import string
        
        chars = string.ascii_letters + string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        return {
            "password": password,
            "length": length,
            "has_symbols": use_symbols,
            "strength": HackingTools._check_password_strength(password)
        }
    
    @staticmethod
    def _check_password_strength(password):
        """تقييم قوة كلمة المرور"""
        score = 0
        if len(password) >= 12:
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 1
        
        if score >= 5:
            return "Very Strong"
        elif score >= 4:
            return "Strong"
        elif score >= 3:
            return "Medium"
        elif score >= 2:
            return "Weak"
        else:
            return "Very Weak"
    
    # ============================================================
    # أدوات التحليل (Analysis Tools)
    # ============================================================
    
    def analyze_log_file(self, log_path, patterns=None):
        """
        تحليل ملف سجل للبحث عن أنماط محددة
        """
        if patterns is None:
            patterns = {
                "error": r"(?i)error|fail|exception|critical",
                "warning": r"(?i)warning|warn",
                "attack": r"(?i)sql injection|xss|command injection|path traversal",
                "auth": r"(?i)login|auth|password|credential"
            }
        
        results = {key: [] for key in patterns}
        total_lines = 0
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    total_lines = line_num
                    for category, pattern in patterns.items():
                        if re.search(pattern, line):
                            results[category].append({
                                "line": line_num,
                                "content": line.strip()[:200]
                            })
            
            data = {
                "file": log_path,
                "analysis": results,
                "total_lines": total_lines,
                "status": "success"
            }
        except Exception as e:
            data = {
                "file": log_path,
                "status": "failed",
                "error": str(e)
            }
        self.results["log_analysis"] = data
        return data
    
    # ============================================================
    # أدوات التقرير (Report Tools)
    # ============================================================
    
    def export_results_to_json(self, filename=None):
        """تصدير جميع النتائج إلى ملف JSON"""
        if filename is None:
            filename = f"hacking_tools_report_{int(time.time())}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.get_system_info(),
            "results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return {
            "filename": filename,
            "size": os.path.getsize(filename),
            "status": "success"
        }
    
    def clear_results(self):
        """مسح جميع النتائج المخزنة"""
        self.results = {}
        return {"status": "cleared", "timestamp": datetime.now().isoformat()}


class HackingToolsWindow:
    """نافذة أدوات الاختراق الأخلاقي داخل التطبيق."""

    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        self.tools = HackingTools()
        self.target_entry = None
        self.ports_entry = None
        self.domain_entry = None
        self.text_entry = None
        self.output_text = None
        self.terminal_frame = None
        self.terminal_button = None
        self.terminal_dropdown = None
        self.terminal_hide_after_id = None
        self.terminal_option_buttons = []
        self.terminal_option_base_bg = "#111827"
        self.terminal_option_hover_bg = "#012456"
        self.active_terminal_mode = None
        self.terminal_input_start = "1.0"
        self.terminal_is_running = False

    def open(self):
        """فتح الفورم."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Hacking tools أدوات الإختراق")
        self.window.geometry("780x760")
        self.window.minsize(680, 640)
        self.window.configure(bg="#0d0d0d")
        self.window.transient(self.parent)
        self.window.protocol("WM_DELETE_WINDOW", self._close)

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self.window, bg="#0d0d0d")
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        tk.Label(
            container,
            text="Hacking tools أدوات الإختراق",
            fg="#00ff00",
            bg="#0d0d0d",
            font=("Arial", 20, "bold"),
            anchor="center",
        ).pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            container,
            text="Ethical and authorized testing only - للاستخدام التعليمي والاختبار المصرح فقط",
            fg="#00ffff",
            bg="#0d0d0d",
            font=("Tahoma", 10, "bold"),
            anchor="center",
        ).pack(fill=tk.X, pady=(0, 12))

        input_frame = tk.Frame(container, bg="#1a1a1a", relief=tk.RIDGE, bd=2)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.target_entry = self._add_labeled_entry(input_frame, "Target/IP:", "127.0.0.1", 0, 0)
        self.ports_entry = self._add_labeled_entry(input_frame, "Ports:", "22,80,443", 0, 2)
        self.domain_entry = self._add_labeled_entry(input_frame, "Domain/URL:", "https://example.com", 1, 0)
        self.text_entry = self._add_labeled_entry(input_frame, "Text:", "Hello World", 1, 2)

        buttons_frame = tk.Frame(container, bg="#0d0d0d")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))

        buttons = [
            ("Tools Details\nتفاصيل الأدوات", self._show_tools_details, "#0f172a"),
            ("System Info\nمعلومات النظام", self._run_system_info, "#334155"),
            ("Network Interfaces\nواجهات الشبكة", self._run_network_interfaces, "#334155"),
            ("Routing Table\nجدول التوجيه", self._run_routing_table, "#334155"),
            ("Port Scan\nفحص المنافذ", self._run_port_scan, "#0f766e"),
            ("DNS Lookup\nاستعلام DNS", self._run_dns_lookup, "#1d4ed8"),
            ("Reverse DNS\nDNS عكسي", self._run_reverse_dns, "#1d4ed8"),
            ("HTTP Headers\nرؤوس HTTP", self._run_headers, "#7c2d12"),
            ("Traceroute\nتتبع المسار", self._run_traceroute, "#075985"),
            ("Hash Text\nحساب الهاش", self._run_hash_text, "#581c87"),
            ("Base64 Encode\nتشفير Base64", self._run_base64_encode, "#581c87"),
            ("Generate Password\nتوليد كلمة مرور", self._run_generate_password, "#166534"),
            ("Export JSON\nتصدير JSON", self._run_export_json, "#92400e"),
            ("Clear\nمسح", self._clear_output, "#991b1b"),
            ("Scripts\nسكربتات", self._open_scripts_window, "#0f172a"),
        ]

        for index, (text, command, color) in enumerate(buttons):
            row = index // 3
            col = index % 3
            tk.Button(
                buttons_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Tahoma", 8, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                width=23,
                height=2,
            ).grid(row=row, column=col, padx=4, pady=4, sticky="ew")

        for col in range(3):
            buttons_frame.grid_columnconfigure(col, weight=1)

        self.terminal_frame = tk.Frame(
            container,
            bg="#00ff00",
            highlightbackground="#00ff00",
            highlightcolor="#00ff00",
            highlightthickness=2,
            bd=0,
        )
        self.terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.output_text = scrolledtext.ScrolledText(
            self.terminal_frame,
            bg="#111827",
            fg="#00ff00",
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            height=16,
            insertbackground="#00ff00",
            insertwidth=2,
            insertontime=600,
            insertofftime=300,
            padx=8,
            pady=8,
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.output_text.bind("<Return>", self._handle_terminal_enter)
        self.output_text.bind("<Button-1>", self._keep_terminal_cursor_editable)
        self.output_text.bind("<KeyPress>", self._keep_terminal_input_area)
        self.output_text.bind("<Control-v>", self._paste_into_terminal)
        self.output_text.bind("<Control-V>", self._paste_into_terminal)
        self.output_text.bind("<Control-c>", self._copy_from_terminal)
        self.output_text.bind("<Control-C>", self._copy_from_terminal)

        terminal_actions = tk.Frame(container, bg="#0d0d0d")
        terminal_actions.pack(fill=tk.X, pady=(0, 2))

        tk.Button(
            terminal_actions,
            text="Copy نسخ",
            command=self._copy_terminal_output,
            bg="#0f766e",
            fg="white",
            font=("Tahoma", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=22,
            pady=7,
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            terminal_actions,
            text="Delete حذف",
            command=self._delete_terminal_output,
            bg="#991b1b",
            fg="white",
            font=("Tahoma", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=22,
            pady=7,
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.terminal_button = tk.Button(
            terminal_actions,
            text="Terminal الطرفية",
            command=self._show_terminal_dropdown,
            bg="#111827",
            fg="white",
            font=("Tahoma", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=22,
            pady=7,
        )
        self.terminal_button.pack(side=tk.LEFT)
        self.terminal_button.bind("<Enter>", lambda _event: self._show_terminal_dropdown())
        self.terminal_button.bind("<FocusIn>", lambda _event: self._show_terminal_dropdown())
        self.terminal_button.bind("<Motion>", lambda _event: self._show_terminal_dropdown())
        self.terminal_button.bind("<Button-1>", lambda _event: self._show_terminal_dropdown())
        self.terminal_button.bind("<Leave>", lambda _event: self._schedule_terminal_dropdown_hide())

        self._write_output("Ready. Use only on systems you own or have explicit permission to test.\n")

    def _add_labeled_entry(self, parent, label, default, row, col):
        tk.Label(
            parent,
            text=label,
            fg="#00ffff",
            bg="#1a1a1a",
            font=("Tahoma", 10, "bold"),
            anchor="w",
        ).grid(row=row, column=col, padx=(10, 4), pady=8, sticky="w")

        entry = tk.Entry(parent, bg="#0d0d0d", fg="white", insertbackground="white", relief=tk.FLAT)
        entry.insert(0, default)
        entry.grid(row=row, column=col + 1, padx=(0, 10), pady=8, sticky="ew")
        parent.grid_columnconfigure(col + 1, weight=1)
        return entry

    def _run_async(self, title, func):
        def worker():
            try:
                result = func()
            except Exception as error:
                result = {"status": "failed", "error": str(error)}

            if self.window and self.window.winfo_exists():
                self.window.after(0, lambda: self._show_result(title, result))

        self._write_output(f"\nRunning: {title}\n")
        threading.Thread(target=worker, daemon=True).start()

    def _show_result(self, title, result):
        self._write_output(f"\n=== {title} ===\n")
        self._write_output(json.dumps(result, ensure_ascii=False, indent=2))
        self._write_output("\n")
        self.app._set_status(f"HACKING TOOLS - {title.upper()}")

    def _write_output(self, text):
        if not self.output_text:
            return
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def _get_target(self):
        return self.target_entry.get().strip() or "127.0.0.1"

    def _get_domain_or_url(self):
        return self.domain_entry.get().strip() or "https://example.com"

    def _show_tools_details(self):
        """عرض تفاصيل الأدوات في فورم صغير في المنتصف."""
        details_window = tk.Toplevel(self.window)
        details_window.title("Tools Details تفاصيل الأدوات")
        details_window.geometry("620x520")
        details_window.configure(bg="#0d0d0d")
        details_window.transient(self.window)
        details_window.grab_set()

        details_window.update_idletasks()
        width = 620
        height = 520
        x = self.window.winfo_rootx() + max((self.window.winfo_width() - width) // 2, 0)
        y = self.window.winfo_rooty() + max((self.window.winfo_height() - height) // 2, 0)
        details_window.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(
            details_window,
            text="Tools Details تفاصيل الأدوات",
            fg="#00ff00",
            bg="#0d0d0d",
            font=("Arial", 16, "bold"),
        ).pack(fill=tk.X, pady=(14, 8))

        details_text = """ملخص الدوال الموجودة في الملف

أدوات فحص الشبكة:
  port_scan() - فحص المنافذ
  ping_sweep() - فحص الأجهزة الحية

أدوات DNS:
  dns_lookup() - استعلام DNS
  reverse_dns() - Reverse DNS

أدوات الويب:
  check_headers() - فحص رؤوس HTTP
  subdomain_enum() - تعداد النطاقات الفرعية

أدوات النظام:
  get_system_info() - معلومات النظام
  get_network_interfaces() - واجهات الشبكة
  get_routing_table() - جدول التوجيه

أدوات المراقبة:
  traceroute() - تتبع المسار
  whois_lookup() - استعلام WHOIS

أدوات التشفير:
  hash_string() - حساب هاش
  base64_encode() - تشفير Base64
  base64_decode() - فك Base64

أدوات التوليد:
  generate_password() - توليد كلمة مرور

أدوات التحليل:
  analyze_log_file() - تحليل ملفات السجل

أدوات التقرير:
  export_results_to_json() - تصدير النتائج
  clear_results() - مسح النتائج
"""

        text_box = scrolledtext.ScrolledText(
            details_window,
            bg="#111827",
            fg="white",
            font=("Tahoma", 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=12,
            pady=12,
            height=18,
        )
        text_box.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))
        text_box.insert(tk.END, details_text)
        text_box.config(state=tk.DISABLED)

        tk.Button(
            details_window,
            text="Close إغلاق",
            command=details_window.destroy,
            bg="#991b1b",
            fg="white",
            font=("Tahoma", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=18,
            pady=7,
        ).pack(pady=(0, 12))

    def _run_system_info(self):
        self._run_async("System Info", self.tools.get_system_info)

    def _run_network_interfaces(self):
        self._run_async("Network Interfaces", self.tools.get_network_interfaces)

    def _run_routing_table(self):
        self._run_async("Routing Table", self.tools.get_routing_table)

    def _run_port_scan(self):
        target = self._get_target()
        ports = self.ports_entry.get().strip() or "22,80,443"
        self._run_async("Port Scan", lambda: self.tools.port_scan(target, ports))

    def _run_dns_lookup(self):
        domain = self._get_domain_or_url().replace("https://", "").replace("http://", "").split("/")[0]
        self._run_async("DNS Lookup", lambda: self.tools.dns_lookup(domain, "A"))

    def _run_reverse_dns(self):
        target = self._get_target()
        self._run_async("Reverse DNS", lambda: self.tools.reverse_dns(target))

    def _run_headers(self):
        url = self._get_domain_or_url()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        self._run_async("HTTP Headers", lambda: self.tools.check_headers(url))

    def _run_traceroute(self):
        target = self._get_domain_or_url().replace("https://", "").replace("http://", "").split("/")[0]
        self._run_async("Traceroute", lambda: self.tools.traceroute(target))

    def _run_hash_text(self):
        text = self.text_entry.get().strip() or "Hello World"
        self._run_async("Hash Text", lambda: self.tools.hash_string(text, "sha256"))

    def _run_base64_encode(self):
        text = self.text_entry.get().strip() or "Hello World"
        self._run_async("Base64 Encode", lambda: self.tools.base64_encode(text))

    def _run_generate_password(self):
        self._run_async("Generate Password", lambda: self.tools.generate_password(16))

    def _run_export_json(self):
        self._run_async("Export JSON", self.tools.export_results_to_json)

    def _open_scripts_window(self):
        """فتح فورم سكربتات الرسائل الآمن."""
        scripts_window = tk.Toplevel(self.window)
        scripts_window.title("Scripts سكربتات")
        scripts_window.geometry("760x680")
        scripts_window.minsize(660, 560)
        scripts_window.configure(bg="#0d0d0d")
        scripts_window.transient(self.window)

        selected_file = tk.StringVar(value="")
        message_type_var = tk.StringVar(value="")
        field_vars = {}

        container = tk.Frame(scripts_window, bg="#0d0d0d")
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        tk.Label(
            container,
            text="Scripts سكربتات",
            fg="#00ff00",
            bg="#0d0d0d",
            font=("Arial", 19, "bold"),
        ).pack(fill=tk.X, pady=(0, 8))

        icons_frame = tk.Frame(container, bg="#0d0d0d")
        icons_frame.pack(fill=tk.X, pady=(0, 10))

        type_frame = tk.Frame(container, bg="#1a1a1a", relief=tk.RIDGE, bd=2)
        type_frame.pack(fill=tk.X, pady=(0, 10))

        form_frame = tk.Frame(container, bg="#0d0d0d")
        form_frame.pack(fill=tk.BOTH, expand=True)

        status_var = tk.StringVar(value="اختر نوع الرسالة لعرض الحقول المناسبة.")

        def set_type(value):
            message_type_var.set(value)
            rebuild_fields()

        icon_buttons = [
            ("WhatsApp", "WhatsAPP", "#16a34a"),
            ("X", "X", "#111827"),
            ("Gmail", "Gmail", "#b91c1c"),
            ("TikTok", "TikTok", "#0f172a"),
            ("Telegram", "Telegram", "#0284c7"),
        ]

        for text, value, color in icon_buttons:
            tk.Button(
                icons_frame,
                text=text,
                command=lambda selected=value: set_type(selected),
                bg=color,
                fg="white",
                font=("Tahoma", 10, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                width=13,
                height=2,
            ).pack(side=tk.LEFT, padx=4)

        tk.Label(
            type_frame,
            text="نوع الرسالة:",
            fg="#00ffff",
            bg="#1a1a1a",
            font=("Tahoma", 11, "bold"),
        ).pack(side=tk.LEFT, padx=(10, 6), pady=10)

        type_menu = tk.OptionMenu(
            type_frame,
            message_type_var,
            "Text",
            "WhatsAPP",
            "Gmail",
            "X",
            "TikTok",
            "Telegram",
            command=lambda value: rebuild_fields(),
        )
        type_menu.configure(bg="#111827", fg="white", activebackground="#012456", activeforeground="white")
        type_menu.pack(side=tk.LEFT, padx=6, pady=8)

        tk.Label(
            container,
            textvariable=status_var,
            fg="#facc15",
            bg="#0d0d0d",
            font=("Tahoma", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 6))

        def clear_form():
            for child in form_frame.winfo_children():
                child.destroy()
            field_vars.clear()

        def add_entry(parent, label, key, row, col=0, show=None, hint=""):
            tk.Label(
                parent,
                text=label,
                fg="#00ffff",
                bg="#1a1a1a",
                font=("Tahoma", 10, "bold"),
                anchor="w",
            ).grid(row=row, column=col, padx=10, pady=(8, 2), sticky="w")
            var = tk.StringVar(value=hint)
            entry = tk.Entry(
                parent,
                textvariable=var,
                show=show,
                bg="#0d0d0d",
                fg="white",
                insertbackground="white",
                relief=tk.FLAT,
            )
            entry.grid(row=row + 1, column=col, padx=10, pady=(0, 8), sticky="ew")
            parent.grid_columnconfigure(col, weight=1)
            field_vars[key] = var
            return entry

        def add_text(parent, label, key, row):
            tk.Label(
                parent,
                text=label,
                fg="#00ffff",
                bg="#1a1a1a",
                font=("Tahoma", 10, "bold"),
                anchor="w",
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=(8, 2), sticky="w")
            text = scrolledtext.ScrolledText(
                parent,
                bg="#0d0d0d",
                fg="white",
                insertbackground="white",
                height=7,
                wrap=tk.WORD,
                relief=tk.FLAT,
            )
            text.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="nsew")
            parent.grid_rowconfigure(row + 1, weight=1)
            field_vars[key] = text
            return text

        def choose_attachment():
            path = filedialog.askopenfilename(
                title="اختر ملفاً للإرفاق كمرفق عادي ظاهر",
                filetypes=[
                    ("All files", "*.*"),
                ],
            )
            if path:
                selected_file.set(path)
                status_var.set(f"تم اختيار المرفق: {os.path.basename(path)}")

        def validate_phone(value):
            return bool(re.fullmatch(r"9665\d{8}", value.strip()))

        def get_field_value(key):
            widget_or_var = field_vars.get(key)
            if isinstance(widget_or_var, tk.StringVar):
                return widget_or_var.get().strip()
            if widget_or_var:
                return widget_or_var.get("1.0", tk.END).strip()
            return ""

        def send_gmail_message():
            import mimetypes
            import smtplib
            import ssl
            from email.message import EmailMessage

            sender = get_field_value("sender_email")
            password = get_field_value("app_password")
            recipient = get_field_value("recipient_email")
            subject = get_field_value("subject")
            body = get_field_value("body")
            attachment_path = selected_file.get().strip()

            message = EmailMessage()
            message["From"] = sender
            message["To"] = recipient
            message["Subject"] = subject
            message.set_content(body)

            if attachment_path:
                if not os.path.exists(attachment_path):
                    raise FileNotFoundError("Attachment file was not found.")

                size_mb = os.path.getsize(attachment_path) / (1024 * 1024)
                if size_mb > 24:
                    raise ValueError("Attachment is larger than 24MB. Gmail may reject large attachments.")

                mime_type, _encoding = mimetypes.guess_type(attachment_path)
                if not mime_type:
                    mime_type = "application/octet-stream"
                maintype, subtype = mime_type.split("/", 1)

                with open(attachment_path, "rb") as file_handle:
                    message.add_attachment(
                        file_handle.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(attachment_path),
                    )

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender, password)
                server.send_message(message)

        def run_gmail_send():
            def worker():
                try:
                    send_gmail_message()
                    scripts_window.after(0, lambda: status_var.set("تم إرسال رسالة Gmail بنجاح."))
                    scripts_window.after(0, lambda: messagebox.showinfo("Gmail", "تم إرسال الرسالة بنجاح."))
                except Exception as error:
                    scripts_window.after(0, lambda: status_var.set(f"فشل إرسال Gmail: {error}"))
                    scripts_window.after(0, lambda: messagebox.showerror("Gmail", f"فشل الإرسال:\n{error}"))

            status_var.set("جاري إرسال رسالة Gmail...")
            threading.Thread(target=worker, daemon=True).start()

        def submit_message():
            msg_type = message_type_var.get()
            if not msg_type:
                messagebox.showwarning("Scripts", "اختر نوع الرسالة أولاً.")
                return

            if msg_type == "Gmail":
                required = ["sender_email", "app_password", "recipient_email", "subject", "body"]
                missing = [key for key in required if not get_field_value(key)]
                if missing:
                    messagebox.showwarning("Gmail", "أكمل جميع حقول Gmail قبل الإرسال.")
                    return

                if not messagebox.askyesno(
                    "Gmail",
                    "سيتم إرسال الرسالة فعلياً عبر Gmail SMTP.\n"
                    "المرفق سيكون ظاهراً كمرفق عادي، بدون تخفي أو تمويه.\n\n"
                    "هل تريد المتابعة؟"
                ):
                    return

                run_gmail_send()
                return
            elif msg_type in ("WhatsAPP", "Telegram"):
                sender = get_field_value("sender_phone")
                recipient = get_field_value("recipient_phone")
                if not validate_phone(sender) or not validate_phone(recipient):
                    messagebox.showwarning("Phone Format", "اكتب أرقام الجوال بالشكل: 9665XXXXXXXX")
                    return
                messagebox.showinfo(msg_type, "تم تجهيز بيانات الرسالة بدون إرسال تلقائي.")
            else:
                messagebox.showinfo(msg_type, "تم تجهيز بيانات الرسالة بدون إرسال تلقائي.")

            status_var.set("تم تجهيز البيانات. لا يتم إخفاء سكربتات داخل الملفات أو تمويه المرفقات.")

        def rebuild_fields():
            clear_form()
            msg_type = message_type_var.get()
            if not msg_type:
                status_var.set("اختر نوع الرسالة لعرض الحقول المناسبة.")
                return

            panel = tk.Frame(form_frame, bg="#1a1a1a", relief=tk.RIDGE, bd=2)
            panel.pack(fill=tk.BOTH, expand=True)

            if msg_type == "Gmail":
                status_var.set("Gmail: تظهر حقول البريد، كلمة مرور التطبيق، المستلم، العنوان، النص، والمرفق.")
                add_entry(panel, "البريد الإلكتروني للمرسل", "sender_email", 0, 0)
                add_entry(panel, "Application password", "app_password", 0, 1, show="*")
                add_entry(panel, "البريد الإلكتروني للمستلم", "recipient_email", 2, 0)
                add_entry(panel, "عنوان الرسالة", "subject", 2, 1)
                add_text(panel, "نص الرسالة", "body", 4)
            elif msg_type in ("WhatsAPP", "Telegram"):
                status_var.set(f"{msg_type}: اكتب أرقام الجوال بالشكل 9665XXXXXXXX.")
                add_entry(panel, "رقم جوال المرسل", "sender_phone", 0, 0, hint="9665XXXXXXXX")
                add_entry(panel, "رقم جوال المستقبل", "recipient_phone", 0, 1, hint="9665XXXXXXXX")
                add_entry(panel, "اسم الحساب أو البريد للحساب", "account_name", 2, 0)
                add_entry(panel, "موضوع الرسالة", "subject", 2, 1)
                add_text(panel, "نص الرسالة", "body", 4)
            elif msg_type in ("TikTok", "X"):
                status_var.set(f"{msg_type}: تظهر حقول الحساب والرسالة فقط.")
                add_entry(panel, "حساب المرسل أو البريد", "sender_account", 0, 0)
                add_entry(panel, "حساب المستقبل", "recipient_account", 0, 1)
                add_entry(panel, "موضوع الرسالة", "subject", 2, 0)
                add_text(panel, "نص الرسالة", "body", 4)
            else:
                status_var.set("Text: تظهر حقول نصية عامة.")
                add_entry(panel, "عنوان الرسالة", "subject", 0, 0)
                add_text(panel, "نص الرسالة", "body", 2)

            attachment_frame = tk.Frame(panel, bg="#1a1a1a")
            attachment_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=8, sticky="ew")
            tk.Button(
                attachment_frame,
                text="إرفاق ملف",
                command=choose_attachment,
                bg="#334155",
                fg="white",
                font=("Tahoma", 10, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=14,
                pady=7,
            ).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(
                attachment_frame,
                textvariable=selected_file,
                fg="white",
                bg="#1a1a1a",
                font=("Tahoma", 9),
                anchor="w",
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(
                panel,
                text="يمكن اختيار أي نوع ملف كمرفق عادي ظاهر. لا يتم دعم إخفاء سكربتات داخل ملفات أو صور.",
                fg="#facc15",
                bg="#1a1a1a",
                font=("Tahoma", 9, "bold"),
                anchor="w",
            ).grid(row=9, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")

            tk.Button(
                panel,
                text="Send Message إرسال الرسالة",
                command=submit_message,
                bg="#0f766e",
                fg="white",
                font=("Tahoma", 11, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=16,
                pady=8,
            ).grid(row=10, column=0, columnspan=2, padx=10, pady=(0, 12), sticky="ew")

        scripts_window.protocol("WM_DELETE_WINDOW", scripts_window.destroy)

    def _clear_output(self):
        self.tools.clear_results()
        self.output_text.delete("1.0", tk.END)
        self._write_output("Cleared.\n")

    def _copy_terminal_output(self):
        """نسخ كل محتوى الطرفية."""
        if not self.output_text:
            return

        text = self.output_text.get("1.0", tk.END).strip()
        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        self.window.update()
        self._write_output("\n[OK] Terminal output copied to clipboard.\n")

    def _copy_from_terminal(self, _event=None):
        """نسخ التحديد داخل الطرفية أو كامل الطرفية عند عدم وجود تحديد."""
        if not self.output_text:
            return "break"

        try:
            text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            text = self.output_text.get("1.0", tk.END).strip()

        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        self.window.update()
        return "break"

    def _paste_into_terminal(self, _event=None):
        """لصق النص داخل منطقة إدخال الطرفية."""
        if not self.output_text:
            return "break"

        try:
            text = self.window.clipboard_get()
        except tk.TclError:
            return "break"

        if self.output_text.compare(tk.INSERT, "<", self.terminal_input_start):
            self.output_text.mark_set(tk.INSERT, tk.END)

        self.output_text.insert(tk.INSERT, text)
        self.output_text.focus_set()
        self.output_text.see(tk.INSERT)
        return "break"

    def _delete_terminal_output(self):
        """حذف كل محتوى الطرفية."""
        if not self.output_text:
            return
        self.output_text.delete("1.0", tk.END)
        self.terminal_input_start = "1.0"

    def _show_terminal_dropdown(self):
        """إظهار قائمة أنماط الطرفية أسفل زر Terminal."""
        if not self.terminal_button:
            return

        self._cancel_terminal_dropdown_hide()

        if self.terminal_dropdown and self.terminal_dropdown.winfo_exists():
            self.terminal_dropdown.lift()
            return

        self.terminal_dropdown = tk.Toplevel(self.window)
        self.terminal_dropdown.overrideredirect(True)
        self.terminal_dropdown.configure(bg="#00ff00")
        self.terminal_dropdown.transient(self.window)
        self.terminal_option_buttons = []

        dropdown_width = 260
        dropdown_height = 108
        x = self.terminal_button.winfo_rootx()
        y = self.terminal_button.winfo_rooty() - dropdown_height
        self.terminal_dropdown.geometry(f"{dropdown_width}x{dropdown_height}+{x}+{max(y, 0)}")

        options = [
            ("Kali Linux (WSL / Bash Shell)", "kali"),
            ("PowerShell", "powershell"),
            ("Command Prompt CMD", "cmd"),
        ]

        for label, mode in options:
            option_button = tk.Button(
                self.terminal_dropdown,
                text=label,
                command=lambda selected=mode: self._select_terminal_mode(selected),
                bg=self.terminal_option_base_bg,
                fg="white",
                activebackground=self.terminal_option_hover_bg,
                activeforeground="white",
                font=("Tahoma", 9, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                anchor="w",
                height=1,
            )
            option_button.pack(fill=tk.X, padx=1, pady=(1 if not self.terminal_option_buttons else 0, 0), ipady=5)
            self.terminal_option_buttons.append(option_button)
            option_button.bind(
                "<Enter>",
                lambda _event, button=option_button: self._highlight_terminal_option(button)
            )
            option_button.bind(
                "<Motion>",
                lambda _event, button=option_button: self._highlight_terminal_option(button)
            )
            option_button.bind(
                "<FocusIn>",
                lambda _event, button=option_button: self._highlight_terminal_option(button)
            )

        self.terminal_dropdown.bind("<Enter>", lambda _event: self._cancel_terminal_dropdown_hide())
        self.terminal_dropdown.bind("<FocusIn>", lambda _event: self._cancel_terminal_dropdown_hide())
        self.terminal_dropdown.bind("<Leave>", lambda _event: self._schedule_terminal_dropdown_hide())

    def _highlight_terminal_option(self, active_button):
        """نقل خلفية التمييز فوراً إلى الخيار الذي يمر عليه المؤشر."""
        self._cancel_terminal_dropdown_hide()
        for button in self.terminal_option_buttons:
            if button.winfo_exists():
                if button is active_button:
                    button.configure(bg=self.terminal_option_hover_bg)
                else:
                    button.configure(bg=self.terminal_option_base_bg)

    def _schedule_terminal_dropdown_hide(self):
        """إخفاء القائمة بعد مهلة قصيرة حتى يستطيع المستخدم الانتقال للخيارات."""
        self._cancel_terminal_dropdown_hide()
        if self.window and self.window.winfo_exists():
            self.terminal_hide_after_id = self.window.after(1200, self._hide_terminal_dropdown)

    def _cancel_terminal_dropdown_hide(self):
        """إلغاء إخفاء القائمة عند رجوع المؤشر إلى الزر أو القائمة."""
        if self.terminal_hide_after_id and self.window and self.window.winfo_exists():
            try:
                self.window.after_cancel(self.terminal_hide_after_id)
            except Exception:
                pass
        self.terminal_hide_after_id = None

    def _hide_terminal_dropdown(self):
        """إخفاء قائمة أنماط الطرفية."""
        self.terminal_hide_after_id = None
        if self.terminal_dropdown and self.terminal_dropdown.winfo_exists():
            self.terminal_dropdown.destroy()
        self.terminal_dropdown = None
        self.terminal_option_buttons = []

    def _select_terminal_mode(self, mode):
        """تغيير تنسيق الطرفية داخل الفورم."""
        self._hide_terminal_dropdown()
        self._set_terminal_mode(mode)

    def _set_terminal_mode(self, mode):
        """تطبيق تنسيق الطرفية المختار."""
        if not self.output_text:
            return

        hostname = socket.gethostname()
        user_home = os.path.expanduser("~")

        if mode == "kali":
            border = "#00ff00"
            bg = "#050505"
            fg = "#00ff00"
            content = self._build_terminal_intro("kali")
            status = "KALI TERMINAL STYLE"
        elif mode == "powershell":
            border = "#00a4ef"
            bg = "#012456"
            fg = "#f5f5f5"
            content = self._build_terminal_intro("powershell")
            status = "POWERSHELL STYLE"
        else:
            border = "#c0c0c0"
            bg = "#000000"
            fg = "#f5f5f5"
            content = self._build_terminal_intro("cmd")
            status = "CMD STYLE"

        self.active_terminal_mode = mode
        if self.terminal_frame:
            self.terminal_frame.configure(
                bg=border,
                highlightbackground=border,
                highlightcolor=border,
            )
        self.output_text.configure(bg=bg, fg=fg, insertbackground=fg)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, content)
        self.output_text.mark_set(tk.INSERT, "end-1c")
        self.terminal_input_start = self.output_text.index(tk.INSERT)
        self.output_text.focus_set()
        self.output_text.see(tk.INSERT)
        self.app._set_status(status)

    def _build_terminal_intro(self, mode):
        """بناء النص الافتتاحي لكل نوع طرفية."""
        hostname = socket.gethostname()
        user_home = os.path.expanduser("~")

        if mode == "kali":
            return f"┌──(kali㉿{hostname})-[~]\n└─$ "
        if mode == "powershell":
            return (
                "Windows PowerShell\n"
                "Copyright (C) Microsoft Corporation. All rights reserved.\n\n"
                "Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows\n\n"
                f"PS {user_home}> "
            )
        version = platform.version()
        return (
            f"Microsoft Windows [Version {version}]\n"
            "(c) Microsoft Corporation. All rights reserved.\n\n"
            f"{user_home}> "
        )

    def _build_terminal_prompt(self):
        """بناء سطر الأمر التالي حسب الطرفية الحالية."""
        hostname = socket.gethostname()
        user_home = os.path.expanduser("~")

        if self.active_terminal_mode == "kali":
            return f"\n┌──(kali㉿{hostname})-[~]\n└─$ "
        if self.active_terminal_mode == "powershell":
            return f"\nPS {user_home}> "
        return f"\n{user_home}> "

    def _handle_terminal_enter(self, _event):
        """تنفيذ الأمر المكتوب داخل الطرفية عند ضغط Enter."""
        if not self.output_text or self.terminal_is_running:
            return "break"

        if not self.active_terminal_mode:
            self._write_output("\n[INFO] اختر نوع الطرفية أولاً من زر Terminal الطرفية.\n")
            self.output_text.mark_set(tk.INSERT, "end-1c")
            self.terminal_input_start = self.output_text.index(tk.INSERT)
            return "break"

        command = self.output_text.get(self.terminal_input_start, "end-1c").strip()
        self.output_text.insert(tk.END, "\n")

        if not command:
            self._append_terminal_prompt()
            return "break"

        self.terminal_is_running = True
        self.output_text.configure(cursor="watch")
        threading.Thread(target=self._execute_terminal_command, args=(command,), daemon=True).start()
        return "break"

    def _execute_terminal_command(self, command):
        """تنفيذ الأمر حسب نوع الطرفية المختار."""
        if self.active_terminal_mode == "kali":
            output = TerminalExecutor.execute_kali_command(command)
        elif self.active_terminal_mode == "powershell":
            output = TerminalExecutor.execute_powershell_command(command)
        else:
            output = TerminalExecutor.execute_cmd_command(command)

        if self.window and self.window.winfo_exists():
            self.window.after(0, lambda: self._finish_terminal_command(output))

    def _finish_terminal_command(self, output):
        """عرض ناتج التنفيذ وتجهيز السطر التالي."""
        if output:
            self.output_text.insert(tk.END, output)
            if not output.endswith("\n"):
                self.output_text.insert(tk.END, "\n")
        self.terminal_is_running = False
        self.output_text.configure(cursor="xterm")
        self._append_terminal_prompt()
        self.app._set_status("TERMINAL READY")

    def _append_terminal_prompt(self):
        """إضافة prompt جديد ووضع المؤشر بعده."""
        prompt = self._build_terminal_prompt()
        self.output_text.insert(tk.END, prompt)
        self.output_text.mark_set(tk.INSERT, "end-1c")
        self.terminal_input_start = self.output_text.index(tk.INSERT)
        self.output_text.focus_set()
        self.output_text.see(tk.INSERT)

    def _keep_terminal_cursor_editable(self, _event):
        """إرجاع المؤشر لمنطقة الإدخال عند النقر داخل الطرفية."""
        if self.output_text:
            self.output_text.after(1, lambda: self.output_text.mark_set(tk.INSERT, tk.END))

    def _keep_terminal_input_area(self, event):
        """منع الكتابة فوق المخرجات السابقة قدر الإمكان."""
        if not self.output_text or event.keysym in ("Left", "Right", "Up", "Down", "Home", "End"):
            return None
        try:
            if self.output_text.compare(tk.INSERT, "<", self.terminal_input_start):
                self.output_text.mark_set(tk.INSERT, tk.END)
        except Exception:
            pass
        return None

    def _close(self):
        self._hide_terminal_dropdown()
        if self.window:
            self.window.destroy()
            self.window = None


if __name__ == "__main__":
    print("=" * 60)
    print("Hacking Tools Module - Ethical Testing Only")
    print("=" * 60)
    
    tools = HackingTools()
    
    print("\n[1] Port Scan Example:")
    result = tools.port_scan("127.0.0.1", "80,443,8080")
    print(f"Open ports: {result['open_ports']}")
    
    print("\n[2] DNS Lookup Example:")
    result = tools.dns_lookup("google.com", "A")
    print(f"Records: {result['records']}")
    
    print("\n[3] Password Generation:")
    result = tools.generate_password(16)
    print(f"Password: {result['password']}")
    print(f"Strength: {result['strength']}")
    
    print("\n[4] Hash Example:")
    result = tools.hash_string("Hello World", "sha256")
    print(f"Hash: {result['hash']}")
    
    print("\n" + "=" * 60)
    print("All tools are for educational and authorized testing only!")
    print("=" * 60)
