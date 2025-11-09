# tests/spellbook/test_spell_unit.py
import unittest
from uuid import uuid4
from unittest.mock import MagicMock

# System under test
from melder.spellbook.spell import Spell
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_types.spell_types import SpellType


# Lightweight stand-ins; Spell doesn't runtime-enforce these beyond annotation.
ClassProfile = MagicMock
MethodProfile = MagicMock


def make_real_spell(
        *,
        spell_obj=None,
        frame=None,
        binding=None,
        name="MySpell",
        existence=Existence.unique,
        spell_type=None,
        profile=None,
        spell_id="SHA256-XYZ",
        permissions=None,
        aetheric_frame="default",
):
    if spell_obj is None:
        class Dummy:
            pass
        spell_obj = Dummy

    if profile is None:
        profile = ClassProfile()

    if permissions is None:
        permissions = MagicMock()
        permissions.name = "create"

    # Pick a concrete SpellType member safely
    if spell_type is None:
        # Prefer a common member name if present; otherwise fall back to the first enum member.
        spell_type = (
                SpellType.__members__.get("class_")
                or next(iter(SpellType.__members__.values()))
        )

    return Spell(
        spell=spell_obj,
        spellframe=frame,
        binding_name=binding,
        spell_name=name,
        existence=existence,
        spell_type=spell_type,
        profile=profile,
        spell_id=spell_id,
        permissions=permissions,
        aetheric_frame=aetheric_frame,
    )


class TestSpellCore(unittest.TestCase):
    def test_init_sets_core_fields_and_defaults(self):
        sp = make_real_spell(binding="b1", frame=str, aetheric_frame="frameA")
        self.assertEqual(sp.binding_name, "b1")
        self.assertIs(sp.spellframe, str)
        self.assertEqual(sp.aetheric_frame, "frameA")
        # Defaults commonly present in Spell
        self.assertIsNone(sp.timeout)
        self.assertEqual(sp.retries, 0)
        self.assertEqual(sp.dependencies, [])
        self.assertIsNone(sp.dependency_graph)
        self.assertIsInstance(sp.pre_hooks, list)
        self.assertIsInstance(sp.activation_hooks, list)
        self.assertIsInstance(sp.post_hooks, list)

    def test_key_uses_frame_and_binding_when_provided(self):
        sp = make_real_spell(frame="FrameX", binding="alt")
        self.assertEqual(sp._key, ("FrameX", "alt"))

    def test_key_falls_back_to_type_name_and_default_binding(self):
        # Passing a CLASS as spell → type(spell) is 'type', so key uses "type"
        class Foo:
            pass
        sp = make_real_spell(spell_obj=Foo, frame=None, binding=None)
        self.assertEqual(sp._key, ("type", "__default__"))

    def test_repr_contains_fields(self):
        sp = make_real_spell(frame=str, binding=None, name="Cache", spell_id="HASH123")
        r = repr(sp)
        self.assertIn("Spell(name=Cache", r)
        self.assertIn("binding=__default__", r)
        self.assertIn("frame=str", r)
        self.assertIn("SHA256=HASH123", r)

    def test_add_owned_conduit_sets_owner_fields_and_flag(self):
        sp = make_real_spell()
        cid = uuid4()
        sp._add_owned_conduit(conduit_id=cid, conduit_name="Main", creations={"scope": "X"})
        self.assertEqual(sp._owner_conduit_id, cid)
        self.assertEqual(sp._owner_conduit_name, "Main")
        self.assertTrue(sp.owned_spell)
        self.assertEqual(sp._owner_creations, {"scope": "X"})

    def test_add_build_details_sets_dag_and_dependencies(self):
        sp = make_real_spell()
        dag = object()
        deps = ["A", "B", "C"]
        sp._add_build_details(dag, deps)
        self.assertIs(sp.dependency_graph, dag)
        self.assertEqual(sp.dependencies, deps)

    def test_add_build_details_rejects_none_dag(self):
        sp = make_real_spell()
        with self.assertRaises(ValueError):
            sp._add_build_details(None, ["Z"])

    def test_add_build_details_rejects_none_dependencies(self):
        sp = make_real_spell()
        with self.assertRaises(ValueError):
            sp._add_build_details(object(), None)

    def test_permissions_passthrough_exposes_name(self):
        perm = MagicMock()
        perm.name = "read"
        sp = make_real_spell(permissions=perm)
        # Mirror what Spellbook relies on: permissions.name
        self.assertEqual(sp.permissions.name, "read")

    def test_cast_is_not_implemented(self):
        sp = make_real_spell()
        with self.assertRaises(NotImplementedError):
            sp.cast()


if __name__ == "__main__":
    unittest.main()
