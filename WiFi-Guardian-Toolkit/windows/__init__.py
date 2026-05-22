# -*- coding: utf-8 -*-
"""Package for all window modules"""

from windows.linking_codex_window import LinkingCodexWindow
from windows.network_info_window import NetworkInfoWindow
from windows.settings_window import SettingsWindow
from windows.tools_window import ToolsWindow
from windows.kali_commands_window import KaliCommandsWindow
from windows.dns_info_window import DNSInfoWindow
from windows.protection_window import ProtectionWindow
from windows.reports_window import ReportsWindow

__all__ = [
    'LinkingCodexWindow',
    'NetworkInfoWindow', 
    'SettingsWindow',
    'ToolsWindow',
    'KaliCommandsWindow',
    'DNSInfoWindow',
    'ProtectionWindow',
    'ReportsWindow'
]
