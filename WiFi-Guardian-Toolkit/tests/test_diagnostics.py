import unittest
from unittest import mock

from core.diagnostics import run_diagnostics


class TestDiagnostics(unittest.TestCase):
    @mock.patch("core.diagnostics.platform.system", return_value="Windows")
    @mock.patch("core.diagnostics._run_quick")
    @mock.patch("core.diagnostics.importlib.import_module")
    @mock.patch("core.diagnostics.socket.create_connection")
    def test_diagnostics_flags(self, _sock, _import_module, _run_quick, _platform):
        def run_quick_mock(command, timeout=5):
            if isinstance(command, (list, tuple)):
                if list(command[:3]) == ["wsl", "-l", "-q"]:
                    return True
                if len(command) >= 4 and command[0] == "wsl" and command[1] == "-d" and command[2] == "kali-linux":
                    return False
            else:
                cmd_text = str(command)
                if "wsl -l -q" in cmd_text:
                    return True
                if "wsl -d kali-linux" in cmd_text:
                    return False
            return False

        _run_quick.side_effect = run_quick_mock
        result = run_diagnostics(timeout_seconds=1)
        self.assertIn(result["wsl"], {"Yes", "No"})
        self.assertIn(result["kali"], {"Yes", "No"})
        self.assertEqual(result["network"], "Yes")
        self.assertEqual(result["dns_module"], "Yes")


if __name__ == "__main__":
    unittest.main()
