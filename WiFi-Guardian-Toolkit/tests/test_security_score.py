import unittest

from core.security_score import calculate_security_score, score_level


class TestSecurityScore(unittest.TestCase):
    def test_full_hardened_score(self):
        snapshot = {
            "doh": "Yes",
            "dot": "Yes",
            "warp": "Yes",
            "conn_111": "Yes",
        }
        diagnostics = {
            "wsl": "Yes",
            "kali": "Yes",
            "network": "Yes",
            "dns_module": "Yes",
        }
        score = calculate_security_score(snapshot, diagnostics)
        self.assertEqual(score, 100)
        self.assertEqual(score_level(score), "HARDENED")

    def test_low_score(self):
        snapshot = {
            "doh": "No",
            "dot": "No",
            "warp": "No",
            "conn_111": "No",
        }
        diagnostics = {
            "wsl": "No",
            "kali": "No",
            "network": "No",
            "dns_module": "No",
        }
        score = calculate_security_score(snapshot, diagnostics)
        self.assertEqual(score, 0)
        self.assertEqual(score_level(score), "RISK")


if __name__ == "__main__":
    unittest.main()
