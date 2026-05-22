from __future__ import annotations

import sys
import webbrowser

from run import BACKEND_URL, FRONTEND_URL
from run_desktop import main as desktop_main


def run_system() -> int:
    """Quick launcher for the Guardian desktop application."""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     Guardian Cyber Assessment Platform                      ║
║                                                              ║
║     تشغيل النظام مباشرة                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )
    print("سيتم تشغيل تطبيق سطح المكتب مع الواجهة المدمجة داخل الفورم.")
    print(f"الداشبورد الداخلي: {FRONTEND_URL}")
    print(f"الوثائق: {BACKEND_URL}/docs")

    if "--docs" in sys.argv:
        webbrowser.open(f"{BACKEND_URL}/docs")
        sys.argv.remove("--docs")

    return desktop_main()


if __name__ == "__main__":
    raise SystemExit(run_system())
