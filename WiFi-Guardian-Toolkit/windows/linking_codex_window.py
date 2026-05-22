# -*- coding: utf-8 -*-
"""نافذة Linking Codex and Terminal - الواجهة الرئيسية للتفاعل مع Codex والطرفيات"""

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import threading
import time
import os
import subprocess
import re

from utils.constants import BG, CODEX_SHORTCUT
from utils.command_extractor import extract_terminal_command, is_python_script
from utils.script_generator import generate_codex_script
from core.terminal_executor import TerminalExecutor


class LinkingCodexWindow:
    """نافذة الربط بين Codex والطرفيات"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.window = None
        
        self._codex_followup_text = None
        self._ai_chat_text = None
        self._target_system_var = None
        self._codex_shortcut_opened = False
        
        self._last_terminal_response = ""
        self._last_terminal_transcript = ""
        self._last_terminal_system = ""
        
    def open(self):
        """فتح النافذة"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Linking Codex and Terminal")
        screen_height = self.parent.winfo_screenheight()
        window_height = min(740, max(620, screen_height - 90))
        self.window.geometry(f"680x{window_height}")
        self.window.minsize(600, 620)
        self.window.configure(bg=BG)
        self.window.transient(self.parent)
        
        self._build_ui()
        self._open_codex_shortcut()
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _build_ui(self):
        """بناء واجهة المستخدم"""
        container = tk.Frame(self.window, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)
        
        # العنوان
        tk.Label(container, text="Linking Codex and Terminal",
                fg="#dbeafe", bg=BG, font=("Arial", 18, "bold"),
                anchor="center").pack(fill=tk.X, pady=(0, 8))
        
        # حقل الكتابة
        tk.Label(container, text="Write your request in Arabic or English:",
                fg="#00ffff", bg=BG, font=("Arial", 11, "bold"),
                anchor="w").pack(fill=tk.X, pady=(0, 5))
        
        self._codex_followup_text = scrolledtext.ScrolledText(
            container, bg="#171717", fg="#f8fafc",
            font=("Arial", 12), height=4, wrap=tk.WORD,
            relief=tk.FLAT, insertbackground="#f8fafc"
        )
        self._codex_followup_text.pack(fill=tk.X, pady=(0, 6))
        
        # زر الإرسال إلى Codex
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(fill=tk.X, pady=(2, 6))
        
        tk.Button(btn_frame, text="Send to Codex",
                 command=self._send_to_codex,
                 bg="#0f766e", fg="white",
                 font=("Arial", 10, "bold"), relief=tk.FLAT,
                 cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        
        # حقل رد Codex
        tk.Label(container, text="Codex Response:",
                fg="#ffaa00", bg=BG, font=("Arial", 11, "bold"),
                anchor="w").pack(fill=tk.X, pady=(0, 5))
        
        self._ai_chat_text = scrolledtext.ScrolledText(
            container, bg="#111827", fg="#facc15",
            font=("Arial", 12), height=7, wrap=tk.WORD,
            relief=tk.FLAT, insertbackground="#facc15"
        )
        self._ai_chat_text.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        self._ai_chat_text.insert(tk.END, "Codex response will appear here.\n")
        
        # اختيار النظام
        system_frame = tk.Frame(container, bg=BG)
        system_frame.pack(fill=tk.X, pady=(2, 6))
        
        tk.Label(system_frame, text="Select System:",
                fg="#00ff00", bg=BG, font=("Arial", 10, "bold"),
                anchor="w").pack(side=tk.LEFT, padx=(0, 10))
        
        self._target_system_var = tk.StringVar(value="kali-linux windows")
        for system in ["kali-linux windows", "PowerShell", "CMD"]:
            tk.Radiobutton(system_frame, text=system,
                          variable=self._target_system_var, value=system,
                          bg=BG, fg="#00ff00", selectcolor=BG,
                          font=("Arial", 10)).pack(side=tk.LEFT, padx=8)
        
        # أزرار التحكم
        controls_frame = tk.Frame(container, bg=BG)
        controls_frame.pack(fill=tk.X, pady=(2, 5))
        
        tk.Button(controls_frame, text="Send to Terminal",
                 command=self._send_to_terminal,
                 bg="#14532d", fg="white",
                 font=("Arial", 10, "bold"), relief=tk.FLAT,
                 cursor="hand2", padx=15, pady=8).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(controls_frame, text="Copy Terminal Response",
                 command=self._copy_response,
                 bg="#1d4ed8", fg="white",
                 font=("Arial", 10, "bold"), relief=tk.FLAT,
                 cursor="hand2", padx=15, pady=8).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(controls_frame, text="Clear All",
                 command=self._clear_all,
                 bg="#991b1b", fg="white",
                 font=("Arial", 10, "bold"), relief=tk.FLAT,
                 cursor="hand2", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
    
    def _send_to_codex(self):
        """إرسال الطلب إلى Codex"""
        user_request = self._get_request_text().strip()
        system = self._target_system_var.get()
        
        if not user_request:
            self._add_message("Please write a request first.", is_error=True)
            return
        
        script = generate_codex_script(user_request, system)
        self._open_codex_shortcut()
        
        # نسخ إلى الحافظة
        self.window.clipboard_clear()
        self.window.clipboard_append(script)
        
        self._add_message(f"Script generated and copied to clipboard.", is_success=True)
        self.app._set_status("SCRIPT SENT TO CODEX")
    
    def _send_to_terminal(self):
        """إرسال الأمر إلى الطرفية"""
        system = self._target_system_var.get()
        codex_response = self._get_codex_response()
        terminal_command = extract_terminal_command(codex_response)
        
        if not system:
            self._add_message("Select a system first.", is_error=True)
            return
        
        if not terminal_command:
            self._add_message("No valid command found in Codex response.", is_error=True)
            return
        
        if is_python_script(terminal_command):
            self._add_message("Response contains a Python script. Saving as file...", is_warning=True)
            return
        
        user_request = self._get_request_text() or "Command from Codex"
        
        def execute():
            if system == "kali-linux windows":
                output = TerminalExecutor.execute_kali_command(terminal_command)
            elif system == "PowerShell":
                output = TerminalExecutor.execute_powershell_command(terminal_command)
            else:
                output = TerminalExecutor.execute_cmd_command(terminal_command)
            
            transcript = self._build_transcript(system, user_request, terminal_command, output)
            self._last_terminal_response = output
            self._last_terminal_transcript = transcript
            self._last_terminal_system = system
            self.app._last_terminal_system = system
            
            # حفظ في history
            if system not in self.app._terminal_sessions_history:
                self.app._terminal_sessions_history[system] = []
            self.app._terminal_sessions_history[system].append(transcript)
            
            if self.window and self.window.winfo_exists():
                self.window.after(0, lambda: self._add_message(f"Output:\n{output[:1000]}", is_response=True))
                self.window.after(0, lambda: self.app._set_status("READY - TERMINAL RESPONSE SAVED"))
        
        threading.Thread(target=execute, daemon=True).start()
    
    def _copy_response(self):
        """نسخ رد الطرفية"""
        if self._last_terminal_transcript:
            self.window.clipboard_clear()
            self.window.clipboard_append(self._last_terminal_transcript)
            self._add_message("Terminal response copied to clipboard.", is_success=True)
        else:
            self._add_message("No terminal response to copy.", is_error=True)
    
    def _clear_all(self):
        """مسح جميع الحقول"""
        if self._codex_followup_text:
            self._codex_followup_text.delete("1.0", tk.END)
        if self._ai_chat_text:
            self._ai_chat_text.config(state=tk.NORMAL)
            self._ai_chat_text.delete(1.0, tk.END)
            self._ai_chat_text.insert(tk.END, "Codex response will appear here.\n")
            self._ai_chat_text.config(state=tk.NORMAL)
        self._add_message("All fields cleared.", is_success=True)
    
    def _open_codex_shortcut(self):
        """فتح اختصار Codex"""
        if self._codex_shortcut_opened:
            return
        
        if os.path.exists(CODEX_SHORTCUT):
            subprocess.Popen(["cmd", "/c", "start", "", CODEX_SHORTCUT], shell=False)
            self._codex_shortcut_opened = True
    
    def _get_request_text(self):
        if self._codex_followup_text:
            return self._codex_followup_text.get("1.0", tk.END).strip()
        return ""
    
    def _get_codex_response(self):
        if self._ai_chat_text:
            return self._ai_chat_text.get("1.0", tk.END).strip()
        return ""
    
    def _build_transcript(self, system, user_request, command, output):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f"""[{timestamp}] {system}
User request:
{user_request}

Terminal command:
{command}

Terminal response:
{output[:3000]}"""
    
    def _add_message(self, message, is_error=False, is_success=False, is_response=False, is_warning=False):
        """إضافة رسالة إلى نافذة الدردشة"""
        if not self._ai_chat_text:
            return
        
        self._ai_chat_text.config(state=tk.NORMAL)
        
        if is_error:
            formatted = f"\n[ERROR] {message}\n"
            tag = "error"
            self._ai_chat_text.tag_config(tag, foreground="#ff4444")
        elif is_success:
            formatted = f"\n[OK] {message}\n"
            tag = "success"
            self._ai_chat_text.tag_config(tag, foreground="#44ff44")
        elif is_warning:
            formatted = f"\n[WARNING] {message}\n"
            tag = "warning"
            self._ai_chat_text.tag_config(tag, foreground="#ffaa00")
        elif is_response:
            formatted = f"{message}\n"
            tag = "response"
            self._ai_chat_text.tag_config(tag, foreground="#00ff00")
        else:
            formatted = f"{message}\n"
            tag = None
        
        if tag:
            self._ai_chat_text.insert(tk.END, formatted, tag)
        else:
            self._ai_chat_text.insert(tk.END, formatted)
        
        self._ai_chat_text.see(tk.END)
        self._ai_chat_text.config(state=tk.NORMAL)
    
    def _close(self):
        """إغلاق النافذة"""
        if self.window:
            self.window.destroy()
            self.window = None
