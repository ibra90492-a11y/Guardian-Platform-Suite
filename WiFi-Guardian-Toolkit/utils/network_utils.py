# -*- coding: utf-8 -*-
"""دوال مساعدة للشبكة - DNS, IP, SSID, etc."""

import socket
import subprocess
import platform
import re
import dns.resolver
import httpx


def get_ssid():
    """الحصول على اسم شبكة WiFi المتصلة"""
    system = platform.system()
    if system != "Windows":
        return "Unsupported OS"
    
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=8
        )
        for line in result.stdout.splitlines():
            if "SSID" in line and "BSSID" not in line and ":" in line:
                return line.split(":", 1)[1].strip() or "Not connected"
    except Exception:
        pass
    return "Not connected"


def get_local_ip():
    """الحصول على عنوان IP المحلي"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("1.1.1.1", 80))
            return sock.getsockname()[0]
    except Exception:
        return "N/A"


def get_active_interface_index():
    """الحصول على مؤشر الواجهة النشطة"""
    system = platform.system()
    if system != "Windows":
        return None
    
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -First 1 -ExpandProperty ifIndex)"],
            capture_output=True,
            text=True,
            timeout=10
        )
        match = re.search(r"\d+", result.stdout)
        return match.group(0) if match else None
    except Exception:
        return None


def test_doh_query():
    """اختبار اتصال DNS over HTTPS"""
    try:
        response = httpx.get(
            "https://cloudflare-dns.com/dns-query",
            params={"name": "cloudflare.com", "type": "A"},
            headers={"accept": "application/dns-json"},
            timeout=6
        )
        return "Yes" if response.status_code == 200 else "No"
    except Exception:
        return "No"


def probe_host(host, port=853, timeout=3):
    """اختبار اتصال بمضيف محدد"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "Yes"
    except Exception:
        return "No"


def collect_cf_snapshot():
    """جمع معلومات Cloudflare"""
    snapshot = {
        "ip": "N/A",
        "doh": "No",
        "dot": "No",
        "warp": "No",
        "state": "Unknown",
        "cf_dc": "Unknown",
        "as_name": "Unknown",
        "as_number": "Unknown",
    }
    
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(
                "https://one.one.one.one/cdn-cgi/trace",
                headers={"User-Agent": "Mozilla/5.0"}
            )
        data = {}
        for line in response.text.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip().lower()] = value.strip()

        snapshot["ip"] = data.get("ip", "N/A")
        snapshot["warp"] = "Yes" if data.get("warp", "").lower() == "on" else "No"
        snapshot["cf_dc"] = data.get("colo", "Unknown").upper()
        snapshot["as_name"] = data.get("asorg", "Unknown")
        snapshot["as_number"] = data.get("asn", "Unknown")
        
        loc_map = {"SA": "Saudi Arabia", "AE": "UAE", "US": "USA", "GB": "UK"}
        snapshot["state"] = loc_map.get(data.get("loc", "").upper(), data.get("loc", "Unknown"))
    except Exception:
        pass

    snapshot["doh"] = test_doh_query()
    snapshot["dot"] = probe_host("1.1.1.1", 853)
    return snapshot


def get_dns_summary():
    """إرجاع ملخص DNS سريع للنوافذ التي تحتاج نصاً مباشراً."""
    snapshot = collect_cf_snapshot()
    return "\n".join([
        f"SSID: {get_ssid()}",
        f"Local IP: {get_local_ip()}",
        f"DNS (DoH): {snapshot.get('doh', 'No')}",
        f"DNS (DoT): {snapshot.get('dot', 'No')}",
        f"WARP: {snapshot.get('warp', 'No')}",
        f"Location: {snapshot.get('state', 'Unknown')}",
        f"Data Center: {snapshot.get('cf_dc', 'Unknown')}",
        f"AS Name: {snapshot.get('as_name', 'Unknown')}",
        f"AS Number: {snapshot.get('as_number', 'Unknown')}",
    ])
