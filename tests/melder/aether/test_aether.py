import unittest
import uuid
from src.melder.aether.aether import Aether
from src.melder.aether.aetheric_frame import AethericFrame


class _StubCloud:
    def __init__(self):
        self.registered = []

    def _register_conduit(self, conduit):
        self.registered.append(conduit)


class _DummyCtx:
    def __init__(self, cid=None):
        self._conduit_id = cid or uuid.uuid4()


class _DummyConduit:
    def __init__(self, name="c", cid=None):
        self.name = name
        self.__creation_context__ = _DummyCtx(cid)


class TestAether(unittest.TestCase):
    def setUp(self):
        # Always start fresh
        a = Aether()
        a._reset_for_testing()
        self.aether = Aether()
        # sanity: default frame present
        self.assertIsInstance(self.aether._default_frame, AethericFrame)

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
    def test_seal_idempotent_and_flags(self):
        self.assertFalse(self.aether._sealed)
        self.aether.seal()
        self.assertTrue(self.aether._sealed)
        self.assertIsNone(self.aether._default_frame)
        # second seal should not raise or change anything
        self.aether.seal()
        self.assertTrue(self.aether._sealed)

    # 4
    def test_seal_calls_frame_seal_even_on_exception(self):
        class _BadFrame(AethericFrame):
            def seal(self):
                raise RuntimeError("boom")

        # Inject a bad frame next to default
        self.aether._aetheric_frames["bad"] = _BadFrame("bad")
        # Should not raise
        self.aether.seal()

    # 5
    def test_reset_for_testing_resets_singleton(self):
        self.aether.seal()
        self.aether._reset_for_testing()
        self.assertIsNone(Aether._instance)
        self.assertFalse(Aether._initialized)

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
        cid = c.__creation_context__._conduit_id
        self.assertIn(cid, self.aether._default_frame._conduits)
        self.assertIs(self.aether._default_frame._conduits[cid], c)

    # 12
    def test_add_conduit_duplicate_raises(self):
        c = _DummyConduit("dup", cid=uuid.uuid4())
        self.aether._default_frame._conduits.clear()
        self.aether._default_frame._conduits[c.__creation_context__._conduit_id] = c
        with self.assertRaises(ValueError):
            self.aether._add_conduit(c)

    # 13
    def test_remove_conduit_success(self):
        c = _DummyConduit("gone", cid=uuid.uuid4())
        self.aether._default_frame._conduits.clear()
        self.aether._default_frame._conduits[c.__creation_context__._conduit_id] = c
        self.aether._remove_conduit(c)
        self.assertNotIn(c.__creation_context__._conduit_id, self.aether._default_frame._conduits)

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
        self.aether._default_frame._conduits[c1.__creation_context__._conduit_id] = c1
        self.aether._default_frame._conduits[c2.__creation_context__._conduit_id] = c2
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
        self.aether._default_frame._conduits[c.__creation_context__._conduit_id] = c
        got = self.aether._get_conduit_by_id(c.__creation_context__._conduit_id)
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
        frame._conduits[c.__creation_context__._conduit_id] = c
        # Add/remove in cluster
        self.aether._add_conduit_to_cluster(c, "g")
        ids = self.aether._get_conduits_in_cluster("g")
        self.assertIn(c.__creation_context__._conduit_id, ids)
        self.aether._remove_conduit_from_cluster(c, "g")
        self.assertNotIn(c.__creation_context__._conduit_id, ids)
        # Spell registry checks
        frame._spell_registry.clear()
        spell_id = "deadbeef" * 8  # 64 hex chars like sha256
        self.assertFalse(self.aether._check_for_spell(spell_id))
        # Register set and resolve owner by spell
        frame._spell_registry.clear()
        spell_set = set([spell_id])
        self.aether._add_spells_to_aether(c.__creation_context__._conduit_id, spell_set)
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
