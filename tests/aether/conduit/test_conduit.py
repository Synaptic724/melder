# tests/test_conduit_unittest.py
import unittest
from unittest.mock import patch
from uuid import uuid4, UUID
import types

# SUT
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies


# ------------------- Fakes / Test Doubles -------------------

class FakeConfig:
    def __init__(self, system_state="dynamic", debugging=False, disposal=True, disposal_method_names=None):
        self._props = {
            "system_state": system_state,
            "debugging": debugging,
            "disposal": disposal,
            "disposal_method_names": disposal_method_names or ["close", "dispose", "shutdown"],
        }

    def get_property(self, name):
        return self._props.get(name)


class FakeSpell:
    def __init__(self, permissions_name="create"):
        self.permissions = types.SimpleNamespace(name=permissions_name)


class FakeSpellbook:
    def __init__(self, initial_spells=None):
        self._spells = dict(initial_spells or {})

    def _find_spell(self, spell_id):
        return self._spells.get(spell_id)

    def _find_contracted_spell(self, spell_id):
        return self._spells.get(spell_id)

    def find_spell_id(self, spellframe, spell_name, binding_name):
        key = (spellframe, spell_name, binding_name)
        return f"{spellframe}:{spell_name}:{binding_name}" if key in self._spells else None

    def find_spell_key(self, spellframe, spell_name, binding_name):
        key = (spellframe, spell_name, binding_name)
        return key if key in self._spells else None

    def inspect_spell(self, spell, aetheric_frame="default"):
        for k, v in self._spells.items():
            if v is spell:
                # When added via string key, also mirror tuple key
                return k if isinstance(k, str) else f"{k[0]}:{k[1]}:{k[2]}"
        return None

    def bind(self, *, spell, existence, spellframe=None, binding_name=None, permissions="create", **kwargs):
        sid = f"{spellframe}:{getattr(spell, '__name__', str(spell))}:{binding_name}"
        if sid in self._spells:
            raise RuntimeError("Already bound")
        self._spells[(spellframe, getattr(spell, '__name__', str(spell)), binding_name)] = FakeSpell(permissions)
        return sid

    def create_new_preset_spellbook(self):
        return None

    def seal(self):
        return None


class FakeConduitCloud:
    def __init__(self):
        self.registered = []

    def _register_conduit(self, conduit):
        self.registered.append(conduit)


class FakeAether:
    def __init__(self):
        self.added_conduits = []
        self.spells_added = []
        self.conduits_by_id = {}
        self.conduits_by_name = {}
        self.clouds = {"default": FakeConduitCloud()}
        self.register_cloud_calls = []

    @property
    def sealed(self):
        return False

    def _add_conduit(self, conduit, frame):
        self.added_conduits.append((conduit, frame))
        cid = conduit.__creation_context__._conduit_id
        if cid:
            self.conduits_by_id[cid] = conduit
        if conduit.name:
            self.conduits_by_name[(conduit.name, frame)] = conduit

    def _remove_conduit(self, conduit, frame):
        self.added_conduits = [(c, f) for (c, f) in self.added_conduits if not (c is conduit and f == frame)]

    def _add_spells_to_aether(self, conduit_id, spell_set, frame):
        self.spells_added.append((conduit_id, tuple(sorted(list(spell_set))), frame))

    def _get_conduit_by_spell_id(self, spell_id, frame):
        for c, f in self.added_conduits:
            if f == frame and getattr(c, "_spellbook", None) and c._spellbook._find_spell(spell_id):
                return c
        return None

    def _check_for_spell(self, spell_id, frame):
        return self._get_conduit_by_spell_id(spell_id, frame) is not None

    def _get_conduit_cloud(self, frame):
        return self.clouds.setdefault(frame, FakeConduitCloud())

    def _get_conduit_by_id(self, conduit_id, frame):
        return self.conduits_by_id.get(conduit_id)

    def _get_conduit_by_name(self, name, frame):
        return self.conduits_by_name.get((name, frame))

    def _register_conduit_cloud(self, conduit, frame):
        self.register_cloud_calls.append((conduit, frame))
        self._get_conduit_cloud(frame)._register_conduit(conduit)


class FakeConduitWard:
    def __init__(self, owner, dynamic, state, policy):
        self.owner = owner
        self.dynamic = dynamic
        self.state = state
        self.policy = policy
        self.links = []
        self.lesser = {}
        self.initiated = {}
        self.provider = {}
        self.converted = False
        self.sealed_children = False

    def _link(self, target):
        self.links.append(target)
        return True

    def _sever_link(self, target):
        if target in self.links:
            self.links.remove(target)
            return True
        return False

    def _get_links(self):
        return list(self.links)

    def _get_lesser_conduit(self, cid):
        return self.lesser.get(cid)

    def _get_initiated_conduit(self, cid):
        return self.initiated.get(cid)

    def _get_provider_conduit(self, cid):
        return self.provider.get(cid)

    def _get_initiated_conduits(self):
        return list(self.initiated.values())

    def _get_provider_conduits(self):
        return list(self.provider.values())

    def seal_all_lesser_conduits(self):
        self.sealed_children = True

    def _convert_to_normal_conduit(self):
        self.converted = True

    # Contract ops (simple stubs)
    def _add_spell_to_contract(self, **kwargs):
        return True

    def _add_spells_to_contract(self, **kwargs):
        sids = kwargs.get("spell_ids", [])
        return {sid: True for sid in sids}

    def _remove_spell_from_contract(self, **kwargs):
        return True

    def _remove_spells_from_contract(self, **kwargs):
        sids = kwargs.get("spell_ids") or []
        return {sid: True for sid in sids}

    def _remove_all_spells_from_contract(self, **kwargs):
        return True

    def _get_all_spells_in_contracts(self, validate=True):
        return {}

    def _get_spell_in_contracts(self, spell_id):
        return None

    def _get_spells_in_contract_by_conduit(self, conduit_id):
        return {}

    def _get_spells_in_contract_by_conduit_name(self, conduit_name):
        return {}

    def _get_contracted_conduits(self):
        return []

    def _describe_contract(self, conduit_id):
        return {"conduit_id": conduit_id, "spells": [], "permissions": []}

    def _validate_contracts_and_define(self):
        return {}

    def _validate_received_contracts(self):
        return True


# ------------------- Test Case -------------------

class TestConduit(unittest.TestCase):
    def setUp(self):
        # Patch ConduitWard class used by Conduit
        self.patcher_ward = patch(
            "melder.aether.conduit.conduit_ward.conduit_ward.ConduitWard",
            FakeConduitWard,
        )
        self.patcher_ward.start()

        # Fresh FakeAether per test
        self.fake_aether = FakeAether()
        Conduit._aether = self.fake_aether

    def tearDown(self):
        self.patcher_ward.stop()

    def _spellbook_with_one(self):
        fb = FakeSpellbook()
        # mirror both string and tuple key presence (your code reads ._spells.keys())
        fake = FakeSpell("create")
        fb._spells["frame:Foo:bar"] = fake
        fb._spells[("frame", "Foo", "bar")] = fake
        return fb

    # 1
    def test_init_normal_adds_to_aether(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C1")
        self.assertIn((c, "default"), self.fake_aether.added_conduits)

    # 2
    def test_init_lesser_clears_name_and_no_cloud_register(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.lesser, "default", Policies.lesser_conduit, name="X")
        self.assertIsNone(c.name)
        self.assertEqual(self.fake_aether.register_cloud_calls, [])

    # 3
    def test_dynamic_named_normal_registers_cloud(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C2")
        self.assertEqual(self.fake_aether.register_cloud_calls, [(c, "default")])
        self.assertIn(c, self.fake_aether._get_conduit_cloud("default").registered)

    # 4
    def test_normal_without_name_not_registered_cloud(self):
        Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name=None)
        self.assertEqual(self.fake_aether.register_cloud_calls, [])

    # 5
    def test_flags_automatic_sets_dynamic_false(self):
        c = Conduit(FakeSpellbook(), FakeConfig("automatic"), ConduitState.normal, "default", Policies.normal_conduit)
        self.assertFalse(c._Conduit__dynamic_environment__)

    # 6
    def test_flags_dynamic_sets_dynamic_true(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit)
        self.assertTrue(c._Conduit__dynamic_environment__)

    # 7
    def test_debug_flag_sets_debugger_mode(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic", debugging=True), ConduitState.normal, "default", Policies.normal_conduit)
        self.assertTrue(c._Conduit__debugger_mode__)

    # 8
    def test_add_spells_to_aether_on_init(self):
        sb = self._spellbook_with_one()
        Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C3")
        self.assertEqual(len(self.fake_aether.spells_added), 1)
        cid, keys, frame = self.fake_aether.spells_added[0]
        self.assertEqual(frame, "default")
        self.assertIsInstance(cid, str)

    # 9
    def test_name_property_none_when_missing(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit)
        self.assertIsNone(c.name)

    # 10
    def test_name_setter_only_once(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit)
        c.name = "X"
        with self.assertRaises(RuntimeError):
            c.name = "Y"

    # 11
    def test_register_conduit_cloud_raises_when_not_dynamic(self):
        c = Conduit(FakeSpellbook(), FakeConfig("automatic"), ConduitState.normal, "default", Policies.normal_conduit)
        with self.assertRaises(RuntimeError):
            c.register_conduit_cloud(c)

    # 12
    def test_register_conduit_cloud_raises_for_lesser(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.lesser, "default", Policies.lesser_conduit)
        with self.assertRaises(RuntimeError):
            c.register_conduit_cloud(c)

    # 13
    def test_register_conduit_cloud_raises_when_name_missing(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit)
        with self.assertRaises(RuntimeError):
            c.register_conduit_cloud(c)

    # 14
    def test_register_conduit_cloud_calls_aether(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C4")
        c.register_conduit_cloud(c)
        self.assertEqual(self.fake_aether.register_cloud_calls[-1], (c, "default"))

    # 15
    def test_add_conduit_to_aether_raises_when_global_aether_none(self):
        # Temporarily break the class-level aether
        prev = Conduit._aether
        Conduit._aether = None
        try:
            with self.assertRaises(RuntimeError):
                Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C5")
        finally:
            Conduit._aether = prev

    # 16
    def test_get_conduit_by_spell_id(self):
        sb = self._spellbook_with_one()
        c = Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C6")
        found = c.get_conduit_by_spell_id("frame:Foo:bar", "default")
        self.assertIs(found, c)

    # 17
    def test_check_spell_id_true(self):
        sb = self._spellbook_with_one()
        c = Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C7")
        self.assertTrue(c.check_spell_id("frame:Foo:bar", "default"))

    # 18
    def test_get_spell_by_id(self):
        sb = self._spellbook_with_one()
        c = Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C8")
        self.assertIs(c.get_spell_by_id("frame:Foo:bar"), sb._spells["frame:Foo:bar"])

    # 19
    def test_find_spell_id_found(self):
        sb = self._spellbook_with_one()
        c = Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C9")
        sid = c.find_spell_id("frame", "Foo", "bar")
        self.assertIsInstance(sid, str)

    # 20
    def test_find_spell_id_missing_raises(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C10")
        with self.assertRaises(ValueError):
            c.find_spell_id("frame", "Nope", "bar")

    # 21
    def test_find_spell_key_found(self):
        sb = self._spellbook_with_one()
        c = Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C11")
        self.assertEqual(c.find_spell_key("frame", "Foo", "bar"), ("frame", "Foo", "bar"))

    # 22
    def test_find_spell_key_missing_raises(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C12")
        with self.assertRaises(ValueError):
            c.find_spell_key("frame", "Nope", "bar")

    # 23
    def test_inspect_spell_passthrough(self):
        sb = self._spellbook_with_one()
        c = Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C13")
        any_spell = sb._spells["frame:Foo:bar"]
        self.assertEqual(c.inspect_spell(any_spell), "frame:Foo:bar")

    # 24
    def test_bind_only_allowed_for_normal(self):
        lesser = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.lesser, "default", Policies.lesser_conduit)
        with self.assertRaises(RuntimeError):
            lesser.bind(spell=object, existence="unique")

    # 25
    def test_bind_delegates_to_spellbook(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C14")
        sid = c.bind(spell=lambda: None, existence="unique", spellframe="frame", binding_name="baz")
        self.assertIsInstance(sid, str)

    # 26
    def test_get_spell_permissions_returns_value(self):
        sb = self._spellbook_with_one()
        c = Conduit(sb, FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C15")
        p = c.get_spell_permissions("frame:Foo:bar")
        self.assertIn(p, ("create", "read", "block"))

    # 27
    def test_get_spell_permissions_missing_raises(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C16")
        with self.assertRaises(RuntimeError):
            c.get_spell_permissions("nope")

    # 28
    def test_get_conduit_cloud_raises_when_dynamic_enabled(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C17")
        with self.assertRaises(RuntimeError):
            c.get_conduit_cloud()

    # 29
    def test_get_conduit_cloud_returns_cloud_when_automatic(self):
        c = Conduit(FakeSpellbook(), FakeConfig("automatic"), ConduitState.normal, "default", Policies.normal_conduit, name="C18")
        cloud = c.get_conduit_cloud()
        self.assertIsInstance(cloud, FakeConduitCloud)

    # 30
    def test_link_and_sever_link(self):
        c1 = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C19")
        c2 = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C20")
        self.assertTrue(c1.link(c2))
        self.assertEqual(c1.get_links(), [c2])
        self.assertTrue(c1.sever_link(c2))
        self.assertEqual(c1.get_links(), [])

    # 31
    def test_upgrade_to_normal_converts_and_registers(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.lesser, "default", Policies.lesser_conduit)
        c.upgrade_to_normal(name="UP")
        self.assertEqual(c._conduit_state, ConduitState.normal)
        self.assertEqual(self.fake_aether.register_cloud_calls[-1], (c, "default"))

    # 32
    def test_seal_lesser_conduits_calls_ward(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C21")
        c.seal_lesser_conduits()
        self.assertTrue(c._conduit_ward.sealed_children)

    # 33
    def test_contract_qualification_passes_for_normal_dynamic(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C22")
        # Should not raise:
        c._qualify_contracts()

    # 34
    def test_contract_methods_delegate_shapes(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C23")
        self.assertTrue(c.add_spell_to_contract(spell_id="X", conduit=c))
        self.assertEqual(c.add_spells_to_contract(["A","B"], conduit=c), {"A": True, "B": True})
        self.assertTrue(c.remove_spell_from_contract(spell_id="X", conduit=c))
        self.assertEqual(c.remove_spells_from_contract(spell_ids=["A","B"], conduit=c), {"A": True, "B": True})
        self.assertTrue(c._remove_all_spells_from_contract(conduit=c))
        self.assertEqual(c.get_all_spells_in_contracts(), {})
        self.assertIsNone(c.get_spell_in_contracts("Z"))
        self.assertEqual(c.get_spells_in_contract_by_conduit(uuid4()), {})
        self.assertEqual(c.get_spells_in_contract_by_conduit_name("name"), {})
        self.assertEqual(c.get_contracted_conduits(), [])
        self.assertIsInstance(c._describe_contract(uuid4()), dict)

    # 35
    def test_get_conduit_by_id_passthrough(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C24")
        cid = c.__creation_context__._conduit_id
        self.assertIs(c.get_conduit_by_id(cid, "default"), c)

    # 36
    def test_get_conduit_by_name_passthrough(self):
        c = Conduit(FakeSpellbook(), FakeConfig("dynamic"), ConduitState.normal, "default", Policies.normal_conduit, name="C25")
        self.assertIs(c.get_conduit_by_name("C25", "default"), c)


if __name__ == "__main__":
    unittest.main()
