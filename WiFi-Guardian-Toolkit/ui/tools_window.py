"""ToolsWindow UI mixin."""

import tkinter as tk

from .theme import CYAN, GREEN


class ToolsWindowMixin:
    def open_tools_panel(self):
        if self._tools_panel_window and self._tools_panel_window.winfo_exists():
            self._tools_panel_window.lift()
            self._tools_panel_window.focus_force()
            return

        win = tk.Toplevel(self.root)
        win.title("Kali Tools - أدوات كالي لينكس المتقدمة")
        win.geometry("860x620")
        win.minsize(860, 620)
        win.configure(bg="#070707")
        win.transient(self.root)
        self._tools_panel_window = win

        tk.Label(
            win,
            text="Kali Linux Advanced Tools",
            fg=GREEN,
            bg="#070707",
            font=("Tahoma", 18, "bold"),
            anchor="center",
        ).pack(fill=tk.X, pady=(14, 4))
        tk.Label(
            win,
            text="أدوات اختبار الاختراق - كسر كلمات المرور - فحص الشبكات",
            fg=CYAN,
            bg="#070707",
            font=("Tahoma", 13),
            anchor="center",
        ).pack(fill=tk.X, pady=(0, 10))

        canvas = tk.Canvas(win, bg="#070707", highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#070707")

        scrollable_frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        sections = [
            (
                "🔓 Password Cracking Tools | أدوات كسر كلمات المرور",
                "#ff6b6b",
                [
                    ("جون ذا ريبر - John the Ripper", "john --help"),
                    ("هاش كات - Hashcat (GPU)", "hashcat --help"),
                    ("هايدرا - Hydra (Online)", "hydra -h"),
                    ("كرانش - Crunch (Wordlist)", "crunch --help"),
                    ("ميدوسا - Medusa (Parallel)", "medusa -h"),
                    ("إنكراك - Ncrack (Auth)", "ncrack --help"),
                    ("سيلويل - CeWL (Custom Wordlist)", "cewl --help"),
                    ("قوس قزح - RainbowCrack", "rcrack --help"),
                    ("أوف كراك - Ophcrack", "ophcrack --help"),
                    ("سام دامب - Samdump2", "samdump2 --help"),
                    ("فايند ماي هاش - FindMyHash", "findmyhash --help"),
                ],
            ),
            (
                "🌐 Network Scanning Tools | أدوات فحص الشبكات",
                CYAN,
                [
                    ("إن ماب - Nmap (Port Scan)", "nmap -h"),
                    ("ماس سكان - Masscan (Fast Scan)", "masscan --help"),
                    ("نت كات - Netcat (Network Tool)", "nc -h"),
                    ("زين ماب - Zenmap (GUI)", "zenmap --help"),
                    ("زي ماب - Zmap (Internet Scan)", "zmap --help"),
                    ("راست سكان - RustScan (Fast)", "rustscan --help"),
                    ("يونيكورن سكان - Unicornscan", "unicornscan --help"),
                    ("إن بينج - Nping (Ping)", "nping --help"),
                    ("أنجري أي بي سكانر - Angry IP Scanner", "ipscan --help"),
                    ("إف بينج - Fping", "fping --help"),
                    ("إتش بينج - Hping3", "hping3 --help"),
                    ("آرب سكان - Arp-scan", "arp-scan --help"),
                ],
            ),
            (
                "💉 Web Application Testing | اختبار تطبيقات الويب",
                "#ffcc00",
                [
                    ("إس كيو إل ماب - SQLmap (SQL Injection)", "sqlmap --help"),
                    ("نيكتو - Nikto (Web Server)", "nikto -H"),
                    ("جو باستير - Gobuster (Dir Bust)", "gobuster --help"),
                    ("وات ويب - Whatweb (Fingerprint)", "whatweb --help"),
                    ("دبليو بي سكان - WPScan (WordPress)", "wpscan --help"),
                    ("دير بي - Dirb (Directory)", "dirb --help"),
                    ("دبليو فاز - Wfuzz (Fuzzing)", "wfuzz --help"),
                    ("إكس إس إس سترايك - XSStrike (XSS)", "xsstrike --help"),
                    ("إس إس إل سكان - SSLScan (SSL/TLS)", "sslscan --help"),
                    ("سكيب فيش - Skipfish (Scan)", "skipfish --help"),
                    ("أراكني - Arachni (Scanner)", "arachni --help"),
                    ("أوبن فاس - OpenVAS", "openvas --help"),
                ],
            ),
            (
                "📶 Wireless & RF Tools | أدوات الشبكات اللاسلكية",
                "#a78bfa",
                [
                    ("آير كراك - Aircrack-ng Suite", "aircrack-ng --help"),
                    ("واي فايت - Wifite (Auto Attack)", "wifite --help"),
                    ("ريفير - Reaver (WPS)", "reaver --help"),
                    ("ماك تشانجر - MAC Changer", "macchanger --help"),
                    ("كيزميت - Kismet (Detector)", "kismet --help"),
                    ("واش - Wash (WPS Scan)", "wash --help"),
                    ("كاوباتي - Cowpatty (WPA)", "cowpatty --help"),
                    ("بايرت - Pyrit (WPA2)", "pyrit --help"),
                    ("واي فاي فيشر - Wifiphisher", "wifiphisher --help"),
                    ("بيتر كاب - Bettercap", "bettercap --help"),
                    ("إم دي كي 3 - MDK3", "mdk3 --help"),
                    ("فيرن - Fern Wifi Cracker", "fern-wifi-cracker --help"),
                ],
            ),
            (
                "🔍 Forensics Tools | أدوات التحليل الجنائي",
                "#20ff6b",
                [
                    ("فولاتيليتي - Volatility (Memory)", "vol --help"),
                    ("بين ووك - Binwalk (Analysis)", "binwalk --help"),
                    ("فورموست - Foremost (Recovery)", "foremost -h"),
                    ("أوتوبسي - Autopsy (GUI)", "autopsy --help"),
                    ("سلوث كيت - Sleuth Kit", "tsk_loaddb --help"),
                    ("سكالبيل - Scalpel (Recovery)", "scalpel --help"),
                    ("فوتوريك - Photorec", "photorec --help"),
                    ("جيمايجر - Guymager (Imaging)", "guymager --help"),
                    ("دي دي ريسكيو - Ddrescue", "ddrescue --help"),
                    ("إكزيف تول - Exiftool (Metadata)", "exiftool --help"),
                ],
            ),
            (
                "💀 Exploitation Tools | أدوات الاستغلال",
                "#ff4444",
                [
                    ("ميتاسبلويت - Metasploit Framework", "msfconsole -h"),
                    ("سيرش إكسبلويت - Searchsploit", "searchsploit --help"),
                    ("بي إي إي إف - BeEF Framework", "beef-xss --help"),
                    ("سوشال إنجينير تول كيت - SET", "setoolkit --help"),
                    ("آرميتاج - Armitage", "armitage --help"),
                    ("فاستك - Veil Evasion", "veil --help"),
                    ("شيل نو - Shellnoob", "shellnoob --help"),
                    ("باتنيت - Patator", "patator --help"),
                ],
            ),
            (
                "🔄 Reverse Engineering | أدوات الهندسة العكسية",
                "#ff9f43",
                [
                    ("جي دي بي - GDB (Debugger)", "gdb --help"),
                    ("راداري - Radare2", "r2 --help"),
                    ("غيدرا - Ghidra", "ghidra --help"),
                    ("أولاي ديباجر - OllyDbg", "ollydbg --help"),
                    ("إكس64 ديباجر - x64dbg", "x64dbg --help"),
                    ("إي بي كيه تول - APKTool", "apktool --help"),
                    ("ديكس تو جار - Dex2jar", "d2j-dex2jar --help"),
                    ("جادكس - Jadx", "jadx --help"),
                ],
            ),
        ]

        for title, color, tools in sections:
            section = tk.LabelFrame(
                scrollable_frame,
                text=title,
                fg=color,
                bg="#0a0a0a",
                font=("Tahoma", 12, "bold"),
                labelanchor="n",
                padx=10,
                pady=5,
            )
            section.pack(fill=tk.X, padx=10, pady=8)

            for name, cmd in tools:
                frame = tk.Frame(section, bg="#0d0d0d", highlightthickness=1, highlightbackground=color)
                frame.pack(fill=tk.X, pady=3, padx=5)

                tk.Label(
                    frame,
                    text=name,
                    fg=color,
                    bg="#0d0d0d",
                    font=("Tahoma", 11, "bold"),
                    width=35,
                    anchor="w",
                ).pack(side=tk.LEFT, padx=8, pady=5)

                tk.Label(
                    frame,
                    text=cmd,
                    fg="#d1fae5",
                    bg="#0d0d0d",
                    font=("Consolas", 10),
                    anchor="w",
                ).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

                tk.Button(
                    frame,
                    text="📋 نسخ",
                    command=lambda command=cmd: self._copy_to_clipboard(command),
                    bg="#14532d",
                    fg="white",
                    font=("Tahoma", 10),
                    relief=tk.FLAT,
                    cursor="hand2",
                    padx=12,
                    pady=3,
                ).pack(side=tk.RIGHT, padx=5)

                tk.Button(
                    frame,
                    text="🚀 إرسال",
                    command=lambda command=cmd: self._send_to_terminal(command),
                    bg="#0f766e",
                    fg="white",
                    font=("Tahoma", 10),
                    relief=tk.FLAT,
                    cursor="hand2",
                    padx=12,
                    pady=3,
                ).pack(side=tk.RIGHT, padx=5)

        status_var = tk.StringVar(value="")
        status_bar = tk.Label(
            win,
            textvariable=status_var,
            fg=CYAN,
            bg="#0a0a0a",
            font=("Tahoma", 10),
            anchor="w",
            padx=15,
        )
        status_bar.pack(fill=tk.X, side="bottom", pady=5)

        def on_close():
            self._tools_panel_window = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

