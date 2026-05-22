import os
import tempfile
import unittest

from core.report_exporter import export_security_report


class TestReportExporter(unittest.TestCase):
    def test_export_report_files(self):
        with tempfile.TemporaryDirectory() as td:
            payload = {
                "generated_at": "2026-05-08 10:00:00",
                "mode": "defensive",
                "protection_active": True,
                "security_score": 90,
                "security_level": "HARDENED",
                "snapshot": {"doh": "Yes", "dot": "Yes", "warp": "No", "conn_111": "Yes", "ip_address": "1.2.3.4", "state": "OK"},
                "diagnostics": {"network": "Yes"},
                "audit_tail": [],
            }
            json_path, txt_path = export_security_report(td, payload)
            self.assertTrue(os.path.exists(json_path))
            self.assertTrue(os.path.exists(txt_path))


if __name__ == "__main__":
    unittest.main()
