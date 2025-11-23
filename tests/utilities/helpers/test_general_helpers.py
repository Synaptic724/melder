# tests/utilities/helpers/test_general_helpers.py

import unittest
from enum import Enum

from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import DirectedAcyclicWorkGraph
from melder.spellbook.spell_crafter.old_spell_examiner.spell_examiner import InspectorUtility  # sanity import
from melder.utilities.helpers.general_helpers import EnumHelpers, SpellInputUtils


# ----- Test fixtures ---------------------------------------------------------

class lower_color(Enum):
    red = 1
    green = 2
    blue = 3

class UPPER_COLOR(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

class WeirdRepr:
    def __repr__(self) -> str:
        return "<WeirdRepr id=42>"

class Sample:
    pass

class WithDunderName:
    __name__ = "CustomName"  # NOTE: for classes, real __name__ remains the class name


# ----- EnumHelpers tests -----------------------------------------------------

class TestEnumHelpers(unittest.TestCase):
    def test_returns_same_member_if_already_enum(self):
        self.assertIs(
            EnumHelpers.convert_enum_and_check(lower_color.red, lower_color),
            lower_color.red
        )

    def test_string_to_enum_lower_named_members_happy(self):
        self.assertIs(EnumHelpers.convert_enum_and_check("RED", lower_color), lower_color.red)
        self.assertIs(EnumHelpers.convert_enum_and_check("green", lower_color), lower_color.green)
        self.assertIs(EnumHelpers.convert_enum_and_check("BlUe", lower_color), lower_color.blue)

    def test_upper_named_enum_with_mixed_case_string_raises(self):
        with self.assertRaises(ValueError) as ctx:
            EnumHelpers.convert_enum_and_check("red", UPPER_COLOR)
        self.assertIn("Invalid value 'red' for enum UPPER_COLOR.", str(ctx.exception))
        self.assertIn("['RED', 'GREEN', 'BLUE']", str(ctx.exception))

    def test_string_invalid_value_raises_and_lists_valid_options(self):
        with self.assertRaises(ValueError) as ctx:
            EnumHelpers.convert_enum_and_check("purple", lower_color)
        msg = str(ctx.exception)
        self.assertIn("Invalid value 'purple' for enum lower_color.", msg)
        self.assertIn("['red', 'green', 'blue']", msg)

    def test_non_string_non_enum_raises(self):
        for bad in (123, 3.14, object(), WeirdRepr()):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    EnumHelpers.convert_enum_and_check(bad, lower_color)
                self.assertIn("Expected a string or lower_color member", str(ctx.exception))

    def test_lru_cache_effect_basic(self):
        self.assertIs(EnumHelpers.convert_enum_and_check("RED", lower_color), lower_color.red)
        self.assertIs(EnumHelpers.convert_enum_and_check("RED", lower_color), lower_color.red)


# ----- SpellInputUtils.normalize_spellframe ----------------------------------

class TestNormalizeSpellframe(unittest.TestCase):
    def test_class_returns_class_name(self):
        self.assertEqual(SpellInputUtils.normalize_spellframe(Sample), "Sample")

    def test_str_returns_same_string(self):
        self.assertEqual(SpellInputUtils.normalize_spellframe("MyFrame"), "MyFrame")

    def test_other_type_falls_back_to_str(self):
        w = WeirdRepr()
        self.assertEqual(SpellInputUtils.normalize_spellframe(w), "<WeirdRepr id=42>")

    def test_cached_normalize_spellframe_indirect(self):
        self.assertEqual(SpellInputUtils._normalize_frame_cached(Sample), "sample")
        self.assertEqual(SpellInputUtils._normalize_frame_cached("MiXeD"), "mixed")
        self.assertEqual(SpellInputUtils._normalize_frame_cached(WeirdRepr()), "<weirdrepr id=42>")


# ----- SpellInputUtils._normalize_binding_name -------------------------------

class TestNormalizeBindingName(unittest.TestCase):
    def test_default_binding_is___default__(self):
        self.assertEqual(SpellInputUtils._normalize_binding_name(None), "__default__")

    def test_binding_lowercased(self):
        self.assertEqual(SpellInputUtils._normalize_binding_name("Primary"), "primary")

    def test_binding_empty_string_maps_to___default__(self):
        # Your current impl treats "" as falsy and returns "__default__"
        self.assertEqual(SpellInputUtils._normalize_binding_name(""), "__default__")


# ----- SpellInputUtils.normalize_spell_key -----------------------------------

class TestNormalizeSpellKey(unittest.TestCase):
    def test_spellframe_wins_over_spell(self):
        frame, name = SpellInputUtils.normalize_spell_key(spell=Sample, spellframe="Iface", binding_name="Alt")
        self.assertEqual(frame, "iface")
        self.assertEqual(name, "alt")

    def test_spell_used_when_no_spellframe(self):
        frame, name = SpellInputUtils.normalize_spell_key(spell=Sample, binding_name=None)
        self.assertEqual(frame, "sample")
        self.assertEqual(name, "__default__")

    def test_instance_spell_uses_type_name(self):
        inst = Sample()
        frame, name = SpellInputUtils.normalize_spell_key(spell=inst, binding_name="B")
        self.assertEqual(frame, "sample")
        self.assertEqual(name, "b")

    def test_plain_string_spellframe(self):
        frame, name = SpellInputUtils.normalize_spell_key(spell=None, spellframe="Xx", binding_name="Yy")
        self.assertEqual(frame, "xx")
        self.assertEqual(name, "yy")

    def test_weird_object_spellframe_uses_str(self):
        w = WeirdRepr()
        frame, name = SpellInputUtils.normalize_spell_key(spell=None, spellframe=w, binding_name=None)
        self.assertEqual(frame, "<weirdrepr id=42>")
        self.assertEqual(name, "__default__")

    def test_dunder_name_object_as_spell_is_ignored_for_real_class(self):
        # For real classes, Python keeps __name__ as the true class name ("WithDunderName").
        # Your implementation uses getattr(spell, "__name__", type(spell).__name__), so this resolves to the class name.
        frame, name = SpellInputUtils.normalize_spell_key(spell=WithDunderName, binding_name="Z")
        self.assertEqual(frame, "withdundername")
        self.assertEqual(name, "z")

    def test_spell_none_spellframe_none_gives_str_none(self):
        frame, name = SpellInputUtils.normalize_spell_key(spell=None, spellframe=None, binding_name=None)
        self.assertEqual(frame, "none")
        self.assertEqual(name, "__default__")

    def test_binding_name_explicit_empty_goes_to___default__(self):
        frame, name = SpellInputUtils.normalize_spell_key(spell=Sample, binding_name="")
        self.assertEqual(frame, "sample")
        self.assertEqual(name, "__default__")

    def test_cached_paths_return_consistent_values(self):
        a1 = SpellInputUtils._normalize_frame_cached("FOO")
        a2 = SpellInputUtils._normalize_frame_cached("FOO")
        self.assertEqual(a1, a2)
        b1 = SpellInputUtils._normalize_binding_name("BAR")
        b2 = SpellInputUtils._normalize_binding_name("BAR")
        self.assertEqual(b1, b2)

    def test_class_spellframe_direct_class(self):
        frame, name = SpellInputUtils.normalize_spell_key(
            spell=None, spellframe=DirectedAcyclicWorkGraph, binding_name="main"
        )
        self.assertEqual(frame, "directedacyclicworkgraph")
        self.assertEqual(name, "main")


if __name__ == "__main__":
    unittest.main()
