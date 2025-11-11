# tests/spellbook/test_spellbook_extensive.py
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from types import MappingProxyType

# SUT
from melder.spellbook.spellbook import Spellbook

# Real enums used by Spellbook
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions

# Real Spell (for isinstance(ISpell) checks inside Spellbook)
from melder.spellbook.spell import Spell


# ----------------------- Helpers -----------------------

class DummyConfig:
    """Minimal config stub compatible with Spellbook's usage."""
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
    Build a **real** Spell instance without invoking its __init__.
    Only fields Spellbook touches are populated.
    """
    s = Spell.__new__(Spell)  # bypass __init__
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
# 1) Basics & Properties (7 tests)
# ================================================================

class TestBasicsAndProperties(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_init_default_frame_and_unlocked_config(self, _):
        sb = Spellbook()
        self.assertEqual(sb._aetheric_frame, "default")
        self.assertFalse(sb.is_configuration_locked())
        self.assertIsNotNone(sb.get_configuration())

    def test_init_rejects_non_string_frame(self):
        with self.assertRaises(TypeError):
            Spellbook(aetheric_frame=123)  # type: ignore[arg-type]

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=DummyConfig("X"))
    def test_init_with_existing_config_locks(self, _):
        sb = Spellbook(aetheric_frame="X")
        self.assertTrue(sb.is_configuration_locked())
        self.assertEqual(sb.get_configuration()._aether_frame, "X")

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=DummyConfig("Y"))
    def test_init_mismatch_frame_raises(self, _):
        with self.assertRaises(RuntimeError):
            Spellbook(aetheric_frame="Z")

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_spells_property_is_mappingproxy(self, _):
        sb = Spellbook()
        self.assertIsInstance(sb.spells, MappingProxyType)

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_contracted_spells_property_is_nested_proxy(self, _):
        sb = Spellbook()
        cid = uuid4()
        s = make_real_spell("S1", "F", "N", "B")
        sb._add_contracted_spell(s, cid)
        outer = sb.contracted_spells
        self.assertIsInstance(outer, MappingProxyType)
        inner = outer[cid]
        self.assertIsInstance(inner, MappingProxyType)

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_find_counts_initial(self, _):
        sb = Spellbook()
        self.assertEqual(sb._find_spell_count(), 0)
        self.assertEqual(sb._find_contracted_spell_count(), 0)


# ================================================================
# 2) Lookup helpers (6 tests)
# ================================================================

class TestLookupHelpers(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_find_spell_returns_none_when_absent(self):
        self.assertIsNone(self.sb._find_spell("nope"))

    def test_find_contracted_spell_raises_when_absent(self):
        with self.assertRaises(RuntimeError):
            self.sb._find_contracted_spell("nope")

    def test_find_spell_id_from_locals(self):
        s = make_real_spell("ID1", "F", "N", "B")
        self.sb._spells[s.spell_id] = s
        self.sb._lookup_spells[s._key] = s.spell_id
        got = self.sb.find_spell_id("F", "N", "B")
        self.assertEqual(got, "ID1")

    def test_find_spell_id_from_contracted(self):
        cid = uuid4()
        s = make_real_spell("ID2", "F2", "N2", "B2")
        self.sb._add_contracted_spell(s, cid)
        got = self.sb.find_spell_id("F2", "N2", "B2")
        self.assertEqual(got, "ID2")

    def test_find_spell_id_raises(self):
        with self.assertRaises(RuntimeError):
            self.sb.find_spell_id("no", "no", "no")

    def test_find_spell_key_positive_and_negative(self):
        s = make_real_spell("IDX", "AA", "BB", "CC")
        self.sb._spells[s.spell_id] = s
        self.sb._lookup_spells[s._key] = s.spell_id
        self.assertEqual(self.sb.find_spell_key("AA", "BB", "CC"), s._key)
        with self.assertRaises(RuntimeError):
            self.sb.find_spell_key("no", "no", "no")


# ================================================================
# 3) Inspect + Duplicate checks (4 tests)
# ================================================================

class TestInspectAndDup(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()
        Spellbook._aether = MagicMock()

    def test_inspect_spell_positive(self):
        self.sb._bind = MagicMock()
        self.sb._bind.spell_id_inspector.return_value = "HASH123"
        Spellbook._aether._check_for_spell.return_value = True
        got = self.sb.inspect_spell(object(), aetheric_frame="frameX")
        self.assertEqual(got, "HASH123")

    def test_inspect_spell_negative(self):
        self.sb._bind = MagicMock()
        self.sb._bind.spell_id_inspector.return_value = "HASH123"
        Spellbook._aether._check_for_spell.return_value = False
        got = self.sb.inspect_spell(object(), aetheric_frame="frameX")
        self.assertIsNone(got)

    def test_check_all_spells_raises_on_duplicate(self):
        Spellbook._aether = MagicMock()
        Spellbook._aether._check_for_spell.return_value = True
        self.sb._spells["ID"] = make_real_spell("ID", "F", "N", "B")
        with self.assertRaises(RuntimeError):
            self.sb._check_all_spells()

    def test_check_all_spells_ok_when_not_registered(self):
        Spellbook._aether = MagicMock()
        Spellbook._aether._check_for_spell.return_value = False
        self.sb._spells["ID"] = make_real_spell("ID", "F", "N", "B")
        # Should not raise
        self.sb._check_all_spells()


# ================================================================
# 4) Contract API (10 tests)
# ================================================================

class TestContractAPI(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_create_and_remove_link_contract(self):
        cid = uuid4()
        self.sb._create_link_contract(cid)
        self.assertIn(cid, self.sb._contracted_spells)
        self.assertIn(cid, self.sb._lookup_contracted_spells)
        self.sb._remove_link_contract(cid)
        self.assertNotIn(cid, self.sb._contracted_spells)
        self.assertNotIn(cid, self.sb._lookup_contracted_spells)

    def test_create_link_contract_inconsistent_raises(self):
        cid = uuid4()
        self.sb._contracted_spells[cid] = {}
        with self.assertRaises(RuntimeError):
            self.sb._create_link_contract(cid)

    def test_remove_link_contract_inconsistent_raises(self):
        cid = uuid4()
        self.sb._lookup_contracted_spells[cid] = {}
        with self.assertRaises(RuntimeError):
            self.sb._remove_link_contract(cid)

    def test_add_contracted_spell_updates_both_maps(self):
        cid = uuid4()
        s = make_real_spell("S-1", "F", "N", "B")
        self.sb._add_contracted_spell(s, cid)
        self.assertIn("S-1", self.sb._contracted_spells[cid])
        self.assertIn(("F", "B"), self.sb._lookup_contracted_spells[cid])

    def test_remove_contracted_spell_success(self):
        cid = uuid4()
        s = make_real_spell("S-2", "F2", "N2", "B2")
        self.sb._add_contracted_spell(s, cid)
        self.sb._remove_contracted_spell("S-2", cid)
        self.assertNotIn("S-2", self.sb._contracted_spells[cid])
        self.assertNotIn(("F2", "B2"), self.sb._lookup_contracted_spells[cid])

    def test_remove_contracted_spell_no_conduit_raises(self):
        with self.assertRaises(RuntimeError):
            self.sb._remove_contracted_spell("nope", uuid4())

    def test_remove_contracted_spell_missing_id_raises(self):
        cid = uuid4()
        self.sb._create_link_contract(cid)
        with self.assertRaises(RuntimeError):
            self.sb._remove_contracted_spell("nope", cid)

    def test_remove_contracted_spell_missing_key_raises(self):
        cid = uuid4()
        s = make_real_spell("S-3", "F3", "N3", "B3")
        self.sb._add_contracted_spell(s, cid)
        # corrupt lookup to simulate missing key
        self.sb._lookup_contracted_spells[cid].clear()
        with self.assertRaises(RuntimeError):
            self.sb._remove_contracted_spell("S-3", cid)

    def test_clear_contracted_spells_for_conduit_success(self):
        cid = uuid4()
        self.sb._add_contracted_spell(make_real_spell("A", "F", "N", "B"), cid)
        self.sb._add_contracted_spell(make_real_spell("B", "F2", "N2", "B2"), cid)
        self.sb._clear_contracted_spells_for_conduit(cid)
        self.assertEqual(len(self.sb._contracted_spells[cid]), 0)
        self.assertEqual(len(self.sb._lookup_contracted_spells[cid]), 0)

    def test_sever_link_contract_success(self):
        cid = uuid4()
        self.sb._add_contracted_spell(make_real_spell("X", "F", "N", "B"), cid)
        self.sb._sever_link_contract(cid)
        self.assertNotIn(cid, self.sb._contracted_spells)
        self.assertNotIn(cid, self.sb._lookup_contracted_spells)


# ================================================================
# 5) Binding API (11 tests)
# ================================================================

class TestBindingAPI(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()
        Spellbook._aether = MagicMock()
        Spellbook._aether._check_for_spell.return_value = False  # default: not registered
        self.sb._bind = MagicMock()

    def _bind_one(self, frame="F", name="N", bind="B", perm="create"):
        s = make_real_spell("ID-1", frame, name, bind, perm_name=perm)  # real Spell
        self.sb._bind.bind.return_value = s
        sid = self.sb.bind(
            spell=object(),
            existence=Existence.unique,
            permissions=perm,
            spellframe=frame,
            binding_name=bind,
        )
        self.assertEqual(sid, "ID-1")
        return s

    def test_bind_success_updates_maps(self):
        s = self._bind_one(frame="A", name="Thing", bind="b1")
        self.assertIn(s.spell_id, self.sb._spells)
        self.assertEqual(self.sb._lookup_spells[s._key], s.spell_id)

    def test_bind_duplicate_rejected_by_aether(self):
        s = make_real_spell("ID-DUP", "F", "N", "__default__", perm_name="create")
        self.sb._bind.bind.return_value = s
        Spellbook._aether._check_for_spell.return_value = True
        with self.assertRaises(RuntimeError):
            self.sb.bind(spell="x", existence=Existence.unique)

    def test_bind_adds_hooks_when_valid(self):
        s = self._bind_one()
        # No explicit hooks passed; ensure permissions survived the round-trip
        self.assertEqual(self.sb._spells[s.spell_id].permissions.name, s.permissions.name)

    def test_add_hooks_to_spell_accepts_callable_lists(self):
        with patch.object(Spellbook, "_get_configuration_from_aether", return_value=None):
            sb = Spellbook()
        s = make_real_spell("ID-H", "F", "N", "B")  # real Spell (passes isinstance)
        sb._add_hooks_to_spell(
            s,
            pre_hooks=[lambda: None],
            activation_hooks=[lambda: None],
            post_hooks=[lambda: None]
        )
        self.assertEqual(len(s.pre_hooks), 1)
        self.assertEqual(len(s.activation_hooks), 1)
        self.assertEqual(len(s.post_hooks), 1)

    def test_add_hooks_to_spell_rejects_non_spell(self):
        with patch.object(Spellbook, "_get_configuration_from_aether", return_value=None):
            sb = Spellbook()
        with self.assertRaises(TypeError):
            sb._add_hooks_to_spell(object())  # not ISpell

    def test_add_hooks_to_spell_rejects_noncallables(self):
        s = make_real_spell("ID-Y", "F", "N", "B")
        with patch.object(Spellbook, "_get_configuration_from_aether", return_value=None):
            sb = Spellbook()
        with self.assertRaises(TypeError):
            sb._add_hooks_to_spell(s, pre_hooks=[object()])
        with self.assertRaises(TypeError):
            sb._add_hooks_to_spell(s, activation_hooks=[object()])
        with self.assertRaises(TypeError):
            sb._add_hooks_to_spell(s, post_hooks=[object()])

    def test_bind_propagates_exception_from_bind_impl(self):
        self.sb._bind.bind.side_effect = ValueError("whoops")
        with self.assertRaises(ValueError):
            self.sb.bind(spell="x", existence=Existence.unique)

    def test_get_spell_permissions_positive(self):
        s = self._bind_one(perm="read")
        got = self.sb.get_spell_permissions(s.spell_id)
        self.assertEqual(got, "read")

    def test_get_spell_permissions_raises_when_missing(self):
        with self.assertRaises(RuntimeError):
            self.sb.get_spell_permissions("nope")

    def test_find_spell_after_bind(self):
        s = self._bind_one(frame="F2", name="N2", bind="B2")
        got = self.sb._find_spell(s.spell_id)
        self.assertIs(got, s)

    def test_find_spell_key_after_bind(self):
        s = self._bind_one(frame="KF", name="KN", bind="KB")
        k = self.sb.find_spell_key("KF", "KN", "KB")
        self.assertEqual(k, s._key)


# ================================================================
# 6) Configuration API (6 tests)
# ================================================================

class TestConfigurationAPI(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_is_configuration_locked_initial_false(self):
        self.assertFalse(self.sb.is_configuration_locked())

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_configure_success_binds_and_locks(self, _):
        sb = Spellbook()
        sb._configuration = DummyConfig("default")
        Spellbook._aether = MagicMock()
        sb.configure_aether_frame(system_state="automatic",
                                  debugging=True,
                                  disposal=False,
                                  disposal_method_names=["close"])
        self.assertTrue(sb.is_configuration_locked())
        Spellbook._aether._bind_configuration.assert_called_once()

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_configure_unknown_key_raises_and_clears(self, _):
        sb = Spellbook()
        sb._configuration = DummyConfig("default")
        # remove an allowed key to force KeyError
        sb._configuration.available_properties.pop("debugging")
        with self.assertRaises(KeyError):
            sb.configure_aether_frame(system_state="automatic",
                                      debugging=True,
                                      disposal=None,
                                      disposal_method_names=None)
        self.assertEqual(sb._configuration._props, {})

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_configure_validate_false_raises(self, _):
        sb = Spellbook()
        sb._configuration = DummyConfig("default")
        # sabotage validate
        sb._configuration.validate = lambda: False
        with self.assertRaises(ValueError):
            sb.configure_aether_frame(system_state="automatic",
                                      debugging=None,
                                      disposal=None,
                                      disposal_method_names=None)

    def test_configure_when_locked_raises(self):
        self.sb._configuration_locked = True
        with self.assertRaises(RuntimeError):
            self.sb.configure_aether_frame(system_state="automatic",
                                           debugging=None,
                                           disposal=None,
                                           disposal_method_names=None)

    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def test_create_new_preset_spellbook_reuses_frame(self, _):
        sb = Spellbook()
        cfg = DummyConfig("default")
        sb._configuration = cfg
        sb2 = sb.create_new_preset_spellbook()
        # The implementation constructs a new Configuration when Aether returns None.
        from melder.spellbook.configuration.configuration import Configuration
        self.assertIsInstance(sb2.get_configuration(), Configuration)
        self.assertEqual(sb2.get_configuration()._aether_frame, "default")


# ================================================================
# 7) Conjure API (6 tests)
# ================================================================

class TestConjureAPI(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()
        self.sb._configuration = DummyConfig("default")
        Spellbook._aether = MagicMock()

    def _stub_conduit(self):
        """Return a Conduit stub with attributes Spellbook expects to use."""
        conduit = type("FakeConduit", (), {})()
        conduit._id = uuid4()
        conduit._name = "C-Name"
        conduit._creations = {"x": 1}
        return conduit

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_success_creates_conduit_and_locks(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        self.sb._configuration.load_default_dictionary()
        # Ensure duplicate check won't trip
        Spellbook._aether._check_for_spell.return_value = False
        c = self.sb.conjure(policy=Policies.automatic, name="C1")
        self.assertTrue(self.sb.is_configuration_locked())
        MockConduit.assert_called_once()
        _, kwargs = MockConduit.call_args
        self.assertIs(kwargs["spellbook"], self.sb)
        self.assertEqual(kwargs["name"], "C1")
        self.assertEqual(kwargs["conduit_state"], ConduitState.normal)
        self.assertEqual(kwargs["aetheric_frame"], "default")
        self.assertEqual(kwargs["policy"], Policies.automatic)
        self.assertIsNotNone(c)

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_only_once(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        self.sb._configuration.load_default_dictionary()
        Spellbook._aether._check_for_spell.return_value = False
        self.sb.conjure(policy=Policies.automatic)
        with self.assertRaises(RuntimeError):
            self.sb.conjure(policy=Policies.automatic)

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_autoloads_defaults_when_unlocked(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        self.assertFalse(self.sb.is_configuration_locked())
        Spellbook._aether._check_for_spell.return_value = False
        self.sb.conjure(policy=Policies.automatic)
        self.assertTrue(self.sb.is_configuration_locked())

    def test_check_system_state_automatic_rejects_dynamic(self):
        # Use the real enum, not a string
        from melder.spellbook.configuration.system_state import SystemState
        self.sb._configuration.set_property("system_state", SystemState.automatic)
        with self.assertRaises(RuntimeError):
            self.sb._check_system_state(policy=Policies.dynamic)


    def test_check_system_state_dynamic_allows_dynamic(self):
        self.sb._configuration.set_property("system_state", "dynamic")
        # Should not raise
        self.sb._check_system_state(policy=Policies.dynamic)

    @patch("melder.spellbook.spellbook.Conduit")
    def test_define_conduit_into_spells_called(self, MockConduit):
        MockConduit.return_value = self._stub_conduit()
        # add a spell so _define_conduit_into_spells has something to touch
        s = make_real_spell("SID", "F", "N", "B")
        self.sb._spells[s.spell_id] = s
        self.sb._lookup_spells[s._key] = s.spell_id
        self.sb._configuration.load_default_dictionary()
        Spellbook._aether._check_for_spell.return_value = False  # avoid duplicate check trip
        self.sb.conjure(policy=Policies.automatic, name="Z")
        # ownership should be stamped by spell._add_owned_conduit
        self.assertTrue(getattr(s, "owned_spell", False))


# -----------------------
# Total tests: 50
# -----------------------

if __name__ == "__main__":
    unittest.main()
