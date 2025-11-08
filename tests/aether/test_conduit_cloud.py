import unittest

from melder.aether.conduit_cloud import ConduitCloud
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict


class _StubConduit:
    def __init__(self, name):
        self.name = name
        self.sealed = False
    def seal(self):
        self.sealed = True


class TestConduitCloud(unittest.TestCase):
    def setUp(self):
        self.cloud = ConduitCloud("unit")
        # sanity
        self.assertFalse(self.cloud._sealed)
        self.assertEqual(self.cloud._name, "unit")
        self.assertIsInstance(self.cloud._registry, ConcurrentDict)

    # 1
    def test_initial_state(self):
        self.assertEqual(len(self.cloud._registry), 0)

    # 2
    def test_register_then_get(self):
        c = _StubConduit("alpha")
        self.cloud._register_conduit(c)
        got = self.cloud.get_conduit("alpha")
        self.assertIs(got, c)

    # 3
    def test_register_duplicate_raises(self):
        c1 = _StubConduit("dup")
        c2 = _StubConduit("dup")
        self.cloud._register_conduit(c1)
        with self.assertRaises(ValueError):
            self.cloud._register_conduit(c2)

    # 4
    def test_register_none_name_raises(self):
        c = _StubConduit(None)
        with self.assertRaises(ValueError):
            self.cloud._register_conduit(c)

    # 5
    def test_get_missing_raises(self):
        with self.assertRaises(ValueError):
            self.cloud.get_conduit("ghost")

    # 6
    def test_seal_clears_registry(self):
        self.cloud._register_conduit(_StubConduit("a"))
        self.cloud._register_conduit(_StubConduit("b"))
        self.assertGreater(len(self.cloud._registry), 0)
        self.cloud.seal()
        self.assertEqual(len(self.cloud._registry), 0)
        self.assertTrue(self.cloud._sealed)

    # 7
    def test_get_after_seal_raises_runtimeerror(self):
        self.cloud._register_conduit(_StubConduit("x"))
        self.cloud.seal()
        with self.assertRaises(RuntimeError):
            self.cloud.get_conduit("x")

    # 8
    def test_seal_is_idempotent(self):
        self.cloud.seal()
        self.assertTrue(self.cloud._sealed)
        # calling again should not raise and should not change state
        self.cloud.seal()
        self.assertTrue(self.cloud._sealed)
        self.assertEqual(len(self.cloud._registry), 0)

    # 9
    def test_register_then_seal_then_register_again_is_blocked_by_get(self):
        # Note: _register_conduit does not check _sealed (by design), but get_conduit does.
        # We verify that sealing makes the cloud unusable even if someone mutates the registry.
        c = _StubConduit("late")
        self.cloud.seal()
        # Manually try to register post-seal (internal misuse)
        self.cloud._registry["late"] = c
        with self.assertRaises(RuntimeError):
            self.cloud.get_conduit("late")

    # 10
    def test_multiple_conduits_resolve_by_name(self):
        a = _StubConduit("a")
        b = _StubConduit("b")
        self.cloud._register_conduit(a)
        self.cloud._register_conduit(b)
        self.assertIs(self.cloud.get_conduit("a"), a)
        self.assertIs(self.cloud.get_conduit("b"), b)


if __name__ == "__main__":
    unittest.main()
