"""SettingsWindow UI mixin."""

import os
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox

from .theme import CYAN, GREEN, MUTED

SECURITY_FILE = "security_code.txt"
KALI_ACCOUNT_FILE = "kali_account.txt"


class SettingsWindowMixin:
    def open_settings(self):
        if self._settings_window:
            self._settings_window.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("500x450")
        win.configure(bg="#0d0d0d")
        win.transient(self.root)
        self._settings_window = win

        tk.Label(
            win,
            text="⚙️ Settings",
            fg=GREEN,
            bg="#0d0d0d",
            font=("Tahoma", 16, "bold"),
        ).pack(pady=15)

        buttons = [
            ("🔑 Show WiFi Password", self.show_wifi_password),
            ("🔐 Change Security Code", self.change_security_code),
            ("📦 Install Kali Requirements", self.install_requirements),
            ("👤 Create Kali Account", self.create_kali_account),
            ("🔄 Sync Kali Account", self.sync_kali_account),
        ]

        for text, cmd in buttons:
            tk.Button(
                win,
                text=text,
                command=cmd,
                bg="#2d2d2d",
                fg="white",
                font=("Tahoma", 12),
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=15,
                pady=8,
            ).pack(fill=tk.X, padx=30, pady=5)

        def on_close():
            self._settings_window = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


    def open_password_manager(self):
        if self._password_manager_window and self._password_manager_window.winfo_exists():
            self._password_manager_window.lift()
            self._password_manager_window.focus_force()
            return

        win = tk.Toplevel(self.root)
        win.title("إدارة كلمات المرور - Password Manager")
        win.geometry("550x500")
        win.configure(bg="#0d0d0d")
        win.transient(self.root)
        win.resizable(False, False)
        self._password_manager_window = win

        tk.Label(
            win,
            text="🔐 إدارة كلمات المرور",
            fg=GREEN,
            bg="#0d0d0d",
            font=("Tahoma", 18, "bold"),
        ).pack(pady=(20, 10))

        tk.Label(
            win,
            text="تغيير كلمة المرور إلى كلمة قوية",
            fg=CYAN,
            bg="#0d0d0d",
            font=("Tahoma", 12),
        ).pack(pady=(0, 20))

        input_frame = tk.Frame(win, bg="#0d0d0d")
        input_frame.pack(pady=10, padx=30, fill=tk.X)

        tk.Label(
            input_frame,
            text="📧 اسم المستخدم / البريد الإلكتروني:",
            fg=MUTED,
            bg="#0d0d0d",
            font=("Tahoma", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))
        self.username_entry = tk.Entry(
            input_frame,
            font=("Tahoma", 11),
            bg="#1a1a1a",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)

        tk.Label(
            input_frame,
            text="🔑 كلمة المرور القديمة:",
            fg=MUTED,
            bg="#0d0d0d",
            font=("Tahoma", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))
        self.old_password_entry = tk.Entry(
            input_frame,
            font=("Tahoma", 11),
            bg="#1a1a1a",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
            show="*",
        )
        self.old_password_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)

        tk.Label(
            input_frame,
            text="🛡️ كلمة المرور القوية الجديدة:",
            fg=MUTED,
            bg="#0d0d0d",
            font=("Tahoma", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))

        new_pass_frame = tk.Frame(input_frame, bg="#0d0d0d")
        new_pass_frame.pack(fill=tk.X, pady=(0, 15))

        self.new_password_var = tk.StringVar()
        self.new_password_entry = tk.Entry(
            new_pass_frame,
            font=("Consolas", 11),
            bg="#1a1a1a",
            fg="#20ff6b",
            insertbackground="white",
            relief=tk.FLAT,
            textvariable=self.new_password_var,
            width=30,
        )
        self.new_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

        tk.Button(
            new_pass_frame,
            text="📋 نسخ",
            command=self._copy_new_password,
            bg="#14532d",
            fg="white",
            font=("Tahoma", 9),
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
        ).pack(side=tk.RIGHT, padx=(5, 0))

        btn_frame = tk.Frame(win, bg="#0d0d0d")
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="🔐 تغيير كلمة المرور إلى قوية",
            command=self._generate_strong_password,
            bg="#0f766e",
            fg="white",
            font=("Tahoma", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="✅ موافق",
            command=self._confirm_password_change,
            bg="#1d4ed8",
            fg="white",
            font=("Tahoma", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
        ).pack(side=tk.LEFT, padx=5)

        recovery_frame = tk.LabelFrame(
            win,
            text="🔗 استعادة كلمة المرور",
            fg=CYAN,
            bg="#0d0d0d",
            font=("Tahoma", 11, "bold"),
        )
        recovery_frame.pack(fill=tk.X, padx=30, pady=(10, 20))

        snapchat_link = "https://accounts.snapchat.com/v2/login?continue=%2Faccounts%2Fchange_password"
        link_label = tk.Label(
            recovery_frame,
            text=snapchat_link,
            fg="#00d9ff",
            bg="#0d0d0d",
            font=("Consolas", 9),
            cursor="hand2",
            wraplength=450,
        )
        link_label.pack(pady=(10, 5))
        link_label.bind("<Button-1>", lambda _event: webbrowser.open(snapchat_link))

        tk.Button(
            recovery_frame,
            text="🌐 فتح الرابط في المتصفح",
            command=lambda: webbrowser.open(snapchat_link),
            bg="#334155",
            fg="white",
            font=("Tahoma", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
        ).pack(pady=(5, 10))

        self.pm_status_var = tk.StringVar(value="✅ جاهز")
        status_label = tk.Label(
            win,
            textvariable=self.pm_status_var,
            fg=GREEN,
            bg="#0d0d0d",
            font=("Tahoma", 10),
            anchor="w",
        )
        status_label.pack(fill=tk.X, padx=30, pady=(0, 15))

        def on_close():
            self._password_manager_window = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


    def show_wifi_password(self):
        ssid = self._get_ssid()
        if ssid and ssid not in ["Not connected", "Unsupported OS"]:
            messagebox.showinfo(
                "WiFi Password",
                f"SSID: {ssid}\n\nPassword cannot be retrieved without admin privileges.\nUse Windows: netsh wlan show profile name=\"{ssid}\" key=clear",
            )
        else:
            messagebox.showwarning("WiFi", "Not connected to any WiFi network")


    def change_security_code(self):
        current = self._input_dialog("Verify", "Enter current security code:", secret=True)
        if not current or current != self._get_security_code():
            messagebox.showerror("Error", "Invalid security code")
            return
        new1 = self._input_dialog("New Code", "Enter new security code:", secret=True)
        if not new1:
            return
        new2 = self._input_dialog("Confirm", "Confirm new security code:", secret=True)
        if new1 == new2:
            with open(SECURITY_FILE, "w", encoding="utf-8") as file_handle:
                file_handle.write(new1)
            messagebox.showinfo("Success", "Security code changed successfully")
            self._audit_event("security_code_changed", "INFO", "updated")
        else:
            messagebox.showerror("Error", "Codes do not match")


    def install_requirements(self):
        distro = self._get_wsl_distro()
        if not distro:
            messagebox.showerror("Error", "Kali Linux not found in WSL.\nRun: wsl --install -d kali-linux")
            return

        self._set_status("INSTALLING KALI TOOLS...")

        def worker():
            try:
                result = self._run_kali_command(
                    "apt update && apt install -y tmux nmap hydra john hashcat sqlmap nikto gobuster aircrack-ng",
                    require_root=True,
                )
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Installation",
                        "Requirements installation completed!" if result.returncode == 0 else "Installation had issues",
                    ),
                )
                self._set_status("READY")
            except Exception as error:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Installation failed: {error}"))

        threading.Thread(target=worker, daemon=True).start()


    def create_kali_account(self):
        win = tk.Toplevel(self.root)
        win.title("Create Kali Account")
        win.geometry("450x400")
        win.configure(bg="#0d0d0d")
        win.transient(self.root)

        tk.Label(
            win,
            text="👤 Create Kali Linux Account",
            fg=GREEN,
            bg="#0d0d0d",
            font=("Tahoma", 14, "bold"),
        ).pack(pady=15)

        entries = {}
        fields = [("Username:", "user"), ("Password:", "pass"), ("Confirm Password:", "confirm"), ("Full Name:", "full")]

        for label, key in fields:
            frame = tk.Frame(win, bg="#0d0d0d")
            frame.pack(pady=5, padx=20, fill=tk.X)
            tk.Label(frame, text=label, fg=MUTED, bg="#0d0d0d", width=15, anchor="w").pack(side=tk.LEFT)
            entry = tk.Entry(frame, show="*" if "pass" in key else "", font=("Tahoma", 11), width=25)
            entry.pack(side=tk.LEFT, padx=5)
            entries[key] = entry

        def save():
            if entries["pass"].get() != entries["confirm"].get():
                messagebox.showerror("Error", "Passwords do not match")
                return
            if not entries["user"].get():
                messagebox.showerror("Error", "Username required")
                return
            with open(KALI_ACCOUNT_FILE, "w", encoding="utf-8") as file_handle:
                file_handle.write(f"{entries['user'].get()}|{entries['pass'].get()}|{entries['full'].get()}")
            messagebox.showinfo("Success", "Kali account saved!\nSync with WSL using Settings button.")
            win.destroy()

        tk.Button(
            win,
            text="💾 Save Account",
            command=save,
            bg=GREEN,
            fg="black",
            font=("Tahoma", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
        ).pack(pady=20)


    def sync_kali_account(self):
        if not os.path.exists(KALI_ACCOUNT_FILE):
            messagebox.showinfo("Info", "No saved Kali account. Create one first.")
            return

        with open(KALI_ACCOUNT_FILE, "r", encoding="utf-8") as file_handle:
            parts = file_handle.read().strip().split("|")
        if len(parts) < 3:
            messagebox.showerror("Error", "Invalid account file")
            return

        username, password, fullname = parts[0], parts[1], parts[2]
        self._set_status("SYNCING KALI ACCOUNT...")

        def worker():
            try:
                self._sync_kali_account_to_wsl(username, password, fullname)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Account '{username}' synced with WSL"))
                self._set_status("READY")
            except Exception as error:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Sync failed: {error}"))

        threading.Thread(target=worker, daemon=True).start()


    def _generate_strong_password(self):
        import secrets
        import string

        length = 16
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(characters) for _ in range(length))

        self.new_password_var.set(password)
        self.pm_status_var.set("🔐 تم توليد كلمة مرور قوية جديدة - انسخها الآن")

        self.root.clipboard_clear()
        self.root.clipboard_append(password)

        self.new_password_entry.configure(fg="#20ff6b")
        self.root.after(2000, lambda: self.new_password_entry.configure(fg="#20ff6b"))


    def _copy_new_password(self):
        password = self.new_password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.pm_status_var.set("📋 تم نسخ كلمة المرور إلى الحافظة")
            self.root.after(2000, lambda: self.pm_status_var.set("✅ جاهز"))


    def _confirm_password_change(self):
        username = self.username_entry.get().strip()
        old_password = self.old_password_entry.get()
        new_password = self.new_password_var.get()

        if not username:
            self.pm_status_var.set("⚠️ الرجاء إدخال اسم المستخدم أو البريد الإلكتروني")
            return

        if not old_password:
            self.pm_status_var.set("⚠️ الرجاء إدخال كلمة المرور القديمة")
            return

        if not new_password:
            self.pm_status_var.set("⚠️ الرجاء الضغط على 'تغيير كلمة المرور إلى قوية' أولاً")
            return

        message = f"""✅ تم تجهيز كلمة المرور القوية!

📝 البيانات المدخلة:
━━━━━━━━━━━━━━━━━━━━━━
👤 اسم المستخدم: {username}
🔑 كلمة المرور القديمة: {'*' * len(old_password)}
🛡️ كلمة المرور الجديدة: {new_password}
━━━━━━━━━━━━━━━━━━━━━━

📌 الخطوات التالية:
1. تم نسخ كلمة المرور الجديدة تلقائياً
2. اذهب إلى رابط استعادة كلمة المرور في سناب شات
3. قم بتسجيل الدخول باستخدام اسم المستخدم وكلمة المرور القديمة
4. اختر "تغيير كلمة المرور"
5. الصق كلمة المرور الجديدة (Ctrl+V)

⚠️ ملاحظة: هذا البرنامج لا يمكنه تغيير كلمة المرور مباشرة في سناب شات.
يجب عليك القيام بذلك يدوياً من خلال الرابط الموجود في النموذج.

هل تريد فتح رابط سناب شات الآن؟"""

        if messagebox.askyesno("تأكيد تغيير كلمة المرور", message):
            webbrowser.open("https://accounts.snapchat.com/v2/login?continue=%2Faccounts%2Fchange_password")
            self.pm_status_var.set("🌐 تم فتح رابط سناب شات - قم بتسجيل الدخول وتغيير كلمة المرور")

