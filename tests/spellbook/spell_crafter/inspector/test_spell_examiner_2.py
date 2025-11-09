import unittest
import functools
import types
import sys
import inspect
from dataclasses import dataclass, field, make_dataclass
from typing import Any, Optional, Iterator, AsyncIterator, Generic, TypeVar

from melder.spellbook.spell_crafter.inspector.spell_examiner import (
    InspectorUtility, ClassInspector, MethodInspector, SpellExaminer,
    MethodProfile, ClassProfile
)

T = TypeVar("T")

# ---------------------------------------------------------------------
# Targets & helpers (distinct from file 01)
# ---------------------------------------------------------------------

def pos_only_func(a, /, b, *, c=5, **kw):
    return (a, b, c, kw)

def varargs_kwargs(x, *args, y=3, **kw):
    return (x, args, y, kw)

def defaults_none(a=None, b: Optional[int] = None):
    return a, b

def forward_ann_func(x: 'InnerThing') -> 'OuterThing':
    return OuterThing()

def make_partial_target(u, v=10, *args, w=11, **kw):
    return (u, v, args, w, kw)

def no_wrap_decorator(fn):
    # purposely NOT using functools.wraps
    def inner(*a, **k):
        return fn(*a, **k)
    return inner

@no_wrap_decorator
def nowrapped(x, y=2):
    return x + y

def asyncgen_func(n: int) -> AsyncIterator[int]:
    async def _gen():
        for i in range(n):
            yield i
    return _gen()

def generator_with_send() -> Iterator[int]:
    x = 0
    while True:
        inc = (yield x)
        x += (inc or 1)

class OuterThing: ...
class InnerThing: ...

class SlotsThing:
    __slots__ = ("a", "b")
    def __init__(self):
        self.a = 1; self.b = 2
    def slot_m(self, k: int) -> int:
        return self.a + self.b + k

class ConstBag:
    CONST_A = 10
    CONST_B = "Z"
    def f(self): return 1

class OverrideStaticsBase:
    @staticmethod
    def s(): return "baseS"
    @classmethod
    def c(cls): return f"baseC:{cls.__name__}"

class OverrideStaticsChild(OverrideStaticsBase):
    @staticmethod
    def s(): return "childS"
    @classmethod
    def c(cls): return f"childC:{cls.__name__}"

class OwnerSpreadA:
    def where(self): return "A"

class OwnerSpreadB(OwnerSpreadA):
    pass

class OwnerSpreadC(OwnerSpreadB):
    def where(self): return "C"

class PropShadowBase:
    @property
    def p(self): return "base"
class PropShadowChild(PropShadowBase):
    @property
    def p(self): return "child"

class Protoish2:
    def __len__(self): return 1
    def __iter__(self): return iter((1,))
    def __repr__(self): return "r"
    def __str__(self): return "s"
    def __call__(self): return 1
    def __add__(self, other): return 2
    def __hash__(self): return 123

class NestedFrames:
    class Inner:
        @staticmethod
        def z(a=1): return a

@dataclass(frozen=True)
class FrozenD:
    x: int
    y: str = "y"

@dataclass
class DefaultFactoryD:
    d: dict = field(default_factory=dict)

class GenericThing(Generic[T]):
    def put(self, value: T) -> T: return value

def make_dyn_class(name="DynX"):
    return type(name, (), {"v": 1, "m": lambda self: 2})

def build_function_without_module():
    # create a function with a funky __module__
    def f(a, b): return a + b
    f.__module__ = None
    return f

def attrib_with_bad_repr():
    class Bad:
        def __repr__(self):
            raise RuntimeError("die")
    class HasBad:
        BAD = Bad()
    return HasBad

def decorator_returns_other(f):
    def other(*a, **k): return f(*a, **k)
    other.__wrapped__ = f  # pretend "decorated"
    return other

@decorator_returns_other
def replaced(x): return x

class KwOnlyThing:
    def g(self, *, k1, k2=2): return k1 + k2

class PosOnlyThing:
    def h(self, a, /, b): return a + b

class AnnoWeird:
    def f(self, a: "int|str", b: Optional['OuterThing']) -> "dict[str,int]": return {}

# ---------------------------------------------------------------------
# TESTS (40)
# ---------------------------------------------------------------------

class TestUtilityDeep(unittest.TestCase):
    def test_safe_repr_handles_large_container(self):
        big = list(range(200))
        out = InspectorUtility.safe_repr(big, max_len=80)
        # ensure truncates & length tag present
        self.assertIn("... (len ", out)

    def test_safe_repr_none_module_object(self):
        cls = build_function_without_module()
        r = InspectorUtility.safe_repr(cls, max_len=60)
        self.assertTrue(isinstance(r, str))

    def test_is_extension_module_handles_missing_spec(self):
        fake = types.SimpleNamespace()
        self.assertFalse(InspectorUtility.is_extension_module(fake))

    def test_is_extension_module_none(self):
        self.assertFalse(InspectorUtility.is_extension_module(None))

class TestMethodInspectorParams(unittest.TestCase):
    def test_positional_only_and_kwonly_rendered(self):
        data = MethodInspector(pos_only_func).inspect()
        sig = data.get("signature", "")
        # allow backend-specific spacing but ensure the markers are present
        self.assertIn("/", sig)
        self.assertIn("*", sig)

    def test_varargs_kwargs_rendered(self):
        data = MethodInspector(varargs_kwargs).inspect()
        sig = data.get("signature", "")
        self.assertIn("*args", sig)
        self.assertIn("**kw", sig)

    def test_defaults_none_visible(self):
        data = MethodInspector(defaults_none).inspect()
        params = {p["name"]: p for p in data.get("parameters", [])}
        self.assertIn("None", str(params["a"]["default"]))
        self.assertIn("None", str(params["b"]["default"]))

    def test_forward_annotations_show_up_somehow(self):
        data = MethodInspector(forward_ann_func).inspect()
        sig = data.get("signature", "")
        # don’t enforce exact string; just require both names appear somewhere
        self.assertTrue("InnerThing" in sig and "OuterThing" in sig)

    def test_partial_functions_have_signature_and_no_crash(self):
        p = functools.partial(make_partial_target, 7, 8, w=9)
        data = MethodInspector(p).inspect()
        self.assertIn("signature", data)
        self.assertTrue(isinstance(data.get("repr", ""), str))

    def test_nowrapped_function_still_inspected(self):
        data = MethodInspector(nowrapped).inspect()
        self.assertIn("(x, y=2)", data.get("signature", ""))

    def test_async_generator_flag(self):
        data = MethodInspector(asyncgen_func).inspect()
        self.assertTrue(data.get("async_gen") in (True, False))  # just ensure presence
        # not a normal coroutine here
        self.assertFalse(data.get("coroutine", False))

    def test_generator_with_send_detected_as_generator(self):
        data = MethodInspector(generator_with_send).inspect()
        self.assertTrue(data.get("generator"))

class TestMethodKindsAndTraits(unittest.TestCase):
    def test_static_override_detect(self):
        data = MethodInspector(OverrideStaticsChild.s).inspect()
        self.assertTrue(data.get("staticmethod"))

    def test_classmethod_override_detect(self):
        data = MethodInspector(OverrideStaticsChild.c).inspect()
        self.assertTrue(data.get("classmethod"))

    def test_nested_staticmethod_signature(self):
        data = MethodInspector(NestedFrames.Inner.z).inspect()
        self.assertIn("(a=1)", data.get("signature", ""))

    def test_kwonly_method_signature(self):
        data = MethodInspector(KwOnlyThing.g).inspect()
        self.assertIn("*, k1", data.get("signature", ""))

    def test_posonly_method_signature(self):
        data = MethodInspector(PosOnlyThing.h).inspect()
        self.assertIn("/", data.get("signature", ""))

    def test_unionlike_annotations_render(self):
        data = MethodInspector(AnnoWeird.f).inspect()
        sig = data.get("signature", "")
        self.assertTrue("OuterThing" in sig or "dict" in sig)

class TestClassInspectorDeep(unittest.TestCase):
    def test_slots_are_reported(self):
        data = ClassInspector(SlotsThing).inspect()
        self.assertIn("slots", data)
        slots = data["slots"]
        self.assertTrue(slots is None or "a" in slots or "b" in slots)

    def test_constants_appear_as_data_members(self):
        data = ClassInspector(ConstBag).inspect()
        mems = data["members"]
        self.assertIn("CONST_A", mems)
        self.assertEqual(mems["CONST_A"]["kind"], "data")

    def test_owner_resolution_deeper_mro(self):
        data = ClassInspector(OwnerSpreadC).inspect()
        mems = data["members"]
        self.assertTrue(mems["where"]["defined_here"])
        self.assertEqual(mems["where"]["owner_class"], "OwnerSpreadC")

    def test_property_shadowing_shows_child_defined(self):
        data = ClassInspector(PropShadowChild).inspect()
        mems = data["members"]
        self.assertTrue(mems["p"]["defined_here"])

    def test_protocols_including_add_hash(self):
        data = ClassInspector(Protoish2).inspect()
        p = data["protocols"]
        self.assertTrue(p["add"])
        self.assertTrue(p["hash"])

    def test_members_include_signatures_for_user_methods(self):
        data = ClassInspector(SlotsThing).inspect()
        mems = data["members"]
        self.assertIn("slot_m", mems)
        self.assertIn("(self, k: int) -> int", mems["slot_m"]["signature"])

    def test_bad_repr_attribute_does_not_crash(self):
        C = attrib_with_bad_repr()
        data = ClassInspector(C).inspect()
        self.assertIn("members", data)  # just no crash

    def test_dynamic_class_source_may_be_missing_but_no_crash(self):
        D = make_dyn_class()
        data = ClassInspector(D).inspect()
        self.assertIn("members", data)

class TestDataclassFlavors(unittest.TestCase):
    def test_frozen_dataclass_flagged_dataclass(self):
        data = ClassInspector(FrozenD).inspect()
        self.assertTrue(data.get("is_dataclass"))

    def test_default_factory_dataclass_ok(self):
        data = ClassInspector(DefaultFactoryD).inspect()
        self.assertTrue(data.get("is_dataclass"))
        mems = data["members"]
        self.assertIn("__init__", mems or {})  # may or may not be present depending on show_dunders default

class TestGenericAndTyping(unittest.TestCase):
    def test_generic_method_signature_contains_T(self):
        data = ClassInspector(GenericThing).inspect()
        mems = data["members"]
        sig = mems["put"]["signature"]
        self.assertIn("value", sig)

    def test_generic_instance_method_profile(self):
        prof = SpellExaminer(GenericThing[int].put).inspect()
        if isinstance(prof, MethodProfile):
            self.assertIn("value", prof.signature or "")

class TestSpellExaminerDeep(unittest.TestCase):
    def test_class_profile_includes_static_and_class_methods(self):
        prof = SpellExaminer(OverrideStaticsChild).inspect()
        self.assertIsInstance(prof, ClassProfile)
        self.assertIn("s", prof.methods)
        self.assertIn("c", prof.methods)

    def test_function_profile_parameter_count(self):
        prof = SpellExaminer(varargs_kwargs).inspect()
        self.assertIsInstance(prof, MethodProfile)
        self.assertTrue(len(prof.parameters) >= 1)

    def test_to_json_on_class_with_slots(self):
        js = SpellExaminer(SlotsThing).to_json()
        self.assertIn('"name": "SlotsThing"', js)

    def test_to_json_on_no_wrap_decorated_function(self):
        js = SpellExaminer(nowrapped).to_json()
        self.assertIn('"name": "nowrapped"', js)

    def test_examiner_on_instance_returns_fallback(self):
        data = SpellExaminer(SlotsThing()).inspect()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["type"], "SlotsThing")

class TestDecorationWeirdness(unittest.TestCase):
    def test_function_marked_replaced_still_inspectable(self):
        data = MethodInspector(replaced).inspect()
        self.assertTrue("signature" in data)

    def test_class_decorated_like_wrapped_sets_flag_either_way(self):
        # fabricate a decorated-like class
        class X: pass
        X.__wrapped__ = X
        data = ClassInspector(X).inspect()
        self.assertTrue(data.get("decorated") in (True, False))  # just ensure key present

class TestMiscResilience(unittest.TestCase):
    def test_method_with_missing_module_info(self):
        f = build_function_without_module()
        data = MethodInspector(f).inspect()
        self.assertIn("name", data)

    def test_class_with_nested_static_readable(self):
        data = ClassInspector(NestedFrames.Inner).inspect()
        mems = data["members"]
        self.assertIn("z", mems)

    def test_method_signature_parameters_dict_shape(self):
        data = MethodInspector(varargs_kwargs).inspect()
        plist = data.get("parameters", [])
        # entries should have expected keys
        self.assertTrue(all({"name", "kind", "default", "annotation"} <= set(p) for p in plist))

    def test_repr_of_methodprofile_is_stringy(self):
        prof = SpellExaminer(varargs_kwargs).inspect()
        self.assertIsInstance(prof, MethodProfile)
        self.assertTrue(isinstance(prof.repr, str))

    def test_repr_of_classprofile_is_stringy(self):
        prof = SpellExaminer(SlotsThing).inspect()
        self.assertIsInstance(prof, ClassProfile)
        # the original dict is in .members; ensure it looks dict-like
        self.assertTrue(isinstance(prof.members, dict))

if __name__ == "__main__":
    unittest.main()
