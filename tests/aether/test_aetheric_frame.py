import unittest
import uuid

from melder.aether.aetheric_frame import AethericFrame
from melder.aether.conduit_cloud import ConduitCloud
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_set import ConcurrentSet


class _StubConduit:
    def __init__(self):
        self.sealed = False

    def seal(self):
        self.sealed = True


class _BoomConduit:
    def seal(self):
        raise RuntimeError("boom")


class TestAethericFrame(unittest.TestCase):
    def setUp(self):
        self.frame = AethericFrame("unit")

        # sanity on fresh state
        self.assertFalse(self.frame._sealed)
        self.assertEqual(self.frame.name, "unit")

    # 1
    def test_initial_types_and_defaults(self):
        self.assertIsInstance(self.frame._lock.__class__.__name__, str)  # lock exists
        self.assertIsInstance(self.frame._conduits, ConcurrentDict)
        self.assertIsInstance(self.frame._spell_registry, ConcurrentDict)
        self.assertIsInstance(self.frame._conduit_clusters, ConcurrentDict)
        self.assertIsInstance(self.frame._conduit_cloud, ConduitCloud)
        self.assertIsNone(self.frame._configuration)

    # 2
    def test_add_conduit_and_seal_calls_conduit_seal(self):
        c1 = _StubConduit()
        c2 = _StubConduit()
        cid1 = uuid.uuid4()
        cid2 = uuid.uuid4()

        self.frame._conduits[cid1] = c1
        self.frame._conduits[cid2] = c2

        self.frame.seal()

        self.assertTrue(c1.sealed)
        self.assertTrue(c2.sealed)

    # 3
    def test_seal_clears_conduits_and_registries(self):
        # seed registries
        cid = uuid.uuid4()
        c = _StubConduit()
        self.frame._conduits[cid] = c

        sset = ConcurrentSet()
        sset.add("deadbeef" * 8)
        self.frame._spell_registry[cid] = sset

        self.frame._conduit_clusters["groupA"] = ConcurrentList([cid])

        self.frame.seal()

        self.assertEqual(len(self.frame._conduits), 0)
        self.assertEqual(len(self.frame._spell_registry), 0)
        self.assertEqual(len(self.frame._conduit_clusters), 0)
        self.assertTrue(self.frame._sealed)

    # 4
    def test_conduit_cloud_is_sealed_with_frame(self):
        self.assertFalse(self.frame._conduit_cloud._sealed)
        self.frame.seal()
        self.assertTrue(self.frame._conduit_cloud._sealed)

    # 5
    def test_seal_is_idempotent(self):
        self.frame.seal()
        # re-populate after seal to ensure a second seal doesn't regress (shouldn't be possible in real flow)
        # but we only check that calling seal again doesn't explode and remains sealed
        self.frame.seal()
        self.assertTrue(self.frame._sealed)

    # 6
    def test_seal_returns_early_when_already_sealed(self):
        self.frame.seal()
        # mutate an internal value to ensure the early-return path doesn't touch data
        was_cloud = self.frame._conduit_cloud
        self.frame.seal()
        self.assertIs(self.frame._conduit_cloud, was_cloud)

    # 7
    def test_bubbling_conduit_exception(self):
        cid = uuid.uuid4()
        self.frame._conduits[cid] = _BoomConduit()
        with self.assertRaises(RuntimeError):
            self.frame.seal()
        # After an exception, frame should remain unsealed and registries intact
        self.assertFalse(self.frame._sealed)
        self.assertIn(cid, self.frame._conduits)

    # 8
    def test_cluster_bookkeeping_manual(self):
        cid1 = uuid.uuid4()
        cid2 = uuid.uuid4()
        self.frame._conduit_clusters["G"] = ConcurrentList()
        self.frame._conduit_clusters["G"].append(cid1)
        self.frame._conduit_clusters["G"].append(cid2)
        self.assertIn(cid1, self.frame._conduit_clusters["G"])
        self.assertIn(cid2, self.frame._conduit_clusters["G"])
        # Clear via seal
        self.frame.seal()
        self.assertNotIn("G", self.frame._conduit_clusters)

    # 9
    def test_spell_registry_bookkeeping_manual(self):
        cid = uuid.uuid4()
        s = ConcurrentSet()
        s.add("cafebabe" * 8)
        self.frame._spell_registry[cid] = s
        self.assertIn(cid, self.frame._spell_registry)
        self.assertIn("cafebabe" * 8, self.frame._spell_registry[cid])
        self.frame.seal()
        self.assertEqual(len(self.frame._spell_registry), 0)

    # 10
    def test_seal_does_not_mutate_name_or_configuration(self):
        self.frame._configuration = {"x": 1}
        self.frame.seal()
        self.assertEqual(self.frame.name, "unit")
        self.assertEqual(self.frame._configuration, {"x": 1})

    # 11
    def test_double_seal_does_not_call_conduit_seal_twice(self):
        class _CountConduit:
            def __init__(self):
                self.count = 0
            def seal(self):
                self.count += 1

        cid = uuid.uuid4()
        cc = _CountConduit()
        self.frame._conduits[cid] = cc

        self.frame.seal()
        first = cc.count
        self.frame.seal()
        second = cc.count
        self.assertEqual(first, 1)
        self.assertEqual(second, 1)

    # 12
    def test_conduits_iterated_before_clear(self):
        # Ensure seal order is: seal each conduit, then clear dicts
        tracker = []
        class _TrackConduit:
            def __init__(self, tag):
                self.tag = tag
            def seal(self):
                tracker.append(self.tag)

        for i in range(3):
            self.frame._conduits[uuid.uuid4()] = _TrackConduit(i)

        self.frame.seal()
        self.assertEqual(tracker, [0, 1, 2])
        self.assertEqual(len(self.frame._conduits), 0)

    # 13
    def test_no_ops_when_already_sealed(self):
        self.frame.seal()
        # Take snapshots
        conduits_len = len(self.frame._conduits)
        spells_len = len(self.frame._spell_registry)
        clusters_len = len(self.frame._conduit_clusters)
        cloud = self.frame._conduit_cloud
        # Call again
        self.frame.seal()
        self.assertEqual(len(self.frame._conduits), conduits_len)
        self.assertEqual(len(self.frame._spell_registry), spells_len)
        self.assertEqual(len(self.frame._conduit_clusters), clusters_len)
        self.assertIs(self.frame._conduit_cloud, cloud)

    # 14
    def test_state_after_init_then_after_seal(self):
        # preconditions
        self.assertFalse(self.frame._sealed)
        # mutate a bit
        cid = uuid.uuid4()
        self.frame._conduits[cid] = _StubConduit()
        self.frame._conduit_clusters["X"] = ConcurrentList([cid])
        self.frame._spell_registry[cid] = ConcurrentSet(["dead" * 16])

        self.frame.seal()
        # postconditions
        self.assertTrue(self.frame._sealed)
        self.assertEqual(len(self.frame._conduits), 0)
        self.assertEqual(len(self.frame._conduit_clusters), 0)
        self.assertEqual(len(self.frame._spell_registry), 0)


if __name__ == "__main__":
    unittest.main()
