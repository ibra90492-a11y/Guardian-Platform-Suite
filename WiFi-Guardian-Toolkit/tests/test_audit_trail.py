import os
import tempfile
import unittest

from core.audit_trail import AuditTrail


class TestAuditTrail(unittest.TestCase):
    def test_add_and_read_recent(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "audit.jsonl")
            audit = AuditTrail(path)
            audit.add_event("evt1", "INFO", "details1")
            audit.add_event("evt2", "WARN", "details2")
            recent = audit.read_recent(limit=2)
            self.assertEqual(len(recent), 2)
            self.assertEqual(recent[-1]["event"], "evt2")


if __name__ == "__main__":
    unittest.main()
