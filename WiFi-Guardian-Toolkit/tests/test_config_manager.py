import os
import tempfile
import unittest

from core.config_manager import ConfigManager, DEFAULT_CONFIG


class TestConfigManager(unittest.TestCase):
    def test_load_creates_default(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "app_config.json")
            manager = ConfigManager(path)
            data = manager.load()
            self.assertEqual(data["provider"], DEFAULT_CONFIG["provider"])
            self.assertTrue(os.path.exists(path))

    def test_save_and_reload(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "app_config.json")
            manager = ConfigManager(path)
            manager.save({"provider": "cloudflare", "refresh_interval_seconds": 30})
            data = manager.load()
            self.assertEqual(data["provider"], "cloudflare")
            self.assertEqual(data["refresh_interval_seconds"], 30)


if __name__ == "__main__":
    unittest.main()
