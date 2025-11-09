# tests/spellbook/test_spellbook_more.py
import unittest
from unittest.mock import patch, MagicMock
from types import MappingProxyType
from uuid import uuid4, UUID

# SUT
from melder.spellbook.spellbook import Spellbook

# Real enums/types used by Spellbook
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.spell import Spell


# ----------------------- Helpers -----------------------

class DummyConfig:
    """Minimal config stub compatible with Spellbook's configuration usage."""
    def __init__(self, frame="default"):
        self._aether_frame = frame
        self._frozen = False
        self._props = {}
        self.available_properties = {
            "system_state": None,
            "debugging": None,
            "disposal": None,
            "disposal_method_names": None,
        }

    def set_property(self, k, v): self._props[k] = v
    def get_property(self, k): return self._props.get(k)
    def validate(self): return True
    def freeze(self): self._frozen = True
    def clear_properties(self): self._props.clear()
    def load_default_dictionary(self):
        self._props.setdefault("system_state", "automatic")


def make_real_spell(
        spell_id: str,
        frame,
        name: str,
        binding: str,
        perm_name: str = "create",
):
    """
    Real Spell instance without calling __init__, loaded with the fields Spellbook touches.
    """
    s = Spell.__new__(Spell)
    s.spell_id = spell_id
    s.spellframe = frame
    s.spell_name = name
    s.binding_name = binding
    s._key = (frame or name, binding or "__default__")
    perm = MagicMock()
    perm.name = perm_name
    s.permissions = perm
    s.pre_hooks = []
    s.activation_hooks = []
    s.post_hooks = []
    def _add_owned_conduit(conduit_id: UUID, conduit_name: str, creations: object):
        setattr(s, "_owner_conduit_id", conduit_id)
        setattr(s, "_owner_conduit_name", conduit_name)
        setattr(s, "_owner_creations", creations)
        setattr(s, "owned_spell", True)
        return None
    s._add_owned_conduit = _add_owned_conduit
    return s


# ================================================================
# 1) MappingProxy immutability & basic properties (6 tests)
# ================================================================

class TestMappingProxyImmutability(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_spells_proxy_is_readonly(self):
        s = make_real_spell("A", "F", "N", "B")
        self.sb._spells[s.spell_id] = s
        proxy = self.sb.spells
        self.assertIsInstance(proxy, MappingProxyType)
        with self.assertRaises(TypeError):
            proxy["X"] = s  # type: ignore[index]

    def test_contracted_spells_outer_is_readonly(self):
        cid = uuid4()
        s = make_real_spell("B", "F", "N", "B")
        self.sb._add_contracted_spell(s, cid)
        outer = self.sb.contracted_spells
        with self.assertRaises(TypeError):
            outer[cid] = {}  # type: ignore[index]

    def test_contracted_spells_inner_is_readonly(self):
        cid = uuid4()
        s = make_real_spell("C", "F", "N", "B")
        self.sb._add_contracted_spell(s, cid)
        inner = self.sb.contracted_spells[cid]
        with self.assertRaises(TypeError):
            inner["Z"] = s  # type: ignore[index]

    def test_find_counts_after_mutations(self):
        self.assertEqual(self.sb._find_spell_count(), 0)
        s = make_real_spell("D", "F", "N", "B")
        self.sb._spells[s.spell_id] = s
        self.assertEqual(self.sb._find_spell_count(), 1)
        self.assertEqual(self.sb._find_contracted_spell_count(), 0)

    def test_make_spell_key_various(self):
        self.assertEqual(self.sb._make_spell_key("Frame", "Name", None), ("Frame", "__default__"))
        self.assertEqual(self.sb._make_spell_key(None, "Name", "bind"), ("Name", "bind"))
        self.assertEqual(self.sb._make_spell_key("", "Name", ""), ("Name", "__default__"))


# ================================================================
# 2) Contract lookup helpers (4 tests)
# ================================================================

class TestContractLookupHelpers(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_find_contracted_spell_by_id_positive(self):
        cid = uuid4()
        s = make_real_spell("E", "F", "N", "B")
        self.sb._add_contracted_spell(s, cid)
        got = self.sb._find_contracted_spell_by_id("E", cid)
        self.assertIs(got, s)

    def test_find_contracted_spell_by_id_missing_conduit_returns_none(self):
        self.assertIsNone(self.sb._find_contracted_spell_by_id("E", uuid4()))

    def test_find_contracted_spell_by_id_missing_spell_returns_none(self):
        cid = uuid4()
        self.sb._create_link_contract(cid)
        self.assertIsNone(self.sb._find_contracted_spell_by_id("missing", cid))

    def test_find_contracted_spell_global_helper_positive(self):
        cid = uuid4()
        s = make_real_spell("F", "F", "N", "B")
        self.sb._add_contracted_spell(s, cid)
        self.assertIs(self.sb._find_contracted_spell("F"), s)


# ================================================================
# 3) Binding API: permissions, hooks, keys, errors (12 tests)
# ================================================================

class TestBindingMore(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()
        Spellbook._aether = MagicMock()
        Spellbook._aether._check_for_spell.return_value = False
        self.sb._bind = MagicMock()

    def _bind_one(self, frame=None, name="N", bind=None, perm="create"):
        s = make_real_spell("ID-Z", frame, name, bind, perm_name=perm)
        self.sb._bind.bind.return_value = s
        sid = self.sb.bind(
            spell=object(),
            existence=Existence.unique,
            permissions=perm,
            spellframe=frame,
            binding_name=bind,
        )
        self.assertEqual(sid, "ID-Z")
        return s

    def test_bind_permissions_accepts_strings(self):
        s = make_real_spell("ID-PS", "F", "N", "B", perm_name="read")
        self.sb._bind.bind.return_value = s
        sid = self.sb.bind(spell=object(), existence=Existence.unique, permissions="read",
                           spellframe="F", binding_name="B")
        self.assertEqual(sid, "ID-PS")
        self.assertEqual(self.sb._spells["ID-PS"].permissions.name, "read")

    def test_bind_permissions_block(self):
        s = make_real_spell("ID-BL", "F", "N", "B", perm_name="block")
        self.sb._bind.bind.return_value = s
        self.sb.bind(spell=object(), existence=Existence.unique, permissions="block",
                     spellframe="F", binding_name="B")
        self.assertEqual(self.sb._spells["ID-BL"].permissions.name, "block")

    def test_bind_rejects_noncallable_hooks_in_kwargs(self):
        s = make_real_spell("ID-HO", "F", "N", "B")
        self.sb._bind.bind.return_value = s
        with self.assertRaises(TypeError):
            self.sb.bind(spell=object(), existence=Existence.unique, permissions="create",
                         spellframe="F", binding_name="B",
                         pre_hooks=[object()])

    def test_bind_key_defaults_when_frame_and_binding_none(self):
        s = self._bind_one(frame=None, name="MySpell", bind=None)
        self.assertIn(("MySpell", "__default__"), self.sb._lookup_spells)
        self.assertEqual(self.sb._lookup_spells[("MySpell", "__default__")], s.spell_id)

    def test_bind_updates_both_maps(self):
        s = self._bind_one(frame="FF", name="NN", bind="BB")
        self.assertIn(s.spell_id, self.sb._spells)
        self.assertEqual(self.sb._lookup_spells[s._key], s.spell_id)

    def test_bind_propagates_bind_exception(self):
        self.sb._bind.bind.side_effect = RuntimeError("boom")
        with self.assertRaises(RuntimeError):
            self.sb.bind(spell=object(), existence=Existence.unique, permissions="create")

    def test_add_hooks_valid_lists(self):
        s = make_real_spell("ID-H1", "F", "N", "B")
        self.sb._add_hooks_to_spell(s, pre_hooks=[lambda: None], activation_hooks=[lambda: None], post_hooks=[lambda: None])
        self.assertEqual(len(s.pre_hooks), 1)
        self.assertEqual(len(s.activation_hooks), 1)
        self.assertEqual(len(s.post_hooks), 1)

    def test_add_hooks_rejects_non_spell(self):
        with self.assertRaises(TypeError):
            self.sb._add_hooks_to_spell(object())  # not ISpell

    def test_add_hooks_rejects_noncallables(self):
        s = make_real_spell("ID-H2", "F", "N", "B")
        with self.assertRaises(TypeError):
            self.sb._add_hooks_to_spell(s, pre_hooks=[object()])
        with self.assertRaises(TypeError):
            self.sb._add_hooks_to_spell(s, activation_hooks=[object()])
        with self.assertRaises(TypeError):
            self.sb._add_hooks_to_spell(s, post_hooks=[object()])

    def test_find_spell_after_bind(self):
        s = self._bind_one(frame="FF2", name="NN2", bind="BB2")
        self.assertIs(self.sb._find_spell(s.spell_id), s)

    def test_get_spell_permissions_positive(self):
        s = self._bind_one(perm="read")
        self.assertEqual(self.sb.get_spell_permissions(s.spell_id), "read")


# ================================================================
# 4) Configuration API extras (8 tests)
# ================================================================

class TestConfigurationMore(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_configure_partial_kwargs_only_touch_those(self):
        self.sb._configuration = DummyConfig("default")
        self.sb.configure_aether_frame(system_state="automatic", debugging=None, disposal=None, disposal_method_names=None)
        self.assertEqual(self.sb._configuration.get_property("system_state"), "automatic")
        self.assertIsNone(self.sb._configuration.get_property("debugging"))
        self.assertIsNone(self.sb._configuration.get_property("disposal"))
        self.assertIsNone(self.sb._configuration.get_property("disposal_method_names"))

    def test_configure_then_reconfigure_raises(self):
        self.sb._configuration = DummyConfig("default")
        self.sb.configure_aether_frame(system_state="automatic", debugging=True, disposal=False, disposal_method_names=["close"])
        with self.assertRaises(RuntimeError):
            self.sb.configure_aether_frame(system_state="automatic", debugging=True, disposal=False, disposal_method_names=["close"])

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=DummyConfig("frameX"))
    def test_initialize_configuration_uses_aether_when_present(self, _):
        sb = Spellbook(aetheric_frame="frameX")
        self.assertTrue(sb.is_configuration_locked())
        self.assertEqual(sb.get_configuration()._aether_frame, "frameX")

    def test_get_configuration_returns_current_object(self):
        cfg = self.sb.get_configuration()
        self.assertIs(self.sb._configuration, cfg)

    def test_create_new_preset_spellbook_returns_fresh_config_when_aether_none(self):
        cfg = DummyConfig("default")
        self.sb._configuration = cfg
        # Patch constructor path for the *new* instance to behave like normal (aether is None)
        with patch.object(Spellbook, "_get_configuration_from_aether", return_value=None):
            sb2 = self.sb.create_new_preset_spellbook()
        from melder.spellbook.configuration.configuration import Configuration
        self.assertIsInstance(sb2.get_configuration(), Configuration)
        self.assertEqual(sb2.get_configuration()._aether_frame, "default")

    def test_is_configuration_locked_initial_false(self):
        self.assertFalse(self.sb.is_configuration_locked())

    def test_configure_unknown_key_raises_and_rolls_back(self):
        self.sb._configuration = DummyConfig("default")
        self.sb._configuration.available_properties.pop("debugging")
        with self.assertRaises(KeyError):
            self.sb.configure_aether_frame(system_state="automatic", debugging=True, disposal=None, disposal_method_names=None)
        self.assertEqual(self.sb._configuration._props, {})

    def test_configure_validate_false_raises(self):
        self.sb._configuration = DummyConfig("default")
        self.sb._configuration.validate = lambda: False
        with self.assertRaises(ValueError):
            self.sb.configure_aether_frame(system_state="automatic", debugging=None, disposal=None, disposal_method_names=None)


# ================================================================
# 5) Conjure API: args, locks, duplicate protection (6 tests)
# ================================================================

class TestConjureMore(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()
        self.sb._configuration = DummyConfig("default")
        Spellbook._aether = MagicMock()

    def _stub_conduit(self):
        ctx = type("Ctx", (), {})()
        setattr(ctx, "_conduit_id", uuid4())
        conduit = type("FakeConduit", (), {})()
        conduit.__creation_context__ = ctx
        conduit._name = "C-Name"
        conduit._creations = {"x": 1}
        return conduit

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_passes_configuration_and_name_none(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        self.sb._configuration.load_default_dictionary()
        Spellbook._aether._check_for_spell.return_value = False
        c = self.sb.conjure(policy=Policies.automatic, name=None)
        self.assertIsNotNone(c)
        _, kwargs = MockConduit.call_args
        self.assertIs(kwargs["configuration"], self.sb._configuration)
        self.assertIsNone(kwargs["name"])

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_fails_when_local_spell_registered_in_aether(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        s = make_real_spell("LOC-1", "F", "N", "B")
        self.sb._spells[s.spell_id] = s
        self.sb._configuration.load_default_dictionary()
        Spellbook._aether._check_for_spell.return_value = True
        with self.assertRaises(RuntimeError):
            self.sb.conjure(policy=Policies.automatic, name="bad")

    def test_check_system_state_accepts_automatic_in_automatic(self):
        self.sb._configuration.set_property("system_state", "automatic")
        # Should not raise:
        self.sb._check_system_state(Policies.automatic)

    def test_check_system_state_rejects_non_automatic_in_automatic(self):
        self.sb._configuration.set_property("system_state", "automatic")
        with self.assertRaises(RuntimeError):
            self.sb._check_system_state(Policies.dynamic)

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_autolocks_when_unlocked(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        self.assertFalse(self.sb.is_configuration_locked())
        Spellbook._aether._check_for_spell.return_value = False
        self.sb.conjure(policy=Policies.automatic)
        self.assertTrue(self.sb.is_configuration_locked())

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_sets_policy_enum(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        self.sb._configuration.load_default_dictionary()
        Spellbook._aether._check_for_spell.return_value = False
        self.sb.conjure(policy=Policies.automatic, name="ok")
        _, kwargs = MockConduit.call_args
        self.assertIs(kwargs["policy"], Policies.automatic)


# ================================================================
# 6) Misc: inspect, set_policy_state, locks, seal placeholder (4 tests)
# ================================================================

class TestMisc(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()
        Spellbook._aether = MagicMock()

    def test_inspect_spell_uses_default_frame(self):
        self.sb._bind = MagicMock()
        self.sb._bind.spell_id_inspector.return_value = "HASH-1"
        Spellbook._aether._check_for_spell.return_value = True
        got = self.sb.inspect_spell(object())  # default frame "default"
        self.assertEqual(got, "HASH-1")
        Spellbook._aether._check_for_spell.assert_called_with("HASH-1", "default")

    def test_set_policy_state_whitelist_and_block_flags(self):
        # Initial call: whitelist_all
        self.sb._set_policy_state(Policies.whitelist_all)
        self.assertTrue(self.sb._whitelist_all_spells)
        self.assertFalse(self.sb._block_all_spells)
        # Flip: block_all
        self.sb._set_policy_state(Policies.block_all)
        self.assertTrue(self.sb._block_all_spells)
        self.assertFalse(self.sb._whitelist_all_spells)

    def test_make_spell_key_under_lock_reentrancy(self):
        with self.sb._lock:
            k = self.sb._make_spell_key("F", "N", "B")
            self.assertEqual(k, ("F", "B"))

    def test_seal_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.sb.seal()


# -----------------------
# Total tests: 40
# -----------------------

if __name__ == "__main__":
    unittest.main()
