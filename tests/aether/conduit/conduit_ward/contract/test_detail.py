# tests/aether/conduit/conduit_ward/contract/test_detail.py
import threading
import time
import unittest

from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions


class TestDetail(unittest.TestCase):

    # ---------- Construction ----------

    def test_construct_with_valid_enum(self):
        d = Detail("SID1", Permissions.create)
        self.assertEqual(d.spell_id, "SID1")
        self.assertIs(d.permissions, Permissions.create)

    def test_construct_with_read_permission(self):
        d = Detail("READ_SPELL", Permissions.read)
        self.assertEqual(d.spell_id, "READ_SPELL")
        self.assertIs(d.permissions, Permissions.read)

    def test_construct_with_block_permission(self):
        d = Detail("BLOCK_SPELL", Permissions.block)
        self.assertEqual(d.spell_id, "BLOCK_SPELL")
        self.assertIs(d.permissions, Permissions.block)

    def test_construct_rejects_string_permission(self):
        with self.assertRaises(TypeError):
            Detail("SIDX", "create")  # not an enum

    def test_construct_rejects_none_permission(self):
        with self.assertRaises(TypeError):
            Detail("SIDX", None)

    # Note: spell_id type is not validated by the class; ensure it accepts strings freely.
    def test_spell_id_accepts_arbitrary_string(self):
        weird = "  S I D :/\\x??  "
        d = Detail(weird, Permissions.read)
        self.assertEqual(d.spell_id, weird)

    # ---------- Cleaning semantics ----------

    def test_cleanup_nulls_fields(self):
        d = Detail("SID2", Permissions.create)
        d.cleanup()
        self.assertIsNone(d.spell_id)
        self.assertIsNone(d.permissions)

    def test_cleanup_is_idempotent(self):
        d = Detail("SID3", Permissions.read)
        d.cleanup()
        # Call again; should not raise and should remain None
        d.cleanup()
        self.assertIsNone(d.spell_id)
        self.assertIsNone(d.permissions)

    def test_multiple_instances_independent(self):
        d1 = Detail("A", Permissions.create)
        d2 = Detail("B", Permissions.read)
        d1.cleanup()
        self.assertIsNone(d1.spell_id)
        self.assertEqual(d2.spell_id, "B")
        self.assertIs(d2.permissions, Permissions.read)

    # ---------- Concurrency / thread-safety ----------

    def test_concurrent_cleanup_calls_do_not_raise(self):
        d = Detail("SID-CONC", Permissions.read)

        errors = []
        def worker():
            try:
                # hammer cleanup a few times
                for _ in range(50):
                    d.cleanup()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertIsNone(d.spell_id)
        self.assertIsNone(d.permissions)

    # ---------- Sanity checks around state transitions ----------

    def test_values_visible_before_cleanup(self):
        d = Detail("PRE", Permissions.create)
        self.assertEqual(d.spell_id, "PRE")
        self.assertIs(d.permissions, Permissions.create)

    def test_values_cleared_after_cleanup(self):
        d = Detail("POST", Permissions.block)
        d.cleanup()
        # Access after cleanup: attributes are still present but set to None
        self.assertIsNone(d.spell_id)
        self.assertIsNone(d.permissions)

    def test_recleanup_after_short_delay(self):
        d = Detail("REcleanup", Permissions.read)
        d.cleanup()
        time.sleep(0.001)
        # Should remain harmless
        d.cleanup()
        self.assertIsNone(d.spell_id)
        self.assertIsNone(d.permissions)

    # ---------- Defensive behavior expectations ----------

    def test_no_implicit_permission_conversion(self):
        # Ensure we don't silently coerce strings like "Create" or "read"
        with self.assertRaises(TypeError):
            Detail("SIDX", Permissions)  # passing the enum type instead of a member

        with self.assertRaises(TypeError):
            Detail("SIDX", "Read")  # not allowed

    def test_large_spell_id(self):
        big_id = "S" * 10_000
        d = Detail(big_id, Permissions.create)
        self.assertEqual(d.spell_id, big_id)
        d.cleanup()
        self.assertIsNone(d.spell_id)


if __name__ == "__main__":
    unittest.main()
