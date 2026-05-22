# -*- coding: utf-8 -*-
"""تنفيذ الأوامر على أنظمة مختلفة (Kali, PowerShell, CMD)"""

import subprocess
import platform


class TerminalExecutor:
    """تنفيذ الأوامر على أنظمة مختلفة"""
    
    @staticmethod
    def get_wsl_distro():
        """الحصول على اسم توزيعة WSL المثبتة"""
        try:
            result = subprocess.run(
                ["wsl", "-l", "-q"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=8
            )
            names = [name.replace("\x00", "").strip() for name in result.stdout.splitlines()]
            names = [name for name in names if name]
            for name in names:
                if "kali" in name.lower():
                    return name
            return names[0] if names else None
        except Exception:
            return None
    
    @staticmethod
    def execute_kali_command(command):
        """تنفيذ أمر على Kali Linux عبر WSL"""
        try:
            distro = TerminalExecutor.get_wsl_distro() or "kali-linux"
            result = subprocess.run(
                ["wsl", "-d", distro, "-u", "root", "--", "bash", "-lc", command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return (output or "Command executed successfully")[:3000]
        except FileNotFoundError:
            return "WSL not installed or Kali Linux not available"
        except subprocess.TimeoutExpired:
            return "Command timeout (30 seconds)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def execute_powershell_command(command):
        """تنفيذ أمر على PowerShell"""
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return (output or "Command executed successfully")[:3000]
        except subprocess.TimeoutExpired:
            return "Command timeout (30 seconds)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def execute_cmd_command(command):
        """تنفيذ أمر على CMD"""
        try:
            result = subprocess.run(
                ["cmd", "/c", command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return (output or "Command executed successfully")[:3000]
        except subprocess.TimeoutExpired:
            return "Command timeout (30 seconds)"
        except Exception as e:
            return f"Error: {str(e)}"
