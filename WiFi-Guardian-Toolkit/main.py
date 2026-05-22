#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WiFi Guardian Toolkit - Main Entry Point"""

import subprocess
import sys


def install_requirements():
    """تثبيت المتطلبات"""
    required = ["dnspython", "httpx", "reportlab"]
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


if __name__ == "__main__":
    install_requirements()
    
    from app import PreventTrackingApp
    
    app = PreventTrackingApp()
    app.run()
