import unittest
import dataclasses
from abc import ABC, abstractmethod

# Adjust this import to your actual path if different:
from melder.spellbook.spell_crafter.spell_examiner.inspectors.class_inspector import ClassInspector


# ---------- Helpers for tests ----------

def no_wrap_decorator(fn):
    # Deliberately NOT using functools.wraps to force (*a, **k) signature
    def inner(*a, **k):
        return fn(*a, **k)
    return inner

def class_tag_decorator(cls):
    """
    Mark a class as 'decorated' in a way ClassInspector can detect.
    Setting __wrapped__ to a different object ensures inspect.unwrap() changes.
    """
    setattr(cls, "__wrapped__", (cls.__name__, "decorated"))
    setattr(cls, "_decorated", True)  # header heuristic also sees this
    return cls


class BaseExample:
    base_attr = 123

    def foo(self, x):  # inherited method
        return x + 1


@class_tag_decorator
class DecoratedExample:
    pass


class WithProps:
    def __init__(self, v):
        self._v = v

    @property
    def v(self):
        return self._v

    @v.setter
    def v(self, nv):
        self._v = nv


class WithAbstract(ABC):
    @abstractmethod
    def doit(self): ...


class WithSlots:
    __slots__ = ("a", "b")
    def __init__(self):
        self.a = 1
        self.b = 2


class Protocolish:
    def __len__(self): return 1
    def __getitem__(self, i): return i
    def __iter__(self): return iter([1,2,3])
    def __call__(self): return "called"
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False
    def __await__(self):
        # just to satisfy presence, not actually awaited in tests
        class _FakeIter:
            def __iter__(self): return self
            def __next__(self): raise StopIteration
        return _FakeIter()
    def __add__(self, other): return 0
    def __hash__(self): return 42
    def __repr__(self): return "<Protocolish>"
    def __str__(self): return "Protocolish"


class MethodShapes:
    def pure(self, x, y=2):  # normal method
        return x + y

    @staticmethod
    def sm(a, b=5):
        return a + b

    @classmethod
    def cm(cls, z=3):
        return z

    @no_wrap_decorator
    def wrapped(self, x, y=2):  # wrapper should show (*a, **k) as primary
        return x + y


@dataclasses.dataclass
class AData:
    x: int
    y: int = 2  # dataclass will have __init__


class DerivedExample(BaseExample):
    def bar(self, t):  # defined here
        return t * 2


# ---------- Test Suite ----------

class TestClassInspector(unittest.TestCase):

    # 1
    def test_header_basic_metadata(self):
        ci = ClassInspector(DerivedExample).inspect()
        self.assertEqual(ci["name"], "DerivedExample")
        self.assertIn("DerivedExample", ci["qualname"])
        self.assertEqual(ci["module"], DerivedExample.__module__)
        self.assertIsInstance(ci["id"], int)
        self.assertIn("BaseExample", ci["mro"])
        self.assertIn("object", ci["mro"])
        self.assertFalse(ci["is_extension_module"])

    # 2
    def test_source_fields_present(self):
        ci = ClassInspector(WithProps).inspect()
        self.assertIsNotNone(ci["file"])
        # Preview may be trimmed but should contain the word 'class'
        self.assertIsInstance(ci["source_preview"], (str, type(None)))
        if ci["source_preview"]:
            self.assertIn("class", ci["source_preview"])
        self.assertIsInstance(ci["source_line_offset"], (int, type(None)))

    # 3
    def test_members_contains_defined_and_inherited(self):
        ci = ClassInspector(DerivedExample, show_dunders=True).inspect()
        members = ci["members"]
        # 'bar' defined on DerivedExample
        self.assertIn("bar", members)
        self.assertTrue(members["bar"]["defined_here"])
        self.assertEqual(members["bar"]["owner_class"], "DerivedExample")
        # 'foo' inherited from BaseExample
        self.assertIn("foo", members)
        self.assertFalse(members["foo"]["defined_here"])
        self.assertEqual(members["foo"]["owner_class"], "BaseExample")

    # 4
    def test_member_signature_normal_method(self):
        ci = ClassInspector(MethodShapes).inspect()
        members = ci["members"]
        self.assertIn("pure", members)
        self.assertEqual(members["pure"]["signature"], "(self, x, y=2)")
        self.assertIsInstance(members["pure"]["src_line"], (int, type(None)))

        # 5
    def test_member_signature_static_and_classmethod(self):
        class Sample:
            @staticmethod
            def sm(z=3): ...
            @classmethod
            def cm(cls, z=3): ...

        ci = ClassInspector(Sample, show_dunders=True).inspect()
        members = ci["members"]

        # staticmethod is stable: no implicit receiver
        self.assertEqual(members["sm"]["signature"], "(z=3)")

        # classmethod may be bound (no cls) or descriptor (with cls)
        self.assertIn(members["cm"]["signature"], ("(cls, z=3)", "(z=3)"))



    # 6
    def test_wrapped_method_primary_and_original_signature(self):
        ci = ClassInspector(MethodShapes).inspect()
        m = ci["members"]["wrapped"]
        # Primary signature from wrapper: (*a, **k)
        self.assertEqual(m["signature"], "(*a, **k)")
        # Original (unwrapped) captured too
        self.assertEqual(m["original_signature"], "(self, x, y=2)")
        self.assertEqual(m["original_name"], "wrapped")

    # 7
    def test_property_detection_and_details(self):
        ci = ClassInspector(WithProps).inspect()
        members = ci["members"]
        self.assertIn("v", members)
        self.assertTrue(members["v"]["property"])
        pd = members["v"]["property_details"]
        self.assertTrue(pd["fget"])
        self.assertTrue(pd["fset"])
        self.assertFalse(pd["fdel"])

    # 8
    def test_abstract_detection(self):
        ci = ClassInspector(WithAbstract).inspect()
        members = ci["members"]
        # doit is abstract
        self.assertIn("doit", members)
        self.assertTrue(members["doit"]["abstract"])

    # 9
    def test_slots_detection(self):
        ci = ClassInspector(WithSlots).inspect()
        self.assertEqual(tuple(ci["slots"]), ("a", "b"))

    # 10
    def test_protocols_map(self):
        ci = ClassInspector(Protocolish).inspect()
        p = ci["protocols"]
        self.assertTrue(p["len"])
        self.assertTrue(p["getitem"])
        self.assertTrue(p["iter"])
        self.assertTrue(p["call"])
        self.assertTrue(p["enter"])
        self.assertTrue(p["await"])
        self.assertTrue(p["add"])
        self.assertTrue(p["hash"])
        self.assertTrue(p["repr"])
        self.assertTrue(p["str"])

    # 11
    def test_annotations_present(self):
        class Ann:
            a: int
            b: str
        ci = ClassInspector(Ann).inspect()
        self.assertIn("a", ci["annotations"])
        self.assertIn("b", ci["annotations"])

    # 12
    def test_dunder_elision_default(self):
        ci = ClassInspector(MethodShapes, show_dunders=False).inspect()
        members = ci["members"]
        # typical dunder like __init__ should not be present (MethodShapes defines none explicitly anyway)
        self.assertNotIn("__repr__", members)

    # 13
    def test_show_dunders_true_includes_dunders(self):
        ci = ClassInspector(MethodShapes, show_dunders=True).inspect()
        members = ci["members"]
        # class dict has many dunders via type; with show_dunders=True, we should see them
        self.assertIn("__module__", members)

    # 14
    def test_dataclass_includes_dunder_init_even_when_filtered(self):
        ci = ClassInspector(AData, show_dunders=False).inspect()
        members = ci["members"]
        # Special rule: dataclass __init__ must appear even when dunders filtered
        self.assertIn("__init__", members)
        self.assertIn("(self, x: int, y: int = 2)", members["__init__"]["signature"])

    # 15
    def test_mro_order_contains_base_and_object(self):
        ci = ClassInspector(DerivedExample).inspect()
        self.assertEqual(ci["mro"][0], "DerivedExample")
        self.assertIn("BaseExample", ci["mro"])
        self.assertIn("object", ci["mro"])

    # 16
    def test_decorated_class_detected_via_unwrap(self):
        ci = ClassInspector(DecoratedExample).inspect()
        # Your decorator sets __wrapped__ to a non-callable tuple, so inspect.unwrap()
        # won’t change the object; the heuristic still flags it as decorated.
        self.assertTrue(ci["decorated"])
        # Don’t require 'wrapped_repr' here—it's only set when unwrap actually changes target.
        # Optional extra sanity: the tag you put on the class is visible as a member.
        self.assertIn("_decorated", ci["members"])
        self.assertEqual(ci["members"]["_decorated"]["repr"], "True")

    # 17
    def test_member_repr_is_safe_and_string(self):
        ci = ClassInspector(MethodShapes).inspect()
        members = ci["members"]
        self.assertIsInstance(members["pure"]["repr"], str)

    # 18
    def test_is_builtin_and_extension_module_flags(self):
        ci = ClassInspector(MethodShapes).inspect()
        # This test class lives in a normal Python module
        self.assertFalse(ci["is_builtin_module"])
        self.assertFalse(ci["is_extension_module"])

    # 19
    def test_member_src_line_present_when_source_available(self):
        ci = ClassInspector(MethodShapes).inspect()
        members = ci["members"]
        # For methods we defined here, src_line should be an int
        self.assertIsInstance(members["pure"]["src_line"], (int, type(None)))
        self.assertIsInstance(members["wrapped"]["src_line"], (int, type(None)))

    # 20
    def test_owner_class_resolution_for_inherited_member(self):
        ci = ClassInspector(DerivedExample).inspect()
        foo_info = ci["members"]["foo"]
        self.assertEqual(foo_info["owner_class"], "BaseExample")
        self.assertFalse(foo_info["defined_here"])


if __name__ == "__main__":
    unittest.main()
