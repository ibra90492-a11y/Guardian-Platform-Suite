"""KaliCommandsWindow UI mixin."""

import tkinter as tk

from .theme import CYAN, GREEN


class KaliCommandsWindowMixin:
    def open_kali_linux_command_form(self):
        if self._kali_command_window:
            self._kali_command_window.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("Kali Linux Command Form")
        win.geometry("750x650")
        win.configure(bg="#0b0b0b")
        win.transient(self.root)
        self._kali_command_window = win

        tk.Label(
            win,
            text="💻 Kali Linux Command Form",
            fg=GREEN,
            bg="#0b0b0b",
            font=("Consolas", 16, "bold"),
        ).pack(pady=10)

        tk.Label(
            win,
            text="📡 Network Scan Commands:",
            fg="#facc15",
            bg="#0b0b0b",
            font=("Tahoma", 11, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        text_frame = tk.Frame(win, bg="#050505", highlightthickness=2, highlightbackground=GREEN)
        text_frame.pack(fill=tk.X, padx=15, pady=5)

        self._network_scan_update_text = tk.Text(
            text_frame,
            height=6,
            bg="#050505",
            fg="#d1fae5",
            font=("Consolas", 10),
            wrap="none",
            relief=tk.FLAT,
        )
        self._network_scan_update_text.pack(fill=tk.X, padx=5, pady=5)
        self._network_scan_update_text.insert("1.0", "nmap -sn 192.168.1.0/24\narp -a")

        btn_frame = tk.Frame(win, bg="#0b0b0b")
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="📋 Copy Commands",
            command=self._copy_network_commands,
            bg="#14532d",
            fg="white",
            font=("Tahoma", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🚀 Send to Terminal",
            command=self._send_network_commands,
            bg="#0f766e",
            fg="white",
            font=("Tahoma", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
        ).pack(side=tk.LEFT, padx=5)

        pass_frame = tk.LabelFrame(
            win,
            text="🔓 Password Cracking Tools",
            fg=GREEN,
            bg="#050505",
            font=("Tahoma", 12, "bold"),
        )
        pass_frame.pack(fill=tk.X, padx=15, pady=15)

        pass_tools = [
            ("John the Ripper", "john --help"),
            ("Hashcat (GPU)", "hashcat --help"),
            ("Hydra (Online)", "hydra -h"),
            ("Crunch (Wordlist)", "crunch --help"),
            ("Medusa", "medusa -h"),
            ("Ncrack", "ncrack --help"),
        ]

        for name, cmd in pass_tools:
            tool_frame = tk.Frame(pass_frame, bg="#050505", highlightthickness=1, highlightbackground=GREEN)
            tool_frame.pack(fill=tk.X, pady=3, padx=5)

            tk.Label(
                tool_frame,
                text=f"{name}:",
                fg=CYAN,
                bg="#050505",
                font=("Tahoma", 10, "bold"),
                width=18,
                anchor="w",
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                tool_frame,
                text=cmd,
                fg="#d1fae5",
                bg="#050505",
                font=("Consolas", 9),
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                tool_frame,
                text="نسخ",
                command=lambda command=cmd: self._copy_to_clipboard(command),
                bg="#14532d",
                fg="white",
                font=("Tahoma", 9),
                relief=tk.FLAT,
                cursor="hand2",
                padx=8,
            ).pack(side=tk.RIGHT, padx=2)

            tk.Button(
                tool_frame,
                text="إرسال",
                command=lambda command=cmd: self._send_to_terminal(command),
                bg="#0f766e",
                fg="white",
                font=("Tahoma", 9),
                relief=tk.FLAT,
                cursor="hand2",
                padx=8,
            ).pack(side=tk.RIGHT, padx=2)

        self._kali_command_copy_status = tk.Label(win, text="", fg=GREEN, bg="#0b0b0b")
        self._kali_command_copy_status.pack(pady=10)

        def on_close():
            self._kali_command_window = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


    def _copy_network_commands(self):
        text = self._network_scan_update_text.get("1.0", tk.END).strip()
        self._copy_to_clipboard(text)


    def _send_network_commands(self):
        text = self._network_scan_update_text.get("1.0", tk.END).strip()
        self._send_to_terminal(text)

