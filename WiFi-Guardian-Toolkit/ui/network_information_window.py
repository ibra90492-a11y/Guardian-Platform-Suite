"""NetworkInformationWindow UI mixin."""

import platform
import socket
import subprocess
import threading
import tkinter as tk
from tkinter import ttk

from .theme import CYAN, GREEN


class NetworkInformationWindowMixin:
    def open_network_information_page(self):
        if self._network_page_window:
            self._network_page_window.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("Network Information")
        win.geometry("1000x600")
        win.configure(bg="#050505")
        win.transient(self.root)
        self._network_page_window = win

        tk.Label(
            win,
            text="🌐 Network Information",
            fg=GREEN,
            bg="#050505",
            font=("Consolas", 18, "bold"),
        ).pack(pady=10)

        ctrl_frame = tk.Frame(win, bg="#050505")
        ctrl_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            ctrl_frame,
            text="🔄 Refresh Scan",
            command=self._refresh_network_scan,
            bg="#0b3b2e",
            fg=GREEN,
            font=("Tahoma", 11),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            ctrl_frame,
            text="📋 Copy Results",
            command=self._copy_network_table,
            bg="#1e3a1f",
            fg=GREEN,
            font=("Tahoma", 11),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
        ).pack(side=tk.LEFT, padx=5)

        self._network_page_status_var = tk.StringVar(value="Ready - Click Refresh to scan")
        tk.Label(
            ctrl_frame,
            textvariable=self._network_page_status_var,
            fg=CYAN,
            bg="#050505",
            font=("Consolas", 10),
        ).pack(side=tk.LEFT, padx=20)

        columns = ("ip", "mac", "vendor", "hostname", "os", "device_type")
        self._network_page_table = ttk.Treeview(win, columns=columns, show="headings", height=15)

        headings = [
            ("ip", "IP", 140),
            ("mac", "MAC Address", 170),
            ("vendor", "Vendor", 180),
            ("hostname", "Hostname", 150),
            ("os", "OS", 130),
            ("device_type", "Device Type", 150),
        ]
        for column_id, label, width in headings:
            self._network_page_table.heading(column_id, text=label)
            self._network_page_table.column(column_id, width=width, anchor="w")

        self._network_page_table.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        scrollbar = ttk.Scrollbar(win, orient="vertical", command=self._network_page_table.yview)
        self._network_page_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self._network_page_copy_status = tk.Label(win, text="", fg=GREEN, bg="#050505")
        self._network_page_copy_status.pack(pady=5)

        def on_close():
            self._network_page_window = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


    def _refresh_network_scan(self):
        if self._network_page_table is None:
            return

        self._network_page_status_var.set("Scanning network...")
        for item in self._network_page_table.get_children():
            self._network_page_table.delete(item)

        def worker():
            devices = self._collect_network_devices()
            self.root.after(0, lambda: self._update_network_table(devices))

        threading.Thread(target=worker, daemon=True).start()


    def _update_network_table(self, devices):
        for dev in devices:
            self._network_page_table.insert(
                "",
                tk.END,
                values=(
                    dev.get("ip", "-"),
                    dev.get("mac", "-"),
                    dev.get("vendor", "-"),
                    dev.get("hostname", "-"),
                    dev.get("os", "-"),
                    dev.get("device_type", "-"),
                ),
            )
        self._network_page_status_var.set(f"Found {len(devices)} device(s)")


    def _collect_network_devices(self):
        devices = []
        try:
            out = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10)
            for line in out.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("Interface") or line.startswith("---"):
                    continue
                parts = line.split()
                if len(parts) >= 3 and "." in parts[0]:
                    ip = parts[0]
                    mac = parts[1] if len(parts) > 1 else "-"
                    devices.append(
                        {
                            "ip": ip,
                            "mac": mac,
                            "vendor": self._get_vendor(mac),
                            "hostname": "-",
                            "os": "-",
                            "device_type": "Unknown",
                        }
                    )
        except Exception:
            pass

        local_ip = self._get_local_ip()
        if local_ip and local_ip != "127.0.0.1":
            devices.insert(
                0,
                {
                    "ip": local_ip,
                    "mac": "-",
                    "vendor": "Local Machine",
                    "hostname": socket.gethostname(),
                    "os": platform.system(),
                    "device_type": "Computer",
                },
            )

        return devices


    def _get_vendor(self, mac):
        mac_prefix = mac[:8].upper() if mac and len(mac) >= 8 else ""
        vendors = {
            "00:1A:1A": "Apple",
            "A4:77:D4": "Apple",
            "B8:F6:55": "Apple",
            "D4:61:01": "Samsung",
            "5C:F3:70": "Samsung",
            "00:50:F2": "Intel",
            "08:00:27": "Oracle",
        }
        return vendors.get(mac_prefix, "Unknown")


    def _copy_network_table(self):
        if self._network_page_table is None:
            return
        lines = []
        for item in self._network_page_table.get_children():
            values = self._network_page_table.item(item)["values"]
            lines.append("\t".join(str(value) for value in values))
        text = "\n".join(lines)
        self._copy_to_clipboard(text)
        self._network_page_copy_status.config(text="✓ Copied to clipboard")
        self.root.after(2000, lambda: self._network_page_copy_status.config(text=""))

