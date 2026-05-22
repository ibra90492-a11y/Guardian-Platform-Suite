"""ProtectionControlsWindow UI mixin."""

import tkinter as tk

from .theme import BG, GREEN, MUTED, PANEL_BG, RED


class ProtectionControlsWindowMixin:
    def _show_protection_controls_modal(self):
        if self._protection_modal_window:
            self._protection_modal_window.lift()
            return

        modal = tk.Toplevel(self.root)
        modal.title("Protection Controls")
        modal.geometry("950x700")
        modal.configure(bg=BG)
        modal.transient(self.root)
        self._protection_modal_window = modal

        tk.Label(
            modal,
            text="🛡️ Protection Controls",
            fg=GREEN,
            bg=BG,
            font=("Consolas", 18, "bold"),
        ).pack(pady=15)

        btn_frame = tk.Frame(modal, bg=BG)
        btn_frame.pack(pady=10)

        buttons = [
            ("🛑 Disable Protection", self.deactivate_prevent_tracking, "#3f3f3f"),
            ("🔄 Refresh Now", self.refresh_now, "#1d4ed8"),
            ("🔍 Diagnostics", self.run_diagnostics_report, "#0f766e"),
            ("📄 Export Report", self.export_security_report, "#7c2d12"),
            ("🔧 Force Baseline DNS", self.force_baseline_dns, "#334155"),
        ]

        for text, cmd, bg_color in buttons:
            tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg=bg_color,
                fg="white",
                font=("Tahoma", 11, "bold"),
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=15,
                pady=8,
            ).pack(side=tk.LEFT, padx=5)

        info_frame = tk.Frame(modal, bg=PANEL_BG, highlightthickness=1, highlightbackground=RED)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        modal_contact_lbl = tk.Label(
            info_frame,
            text="🔐 Contact: NOT SECURE",
            fg=RED,
            bg=PANEL_BG,
            font=("Consolas", 12, "bold"),
        )
        modal_contact_lbl.pack(fill=tk.X, padx=10, pady=10)

        fields = [
            ("📡 SSID", "ssid"), ("🌐 IP Address", "ip_address"),
            ("🔒 DNS (DoH)", "dns_doh"), ("🔐 DNS (DoT)", "dns_dot"),
            ("🗺️ State", "state"), ("🏢 CF Data Center", "cf_dc"),
            ("🏛️ AS Name", "as_name"), ("🔢 AS Number", "as_number"),
        ]

        self._protection_modal_info_vars = {}

        for title, key in fields:
            frame = tk.Frame(info_frame, bg=PANEL_BG)
            frame.pack(fill=tk.X, pady=3, padx=10)

            tk.Label(
                frame,
                text=f"{title}:",
                fg=MUTED,
                bg=PANEL_BG,
                font=("Consolas", 10, "bold"),
                width=18,
                anchor="w",
            ).pack(side=tk.LEFT)

            var = tk.StringVar(value=self.info_vars.get(key, tk.StringVar()).get())
            self._protection_modal_info_vars[key] = var
            tk.Label(
                frame,
                textvariable=var,
                fg=RED,
                bg=PANEL_BG,
                font=("Consolas", 10),
                anchor="w",
            ).pack(side=tk.LEFT, padx=5)

        def update_modal_colors():
            modal_contact_lbl.configure(fg=self.info_color)
            info_frame.configure(highlightbackground=self.info_color)

        update_modal_colors()

        def on_close():
            self._protection_modal_window = None
            modal.destroy()

        modal.protocol("WM_DELETE_WINDOW", on_close)

