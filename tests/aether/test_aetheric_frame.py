import unittest
import uuid
import string

from melder.aether.aetheric_frame import AethericFrame
from melder.aether.conduit_cloud import ConduitCloud
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_set import ConcurrentSet


# ----- Test doubles -----

class _StubConduit:
    def __init__(self, tag=None):
        self._cleaned = False
        self.count = 0
        self.tag = tag

    def cleanup(self):
        self._cleaned = True
        self.count += 1


class _BoomConduit:
    def cleanup(self):
        raise RuntimeError("boom")


class TestAethericFrame(unittest.TestCase):

    def setUp(self):
        self.frame = AethericFrame("unit")
        self.assertFalse(self.frame._cleaned)
        self.assertEqual(self.frame.name, "unit")

    # 1 — baseline construction + types
    def test_initial_types_and_defaults(self):
        self.assertTrue(hasattr(self.frame, "_lock"))
        self.assertIsInstance(self.frame._conduits, ConcurrentDict)
        self.assertIsInstance(self.frame._spell_registry, ConcurrentDict)
        self.assertIsInstance(self.frame._conduit_clusters, ConcurrentDict)
        self.assertIsInstance(self.frame._conduit_cloud, ConduitCloud)
        self.assertIsNone(self.frame._configuration)

    # 2 — ULID shape
    def test_ulid_is_string_26_alnum(self):
        _id = self.frame._id
        self.assertIsInstance(_id, str)
        self.assertEqual(len(_id), 26)
        self.assertTrue(all(ch in string.ascii_uppercase + string.ascii_lowercase + string.digits for ch in _id))

    # 3 — add conduits then cleanup: each conduit gets cleaned
    def test_conduits_get_cleaned_before_cleanup(self):
        c1 = _StubConduit("a")
        c2 = _StubConduit("b")
        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        self.frame._conduits[id1] = c1
        self.frame._conduits[id2] = c2

        self.frame.cleanup()

        self.assertTrue(c1._cleaned)
        self.assertTrue(c2._cleaned)
        self.assertTrue(self.frame._cleaned)

    # 4 — cloud is cleaned (capture ref before null)
    def test_cloud_is_cleaned_before_nulling(self):
        cloud_ref = self.frame._conduit_cloud
        self.assertFalse(cloud_ref._cleaned)
        self.frame.cleanup()
        self.assertTrue(cloud_ref._cleaned)

    # 5 — after cleanup, containers are None
    def test_containers_are_set_to_none_after_cleanup(self):
        self.frame.cleanup()
        self.assertIsNone(self.frame._conduits)
        self.assertIsNone(self.frame._spell_registry)
        self.assertIsNone(self.frame._conduit_clusters)
        self.assertIsNone(self.frame._conduit_cloud)

    # 6 — idempotent cleanup
    def test_cleanup_is_idempotent(self):
        self.frame.cleanup()
        self.frame.cleanup()  # must not raise
        self.assertTrue(self.frame._cleaned)
        self.assertIsNone(self.frame._conduits)

    # 7 — boom conduit exceptions are swallowed
    def test_boom_conduit_exception_is_swallowed(self):
        cid = uuid.uuid4()
        self.frame._conduits[cid] = _BoomConduit()
        # should NOT raise
        self.frame.cleanup()
        self.assertTrue(self.frame._cleaned)

    # 8 — name / configuration survive cleanuping
    def test_name_and_configuration_survive_cleanup(self):
        self.frame._configuration = {"x": 1}
        self.frame.cleanup()
        self.assertEqual(self.frame.name, "unit")
        self.assertEqual(self.frame._configuration, {"x": 1})

    # 9 — cluster bookkeeping pre-cleanup
    def test_cluster_bookkeeping_pre_cleanup(self):
        cid1 = uuid.uuid4()
        cid2 = uuid.uuid4()
        self.frame._conduits[cid1] = _StubConduit()
        self.frame._conduits[cid2] = _StubConduit()

        self.frame._conduit_clusters["G"] = ConcurrentList()
        self.frame._conduit_clusters["G"].append(cid1)
        self.frame._conduit_clusters["G"].append(cid2)

        self.assertIn("G", self.frame._conduit_clusters)
        self.assertEqual(list(self.frame._conduit_clusters["G"]), [cid1, cid2])

    # 10 — spell registry pre-cleanup uniqueness
    def test_spell_registry_concurrent_set_uniqueness(self):
        cid = uuid.uuid4()
        s = ConcurrentSet()
        x = "cafebabe" * 8
        s.add(x)
        s.add(x)
        self.frame._spell_registry[cid] = s
        self.assertIn(cid, self.frame._spell_registry)
        self.assertEqual(len(self.frame._spell_registry[cid]), 1)

    # 11 — multiple clusters + contents pre-cleanup
    def test_multiple_clusters_pre_cleanup(self):
        a = uuid.uuid4()
        b = uuid.uuid4()
        c = uuid.uuid4()
        self.frame._conduit_clusters["A"] = ConcurrentList([a, b])
        self.frame._conduit_clusters["B"] = ConcurrentList([c])
        self.assertIn("A", self.frame._conduit_clusters)
        self.assertIn("B", self.frame._conduit_clusters)
        self.assertEqual(set(self.frame._conduit_clusters["A"]), {a, b})
        self.assertEqual(set(self.frame._conduit_clusters["B"]), {c})

    # 12 — dict keys are the UUIDs you inserted
    def test_conduits_dict_keys(self):
        ids = [uuid.uuid4() for _ in range(3)]
        for i in ids:
            self.frame._conduits[i] = _StubConduit()
        self.assertEqual(set(self.frame._conduits.keys()), set(ids))

    # 13 — conduit.cleanup is called exactly once per conduit even if frame.cleanup called twice
    def test_conduit_cleanup_called_once_each(self):
        c1 = _StubConduit()
        c2 = _StubConduit()
        self.frame._conduits[uuid.uuid4()] = c1
        self.frame._conduits[uuid.uuid4()] = c2

        self.frame.cleanup()
        self.frame.cleanup()  # no-op

        self.assertEqual(c1.count, 1)
        self.assertEqual(c2.count, 1)

    # 14 — cannot (and do not) access containers after cleanup; we only check None
    def test_no_container_access_after_cleanup(self):
        self.frame.cleanup()
        self.assertIsNone(self.frame._conduits)
        self.assertIsNone(self.frame._spell_registry)
        self.assertIsNone(self.frame._conduit_clusters)

    # 15 — pre-cleanup: removing from cluster list behaves
    def test_cluster_remove_pre_cleanup(self):
        cid1 = uuid.uuid4()
        cid2 = uuid.uuid4()
        lst = ConcurrentList([cid1, cid2])
        self.frame._conduit_clusters["Z"] = lst
        lst.remove(cid1)
        self.assertEqual(list(self.frame._conduit_clusters["Z"]), [cid2])

    # 16 — pre-cleanup: spell registry can hold multiple IDs for a single conduit
    def test_spell_registry_multiple_ids(self):
        cid = uuid.uuid4()
        s = ConcurrentSet()
        s.add("deadbeef" * 8)
        s.add("feedface" * 8)
        self.frame._spell_registry[cid] = s
        self.assertEqual(len(self.frame._spell_registry[cid]), 2)

    # 17 — RLock existence (we don’t test behavior, just presence)
    def test_lock_presence(self):
        self.assertTrue(hasattr(self.frame, "_lock"))

    # 18 — two frames have unique ULIDs
    def test_two_frames_have_unique_ids(self):
        f2 = AethericFrame("unit2")
        self.assertNotEqual(self.frame._id, f2._id)

    # 19 — cleanuping with no conduits / no registries still works
    def test_cleanup_with_empty_state(self):
        self.frame.cleanup()
        self.assertTrue(self.frame._cleaned)
        self.assertIsNone(self.frame._conduits)

    # 20 — order hint: all conduits cleaned when present, then containers nulled
    def test_all_conduits_cleaned_then_nulled(self):
        c = [_StubConduit(i) for i in range(5)]
        ids = [uuid.uuid4() for _ in range(5)]
        for i, cid in enumerate(ids):
            self.frame._conduits[cid] = c[i]

        self.frame.cleanup()

        self.assertTrue(all(ci._cleaned for ci in c))
        self.assertIsNone(self.frame._conduits)


if __name__ == "__main__":
    unittest.main()
