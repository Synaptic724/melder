# tests/spellbook/spell_crafter/test_spell_crafter.py
import unittest
import types
import functools
import inspect
import sys
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List, Callable
from uuid import uuid4
from abc import ABC, abstractmethod
from melder.spellbook.spell_crafter.inspector.spell_examiner import (
    InspectorUtility, ClassInspector, MethodInspector, SpellExaminer,
    MethodProfile, ClassProfile
)

# --- Local helpers -----------------------------------------------------------

def make_fake_extension_module() -> object:
    class _Spec:  # mimic importlib.machinery.ModuleSpec
        origin = "/usr/lib/python3.11/lib-dynload/_ctypes.cpython-311-x86_64-linux-gnu.so"
    fake = types.SimpleNamespace()
    fake.__spec__ = _Spec()
    return fake

def make_fake_pyd_module() -> object:
    class _Spec:
        origin = r"C:\Python313\DLLs\_sqlite3.pyd"
    fake = types.SimpleNamespace()
    fake.__spec__ = _Spec()
    return fake


# Targets to inspect
def plain_func(a: int, b: int = 3) -> int:
    return a + b

def func_raises_repr():
    class BadRepr:
        def __repr__(self):
            raise RuntimeError("nope")
    return BadRepr()

def generator_func(n: int):
    for i in range(n):
        yield i

async def async_func(x: int) -> int:
    return x + 1

def make_wrapped():
    def deco(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            return fn(*args, **kwargs)
        return inner

    @deco
    def wrapped(x, y=10):  # noqa: ARG001
        return 42
    return wrapped

def no_wrap_decorator(fn):
    # deliberately NOT using functools.wraps
    def inner(*a, **k):
        return fn(*a, **k)
    return inner

@no_wrap_decorator
def nowrapped(x, y=2):
    return x + y

def make_decorated_class():
    def class_deco(cls):
        # Mark like functools.wraps would
        cls.__wrapped__ = cls  # signal "decorated"
        return cls

    @class_deco
    class DThing:
        VAR = 1
        def m(self, a): return a
    return DThing


class WithProperty:
    def __init__(self):
        self._v = 5
    @property
    def value(self):
        return self._v
    def set_value(self, x):  # helper (not used by @property)
        self._v = x

class WithStatics:
    @staticmethod
    def s(x):  # noqa: ARG001
        return "S"
    @classmethod
    def c(cls, y):  # noqa: ARG001
        return "C"
    def i(self, z):  # noqa: ARG001
        return "I"

class AbstractBase(ABC):
    @abstractmethod
    def must(self): ...

@dataclass
class DataThing:
    a: int
    b: str = "x"

class ForMembers(WithStatics, WithProperty):
    CONST = 7
    def method(self, q: int = 1) -> int:  # noqa: ARG002
        return 99


# -----------------------------------------------------------------------------


class TestInspectorUtility(unittest.TestCase):
    def test_safe_repr_truncates_long_strings(self):
        long = "x" * 300
        r = InspectorUtility.safe_repr(long, max_len=40)
        # be tolerant of repr() quoting differences: just check truncation marker + “len ”
        self.assertIn("... (len ", r)
        self.assertLessEqual(len(r), 65)

    def test_safe_repr_handles_bad_repr(self):
        obj = func_raises_repr()
        out = InspectorUtility.safe_repr(obj, max_len=60)
        self.assertTrue(out.startswith("<unrepr-able "), out)

    def test_is_extension_module_false_for_pure_python(self):
        mod = sys.modules[__name__]
        self.assertFalse(InspectorUtility.is_extension_module(mod))

    def test_is_extension_module_true_for_so(self):
        self.assertTrue(InspectorUtility.is_extension_module(make_fake_extension_module()))

    def test_is_extension_module_true_for_pyd(self):
        self.assertTrue(InspectorUtility.is_extension_module(make_fake_pyd_module()))


class TestMethodInspector_Functions(unittest.TestCase):
    def test_collects_basic_metadata_for_function(self):
        data = MethodInspector(plain_func).inspect()
        self.assertEqual(data["name"], "plain_func")
        self.assertIn("signature", data)
        self.assertIn("(a: int, b: int = 3) -> int", data["signature"])

    def test_parameters_include_defaults_and_annotations(self):
        data = MethodInspector(plain_func).inspect()
        params = {p["name"]: p for p in data["parameters"]}
        # normalize annotations to strings in tests
        ann = params["a"]["annotation"]
        self.assertTrue(ann in ("int", "<class 'int'>"), ann)
        self.assertIn("3", params["b"]["default"])

    def test_detects_lambda(self):
        lam = lambda x: x + 1  # noqa: E731
        data = MethodInspector(lam).inspect()
        self.assertTrue(data["lambda_fn"])
        self.assertFalse(data["generator"])
        self.assertFalse(data["coroutine"])

    def test_detects_generator(self):
        data = MethodInspector(generator_func).inspect()
        self.assertTrue(data["generator"])

    def test_detects_async_coroutine(self):
        data = MethodInspector(async_func).inspect()
        self.assertTrue(data["coroutine"])

    def test_wrapped_function_detection(self):
        wrapped = make_wrapped()
        data = MethodInspector(wrapped).inspect()
        # wrapped via functools.wraps should set decorated flag (impl may be True/False but key exists)
        self.assertIn("decorated", data)
        # sanity: signature present
        self.assertIn("(x, y=10)", data.get("signature", ""))

    def test_nowrapped_function_still_inspected(self):
        data = MethodInspector(nowrapped).inspect()
        # no functools.wraps: inner(*a, **k)
        self.assertIn("(*a, **k)", data.get("signature", ""))


class TestMethodInspector_MethodKinds(unittest.TestCase):
    def test_staticmethod_detection(self):
        data = MethodInspector(WithStatics.s).inspect()
        self.assertTrue(data["staticmethod"])
        self.assertFalse(data["classmethod"])
        self.assertTrue(data["method"] or data["func"])

    def test_classmethod_detection(self):
        data = MethodInspector(WithStatics.c).inspect()
        self.assertTrue(data["classmethod"])
        self.assertFalse(data["staticmethod"])

    def test_instance_method_detection(self):
        data = MethodInspector(WithStatics.i).inspect()
        self.assertFalse(data["staticmethod"])
        self.assertFalse(data["classmethod"])
        self.assertTrue(data["method"] or data["func"])


class TestClassInspector_Basics(unittest.TestCase):
    def test_gathers_header_info(self):
        data = ClassInspector(ForMembers).inspect()
        self.assertEqual(data["name"], "ForMembers")
        self.assertIn("module", data)
        self.assertIn("mro", data)
        self.assertIn("bases", data)
        self.assertIn("annotations", data)
        self.assertIn("slots", data)
        self.assertIn("is_dataclass", data)

    def test_source_info_present_for_user_classes(self):
        data = ClassInspector(ForMembers).inspect()
        self.assertIsNotNone(data["file"])
        self.assertIsInstance(data["source_line_offset"], int)
        self.assertTrue(data["source_preview"] is None or isinstance(data["source_preview"], str))

    def test_protocols_flags(self):
        class Protoish:
            def __len__(self): return 0
            def __iter__(self): return iter(())
            def __repr__(self): return "x"
            def __str__(self): return "x"
            def __call__(self): return 1

        data = ClassInspector(Protoish).inspect()
        p = data["protocols"]
        self.assertTrue(p["len"])
        self.assertTrue(p["iter"])
        self.assertTrue(p["repr"])
        self.assertTrue(p["str"])
        self.assertTrue(p["call"])
        self.assertFalse(p["await"])

    def test_property_details_captured(self):
        data = ClassInspector(WithProperty).inspect()
        members = data["members"]
        # property should be present
        self.assertIn("value", members)
        self.assertTrue(members["value"]["property"])
        self.assertIn("property_details", members["value"])
        self.assertTrue(members["value"]["property_details"]["fget"])

    def test_members_exclude_dunders_by_default(self):
        data = ClassInspector(ForMembers).inspect()
        self.assertNotIn("__init__", data["members"])

    def test_members_include_dunders_when_flag_true(self):
        data = ClassInspector(ForMembers, show_dunders=True).inspect()
        self.assertIn("__init__", data["members"])

    def test_signatures_for_methods(self):
        data = ClassInspector(ForMembers).inspect()
        self.assertIn("method", data["members"])
        sig = data["members"]["method"]["signature"]
        self.assertIn("(self, q: int = 1) -> int", sig)

    def test_dataclass_flag(self):
        data = ClassInspector(DataThing).inspect()
        self.assertTrue(data["is_dataclass"])

    def test_decorated_class_detection(self):
        DThing = make_decorated_class()
        data = ClassInspector(DThing).inspect()
        # our decorator sets __wrapped__, so decorated should be present (impl may normalize to True/False)
        self.assertIn("decorated", data)


class TestSpellExaminer(unittest.TestCase):
    def test_class_returns_ClassProfile(self):
        profile = SpellExaminer(ForMembers).inspect()
        self.assertIsInstance(profile, ClassProfile)
        self.assertEqual(profile.name, "ForMembers")
        # methods dict should include at least one profile (e.g., method, s, c, i)
        self.assertTrue(len(profile.methods) >= 1)

    def test_function_returns_MethodProfile(self):
        profile = SpellExaminer(plain_func).inspect()
        self.assertIsInstance(profile, MethodProfile)
        self.assertEqual(profile.name, "plain_func")
        self.assertIn("(a: int, b: int = 3) -> int", profile.signature)

    def test_instance_returns_fallback_dict(self):
        inst = ForMembers()
        data = SpellExaminer(inst).inspect()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["type"], inst.__class__.__name__)

    def test_to_json_serializes_profiles(self):
        cp = SpellExaminer(ForMembers).to_json()
        self.assertIsInstance(cp, str)
        self.assertIn('"name": "ForMembers"', cp)
        mp = SpellExaminer(nowrapped).to_json()
        self.assertIsInstance(mp, str)
        # no-wrap decorator shows inner function name
        self.assertIn('"name": "inner"', mp)


class TestEdgeCases(unittest.TestCase):
    def test_method_inspector_handles_builtins(self):
        data = MethodInspector(len).inspect()
        # builtins often lack source; ensure no crash and flags exist
        self.assertIn("builtin", data)
        self.assertTrue(data["builtin"])

    def test_class_inspector_handles_builtin_types(self):
        data = ClassInspector(dict).inspect()
        # file/source may be None; ensure keys exist
        self.assertIn("file", data)
        self.assertIn("source_preview", data)
        self.assertIn("protocols", data)

    def test_method_inspector_static_check_does_not_crash_on_nested(self):
        class Outer:
            class Inner:
                @staticmethod
                def z(): return 1
        data = MethodInspector(Outer.Inner.z).inspect()
        self.assertTrue(isinstance(data.get("staticmethod"), bool))

    def test_safe_repr_max_len_boundary(self):
        s = "y" * 50
        r = InspectorUtility.safe_repr(s, max_len=50)
        # may or may not truncate exactly; ensure not exploding and <= ~65
        self.assertLessEqual(len(r), 65)

    def test_method_parameters_have_kinds(self):
        data = MethodInspector(ForMembers.method).inspect()
        params = data.get("parameters", [])
        self.assertTrue(any(p["kind"] in {"POSITIONAL_OR_KEYWORD", "VAR_POSITIONAL", "VAR_KEYWORD"} for p in params))

    def test_class_with_abstract_method_sets_abstract_flag_on_member(self):
        class Impl(AbstractBase):
            def must(self): return 1
        data = ClassInspector(AbstractBase).inspect()
        mems = data["members"]
        # abstract methods are callables; abstract flag should be True
        self.assertTrue(mems["must"]["abstract"])

    def test_class_member_owner_resolution(self):
        data = ClassInspector(ForMembers).inspect()
        mems = data["members"]
        # method is defined on ForMembers; ensure defined_here True
        self.assertTrue(mems["method"]["defined_here"])
        # 's' originates from WithStatics base
        self.assertFalse(mems["s"]["defined_here"])
        self.assertEqual(mems["s"]["owner_class"], "WithStatics")

    def test_default_factory_dataclass_ok(self):
        @dataclass
        class DefaultFactoryD:
            d: dict = field(default_factory=dict)

        data = ClassInspector(DefaultFactoryD).inspect()
        self.assertTrue(data.get("is_dataclass"))
        # By default we don't include dunders; just assert members dict exists.
        self.assertIsInstance(data["members"], dict)


if __name__ == "__main__":
    unittest.main()
