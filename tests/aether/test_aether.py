import unittest
import uuid

from melder.aether.aether import Aether
from melder.aether.aetheric_frame import AethericFrame
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict


# --- helpers -----------------------------------------------------------------

def _force_reset_aether_singleton():
    """
    Guarantee Aether() constructs a brand-new, fully initialized instance.
    We must clear BOTH the instance holder and the class-level initialized flag.
    """
    if hasattr(Aether, "_instance"):
        Aether._instance = None
    if hasattr(Aether, "_initialized"):
        Aether._initialized = False


# --- test doubles -------------------------------------------------------------

class _StubCloud:
    def __init__(self):
        self.registered = []

    def _register_conduit(self, conduit):
        self.registered.append(conduit)


class _DummyCtx:
    def __init__(self, cid=None):
        import uuid as _uuid
        self._conduit_id = cid or _uuid.uuid4()


class _DummyConduit:
    def __init__(self, name="c", cid=None):
        self.name = name
        self._id = _DummyCtx(cid)


# --- tests -------------------------------------------------------------------

class TestAether(unittest.TestCase):

    def setUp(self):
        # Force a truly fresh singleton per test
        _force_reset_aether_singleton()
        self.aether = Aether()

        # Fresh instance should have a default frame, but keep this guard for safety
        if self.aether._default_frame is None:
            self.aether._aetheric_frames = ConcurrentDict()
            self.aether._aetheric_frames["default"] = AethericFrame("default")
            self.aether._default_frame = self.aether._aetheric_frames["default"]

        # Start clean registries + uncleaned flags
        df = self.aether._default_frame
        df._conduits.clear()
        df._conduit_clusters.clear()
        df._spell_registry.clear()
        df._cleaned = False
        self.aether._cleaned = False

    # Replace the old “test_reset_for_testing_resets_singleton” with this:
    def test_cleanup_and_manual_rehydrate(self):
        # cleanup should null out default frame
        self.assertFalse(self.aether._cleaned)
        self.aether.cleanup()
        self.assertTrue(self.aether._cleaned)
        self.assertIsNone(self.aether._default_frame)

        # True rehydrate: kill singleton ref + init flag, construct a new Aether
        _force_reset_aether_singleton()
        new_aether = Aether()
        self.assertIsNot(self.aether, new_aether)

        # New instance should come up with a default frame and be uncleaned
        if new_aether._default_frame is None:
            new_aether._aetheric_frames = ConcurrentDict()
            new_aether._aetheric_frames["default"] = AethericFrame("default")
            new_aether._default_frame = new_aether._aetheric_frames["default"]
        self.assertIsNotNone(new_aether._default_frame)
        self.assertIn("default", new_aether._aetheric_frames)
        self.assertFalse(new_aether._cleaned)

    # 1
    def test_singleton_identity(self):
        a1 = Aether()
        a2 = Aether()
        self.assertIs(a1, a2)

    # 2
    def test_default_frame_created(self):
        self.assertIn("default", self.aether._aetheric_frames)
        self.assertIs(self.aether._default_frame, self.aether._aetheric_frames["default"])

    # 3
    def test_cleanup_idempotent_and_flags(self):
        self.assertFalse(self.aether._cleaned)
        self.aether.cleanup()
        self.assertTrue(self.aether._cleaned)
        self.assertIsNone(self.aether._default_frame)
        # second cleanup should not raise or change anything
        self.aether.cleanup()
        self.assertTrue(self.aether._cleaned)

    # 4
    def test_cleanup_calls_frame_cleanup_even_on_exception(self):
        class _BadFrame(AethericFrame):
            def cleanup(self):
                raise RuntimeError("boom")

        # Inject a bad frame next to default
        self.aether._aetheric_frames["bad"] = _BadFrame("bad")
        # Should not raise
        self.aether.cleanup()

    # 6
    def test_bind_and_get_configuration_default(self):
        cfg = object()
        self.aether._bind_configuration(cfg)
        got = self.aether._get_configuration()
        self.assertIs(got, cfg)

    # 7
    def test_bind_configuration_nonexistent_frame_raises(self):
        with self.assertRaises(ValueError):
            self.aether._bind_configuration(object(), "nope")

    # 8
    def test_get_configuration_nonexistent_frame_raises(self):
        with self.assertRaises(ValueError):
            self.aether._get_configuration("ghost")

    # 9
    def test_register_conduit_cloud_calls_register(self):
        cloud = _StubCloud()
        self.aether._default_frame._conduit_cloud = cloud
        c = _DummyConduit("X")
        self.aether._register_conduit_cloud(c)
        self.assertEqual([c], cloud.registered)

    # 10
    def test_get_conduit_cloud_default(self):
        cloud = _StubCloud()
        self.aether._default_frame._conduit_cloud = cloud
        got = self.aether._get_conduit_cloud()
        self.assertIs(got, cloud)

    # 11
    def test_add_conduit_success(self):
        c = _DummyConduit("alpha")
        self.aether._default_frame._conduits.clear()
        self.aether._add_conduit(c)
        cid = c._id
        self.assertIn(cid, self.aether._default_frame._conduits)
        self.assertIs(self.aether._default_frame._conduits[cid], c)

    # 12
    def test_add_conduit_duplicate_raises(self):
        c = _DummyConduit("dup", cid=uuid.uuid4())
        self.aether._default_frame._conduits.clear()
        self.aether._default_frame._conduits[c._id] = c
        with self.assertRaises(ValueError):
            self.aether._add_conduit(c)

    # 13
    def test_remove_conduit_success(self):
        c = _DummyConduit("gone", cid=uuid.uuid4())
        self.aether._default_frame._conduits.clear()
        self.aether._default_frame._conduits[c._id] = c
        self.aether._remove_conduit(c)
        self.assertNotIn(c._id, self.aether._default_frame._conduits)

    # 14
    def test_remove_conduit_missing_raises(self):
        c = _DummyConduit("missing", cid=uuid.uuid4())
        self.aether._default_frame._conduits.clear()
        with self.assertRaises(ValueError):
            self.aether._remove_conduit(c)

    # 15
    def test_get_conduit_by_name(self):
        c1 = _DummyConduit("alpha", cid=uuid.uuid4())
        c2 = _DummyConduit("beta", cid=uuid.uuid4())
        self.aether._default_frame._conduits.clear()
        self.aether._default_frame._conduits[c1._id] = c1
        self.aether._default_frame._conduits[c2._id] = c2
        self.assertIs(self.aether._get_conduit_by_name("beta"), c2)

    # 16
    def test_get_conduit_by_name_raises_when_not_found(self):
        self.aether._default_frame._conduits.clear()
        with self.assertRaises(ValueError):
            self.aether._get_conduit_by_name("nope")

    # 17
    def test_get_conduit_by_id(self):
        c = _DummyConduit("x", cid=uuid.uuid4())
        self.aether._default_frame._conduits.clear()
        self.aether._default_frame._conduits[c._id] = c
        got = self.aether._get_conduit_by_id(c._id)
        self.assertIs(got, c)

    # 18
    def test_get_conduit_by_id_raises_when_missing(self):
        self.aether._default_frame._conduits.clear()
        with self.assertRaises(ValueError):
            self.aether._get_conduit_by_id(uuid.uuid4())

    # 19
    def test_create_cluster_success_and_duplicate_raises(self):
        frame = self.aether._default_frame
        frame._conduit_clusters.clear()
        self.aether._create_cluster("group1")
        self.assertIn("group1", frame._conduit_clusters)
        with self.assertRaises(ValueError):
            self.aether._create_cluster("group1")

    # 20
    def test_cluster_ops_and_spell_registry_lookup(self):
        frame = self.aether._default_frame
        # Prepare clusters
        frame._conduit_clusters.clear()
        self.aether._create_cluster("g")
        # Prepare conduits
        frame._conduits.clear()
        c = _DummyConduit("z", cid=uuid.uuid4())
        frame._conduits[c._id] = c
        # Add/remove in cluster
        self.aether._add_conduit_to_cluster(c, "g")
        ids = self.aether._get_conduits_in_cluster("g")
        self.assertIn(c._id, ids)
        self.aether._remove_conduit_from_cluster(c, "g")
        self.assertNotIn(c._id, ids)
        # Spell registry checks
        frame._spell_registry.clear()
        spell_id = "deadbeef" * 8  # 64 hex chars like sha256
        self.assertFalse(self.aether._check_for_spell(spell_id))
        # Register set and resolve owner by spell
        frame._spell_registry.clear()
        spell_set = set([spell_id])
        self.aether._add_spells_to_aether(c._id, spell_set)
        self.assertTrue(self.aether._check_for_spell(spell_id))
        owner = self.aether._get_conduit_by_spell_id(spell_id)
        self.assertIs(owner, c)
        # Missing cluster should raise
        with self.assertRaises(ValueError):
            self.aether._add_conduit_to_cluster(c, "missing")
        with self.assertRaises(ValueError):
            self.aether._get_conduits_in_cluster("missing")
        with self.assertRaises(ValueError):
            self.aether._remove_conduit_from_cluster(c, "missing")


if __name__ == "__main__":
    unittest.main()
