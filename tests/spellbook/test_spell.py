# tests/spellbook/test_spell.py
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID

# System under test
from melder.spellbook.spellbook import Spellbook

# Real types we’ll use (no patching)
from melder.spellbook.spell import Spell
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies


# ----------------------- Helpers -----------------------

def make_real_spell(
        spell_id: str,
        frame: str,
        name: str,
        binding: str,
        perm_name: str = "create",
):
    """
    Construct a real Spell instance without relying on its __init__.
    We set the fields Spellbook expects to touch.
    """
    s = Spell.__new__(Spell)  # bypass __init__
    # minimal field set used by Spellbook
    s.spell_id = spell_id
    s.spellframe = frame
    s.spell_name = name
    s.binding_name = binding
    s._key = (frame or name, binding or "__default__")

    # permissions object with .name
    perm = MagicMock()
    perm.name = perm_name
    s.permissions = perm

    # hooks the Spellbook may assign to
    s.pre_hooks = []
    s.activation_hooks = []
    s.post_hooks = []

    # method used by _define_conduit_into_spells
    def _add_owned_conduit(conduit_id: UUID, conduit_name: str, creations: object):
        return None

    s._add_owned_conduit = _add_owned_conduit
    return s


class DummyConfig:
    """Tiny config stub with only what Spellbook actually uses in these tests."""
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


# ----------------------- Tests: Basics -----------------------

class TestSpellbookBasics(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_make_spell_key_normalization(self):
        self.assertEqual(self.sb._make_spell_key("frameX", "MySpell", None), ("frameX", "__default__"))
        self.assertEqual(self.sb._make_spell_key(None, "MySpell", "alt"), ("MySpell", "alt"))
        self.assertEqual(self.sb._make_spell_key("", "MySpell", ""), ("MySpell", "__default__"))

    def test_find_spell_count_initial(self):
        self.assertEqual(self.sb._find_spell_count(), 0)
        self.assertEqual(self.sb._find_contracted_spell_count(), 0)

    def test_initialize_configuration_calls_getter(self):
        # After constructor with patched getter(None), config should be a new Configuration or stubbed later.
        self.assertFalse(callable(self.sb._configuration))


# ----------------------- Tests: Binding -----------------------

class TestSpellbookBinding(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        # Fresh Spellbook; use a local DummyConfig for deterministic behavior when needed
        self.sb = Spellbook()
        # Replace static Aether handle with a mock
        Spellbook._aether = MagicMock()
        Spellbook._aether._check_for_spell.return_value = False
        # Plug a mock binder that returns a REAL Spell instance
        self.sb._bind = MagicMock()

    def _bind_one(self, frame="f", name="N", bind="__default__", perm="create"):
        s = make_real_spell("ID-123", frame, name, bind, perm_name=perm)
        self.sb._bind.bind.return_value = s
        sid = self.sb.bind(
            spell="ignored",
            existence=Existence.unique,
            permissions=perm,
            spellframe=frame,
            binding_name=bind,
        )
        self.assertEqual(sid, "ID-123")
        return s

    def test_bind_success_adds_to_maps(self):
        s = self._bind_one(frame="frameA", name="Thing", bind="b1")
        self.assertIn(s.spell_id, self.sb._spells)
        self.assertIn(s._key, self.sb._lookup_spells)
        self.assertEqual(self.sb._lookup_spells[s._key], s.spell_id)

    def test_bind_duplicate_rejected_by_aether(self):
        # Real Spell returned
        s = make_real_spell("ID-DUP", "f", "N", "__default__", perm_name="create")
        self.sb._bind.bind.return_value = s
        Spellbook._aether._check_for_spell.return_value = True
        with self.assertRaises(RuntimeError):
            self.sb.bind(spell="x", existence=Existence.unique)

    def test_add_hooks_type_checks_accepts_callables(self):
        s = self._bind_one()
        # provide valid hooks
        self.sb._add_hooks_to_spell(s, pre_hooks=[lambda: None], activation_hooks=[lambda: None], post_hooks=[lambda: None])
        self.assertEqual(len(s.pre_hooks), 1)
        self.assertEqual(len(s.activation_hooks), 1)
        self.assertEqual(len(s.post_hooks), 1)

    def test_add_hooks_type_checks_rejects_noncallables(self):
        s = self._bind_one()
        with self.assertRaises(TypeError):
            self.sb._add_hooks_to_spell(s, pre_hooks=[object()])
        with self.assertRaises(TypeError):
            self.sb._add_hooks_to_spell(s, activation_hooks=[object()])
        with self.assertRaises(TypeError):
            self.sb._add_hooks_to_spell(s, post_hooks=[object()])

    def test_find_spell_id_and_key(self):
        s = self._bind_one(frame="F", name="X", bind="B")
        self.assertEqual(self.sb.find_spell_key("F", "X", "B"), s._key)
        self.assertEqual(self.sb.find_spell_id("F", "X", "B"), s.spell_id)

    def test_find_spell_id_raises_when_missing(self):
        with self.assertRaises(RuntimeError):
            self.sb.find_spell_id("nope", "nope", "nope")

    def test_get_spell_permissions(self):
        s = self._bind_one(perm="read")
        got = self.sb.get_spell_permissions(s.spell_id)
        self.assertEqual(got, "read")


# ----------------------- Tests: Contracted Spells -----------------------

class TestSpellbookContractedSpells(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()

    def test_create_and_remove_link_contract_consistency(self):
        cid = uuid4()
        self.sb._create_link_contract(cid)
        self.assertIn(cid, self.sb._contracted_spells)
        self.assertIn(cid, self.sb._lookup_contracted_spells)

        self.sb._remove_link_contract(cid)
        self.assertNotIn(cid, self.sb._contracted_spells)
        self.assertNotIn(cid, self.sb._lookup_contracted_spells)

    def test_create_link_contract_raises_on_partial_state(self):
        cid = uuid4()
        self.sb._contracted_spells[cid] = {}
        with self.assertRaises(RuntimeError):
            self.sb._create_link_contract(cid)

    def test_remove_link_contract_raises_on_partial_state(self):
        cid = uuid4()
        self.sb._lookup_contracted_spells[cid] = {}
        with self.assertRaises(RuntimeError):
            self.sb._remove_link_contract(cid)

    def test_add_and_remove_contracted_spell_updates_both_maps(self):
        cid = uuid4()
        s = make_real_spell("S-1", "F", "N", "B")
        self.sb._add_contracted_spell(s, cid)

        self.assertIn("S-1", self.sb._contracted_spells[cid])
        self.assertIn(("F", "B"), self.sb._lookup_contracted_spells[cid])

        self.sb._remove_contracted_spell("S-1", cid)
        self.assertNotIn("S-1", self.sb._contracted_spells[cid])
        self.assertNotIn(("F", "B"), self.sb._lookup_contracted_spells[cid])

    def test_clear_contracted_spells_for_conduit(self):
        cid = uuid4()
        self.sb._add_contracted_spell(make_real_spell("A", "F", "N", "B"), cid)
        self.sb._add_contracted_spell(make_real_spell("B", "F", "N2", "B2"), cid)
        self.sb._clear_contracted_spells_for_conduit(cid)
        self.assertEqual(len(self.sb._contracted_spells[cid]), 0)
        self.assertEqual(len(self.sb._lookup_contracted_spells[cid]), 0)

    def test_sever_link_contract(self):
        cid = uuid4()
        self.sb._add_contracted_spell(make_real_spell("A", "F", "N", "B"), cid)
        self.sb._sever_link_contract(cid)
        self.assertNotIn(cid, self.sb._contracted_spells)
        self.assertNotIn(cid, self.sb._lookup_contracted_spells)

    def test_find_contracted_spell_helpers(self):
        cid = uuid4()
        s = make_real_spell("Z", "F", "N", "B")
        self.sb._add_contracted_spell(s, cid)
        self.assertIs(self.sb._find_contracted_spell_by_id("Z", cid), s)
        self.assertIs(self.sb._find_contracted_spell("Z"), s)


# ----------------------- Tests: Inspect + Config -----------------------

class TestSpellbookInspectAndConfig(unittest.TestCase):
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

    def test_configure_aether_frame_success(self):
        self.sb._configuration_locked = False
        self.sb._configuration = DummyConfig(frame="default")
        Spellbook._aether._bind_configuration = MagicMock()

        self.sb.configure_aether_frame(
            system_state="automatic",
            debugging=True,
            disposal=False,
            disposal_method_names=["close", "cleanup"],
        )
        self.assertTrue(self.sb._configuration_locked)
        self.assertEqual(self.sb._configuration.get_property("system_state"), "automatic")
        Spellbook._aether._bind_configuration.assert_called_once()

    def test_configure_aether_frame_rejects_unknown_key(self):
        self.sb._configuration_locked = False
        self.sb._configuration = DummyConfig(frame="default")
        # Simulate an unknown key by removing it
        self.sb._configuration.available_properties.pop("debugging")
        with self.assertRaises(KeyError):
            self.sb.configure_aether_frame(
                system_state="automatic",
                debugging=True,
                disposal=None,
                disposal_method_names=None,
            )

    def test_check_system_state_automatic_rejects_dynamic_policies(self):
        self.sb._configuration = DummyConfig(frame="default")
        self.sb._configuration.set_property("system_state", "automatic")
        with self.assertRaises(RuntimeError):
            self.sb._check_system_state(policy="dynamic")  # string intentionally, to hit the early check


# ----------------------- Tests: Conjure -----------------------

class TestSpellbookConjure(unittest.TestCase):
    @patch.object(Spellbook, "_get_configuration_from_aether", return_value=None)
    def setUp(self, _):
        self.sb = Spellbook()
        self.sb._configuration_locked = False
        self.sb._configuration = DummyConfig(frame="default")
        Spellbook._aether = MagicMock()

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_creates_conduit_and_locks_config(self, MockConduit):
        # Ensure defaults
        self.sb._configuration.load_default_dictionary()

        # Pass enum (your _check_system_state runs before EnumHelpers.convert)
        c = self.sb.conjure(policy=Policies.automatic, name="C1")

        # Config frozen/locked
        self.assertTrue(self.sb._configuration_locked)

        # Conduit constructed with expected args
        MockConduit.assert_called_once()
        _, kwargs = MockConduit.call_args
        self.assertEqual(kwargs["name"], "C1")
        self.assertEqual(kwargs["conduit_state"], ConduitState.normal)
        self.assertEqual(kwargs["aetheric_frame"], "default")
        self.assertEqual(kwargs["policy"], Policies.automatic)

        # Only one conjure allowed
        with self.assertRaises(RuntimeError):
            self.sb.conjure(policy=Policies.automatic)

    @patch("melder.spellbook.spellbook.Conduit")
    def test_conjure_rejects_dynamic_policy_in_automatic_state(self, MockConduit):
        self.sb._configuration.set_property("system_state", "automatic")
        with self.assertRaises(RuntimeError):
            self.sb.conjure(policy=Policies.dynamic, name="X")


if __name__ == "__main__":
    unittest.main()
