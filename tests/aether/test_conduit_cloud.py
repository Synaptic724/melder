import unittest
import string

from melder.aether.conduit_cloud import ConduitCloud
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict


# ----- Test doubles -----

class _StubConduit:
    def __init__(self, name):
        self.name = name
        self._cleaned = False
    def cleanup(self):
        self._cleaned = True


class TestConduitCloud(unittest.TestCase):
    def setUp(self):
        self.cloud = ConduitCloud("unit")
        # sanity on construction
        self.assertFalse(self.cloud._cleaned)
        self.assertEqual(self.cloud._name, "unit")
        self.assertIsInstance(self.cloud._registry, ConcurrentDict)

    # 1 — baseline state before any ops
    def test_initial_state_empty_registry(self):
        self.assertEqual(len(self.cloud._registry), 0)

    # 2 — ULID presence/shape (26 char base32-ish)
    def test_ulid_shape(self):
        the_id = self.cloud._id
        self.assertIsInstance(the_id, str)
        self.assertEqual(len(the_id), 26)
        self.assertTrue(all(ch in string.ascii_letters + string.digits for ch in the_id))

    # 3 — register then get works
    def test_register_then_get(self):
        c = _StubConduit("alpha")
        self.cloud._register_conduit(c)
        got = self.cloud.get_conduit("alpha")
        self.assertIs(got, c)

    # 4 — duplicate register by name raises
    def test_register_duplicate_raises(self):
        self.cloud._register_conduit(_StubConduit("dup"))
        with self.assertRaises(ValueError):
            self.cloud._register_conduit(_StubConduit("dup"))

    # 5 — None name rejects
    def test_register_none_name_raises(self):
        with self.assertRaises(ValueError):
            self.cloud._register_conduit(_StubConduit(None))

    # 6 — missing name raises ValueError
    def test_get_missing_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.cloud.get_conduit("ghost")

    # 7 — multiple conduits resolve by distinct names
    def test_multiple_register_and_resolve(self):
        a = _StubConduit("a")
        b = _StubConduit("b")
        self.cloud._register_conduit(a)
        self.cloud._register_conduit(b)
        self.assertIs(self.cloud.get_conduit("a"), a)
        self.assertIs(self.cloud.get_conduit("b"), b)

    # 8 — case sensitivity preserved
    def test_names_are_case_sensitive(self):
        self.cloud._register_conduit(_StubConduit("Alpha"))
        self.cloud._register_conduit(_StubConduit("alpha"))
        self.assertIsInstance(self.cloud.get_conduit("Alpha"), _StubConduit)
        self.assertIsInstance(self.cloud.get_conduit("alpha"), _StubConduit)
        self.assertIsNot(self.cloud.get_conduit("Alpha"), self.cloud.get_conduit("alpha"))

    # 9 — cleanup clears usability: any get raises RuntimeError
    def test_get_after_cleanup_raises_runtimeerror(self):
        self.cloud._register_conduit(_StubConduit("x"))
        self.cloud.cleanup()
        with self.assertRaises(RuntimeError):
            self.cloud.get_conduit("x")

    # 10 — cleanup is idempotent (second call no-op)
    def test_cleanup_is_idempotent(self):
        self.cloud.cleanup()
        self.assertTrue(self.cloud._cleaned)
        # calling again should not raise and keeps cleaned
        self.cloud.cleanup()
        self.assertTrue(self.cloud._cleaned)

    # 11 — cleanup after multiple registrations still blocks all gets
    def test_cleanup_blocks_all_gets(self):
        for n in ("a", "b", "c"):
            self.cloud._register_conduit(_StubConduit(n))
        self.cloud.cleanup()
        for n in ("a", "b", "c"):
            with self.assertRaises(RuntimeError):
                self.cloud.get_conduit(n)

    # 12 — name survives cleaning
    def test_name_survives_cleanup(self):
        self.cloud.cleanup()
        self.assertEqual(self.cloud._name, "unit")

    # 13 — id survives cleaning
    def test_ulid_survives_cleanup(self):
        cached = self.cloud._id
        self.cloud.cleanup()
        self.assertEqual(self.cloud._id, cached)

    # 14 — registry mutability before cleanup (safe pre-cleanup checks)
    def test_registry_contains_pre_cleanup(self):
        self.cloud._register_conduit(_StubConduit("k"))
        self.assertIn("k", self.cloud._registry)
        self.assertGreaterEqual(len(self.cloud._registry), 1)

    # 15 — separate clouds are isolated
    def test_two_clouds_isolated(self):
        c1 = ConduitCloud("one")
        c2 = ConduitCloud("two")
        a = _StubConduit("a")
        c1._register_conduit(a)
        # exists in c1
        self.assertIs(c1.get_conduit("a"), a)
        # not in c2
        with self.assertRaises(ValueError):
            c2.get_conduit("a")
        # cleanup c1 doesn't affect c2
        c1.cleanup()
        self.assertFalse(c2._cleaned)
        self.assertIsInstance(c2._registry, ConcurrentDict)
        # c2 still operable
        b = _StubConduit("b")
        c2._register_conduit(b)
        self.assertIs(c2.get_conduit("b"), b)


if __name__ == "__main__":
    unittest.main()
