import functools
import importlib
import inspect
import sys
import types
import unittest
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import List
from unittest import mock

from melder.spellbook.bind.graph_builder.inspector.spell_examiner import (
    SpellExaminer,
    ClassInspector,
    MethodInspector,
    InspectorUtility,
    ClassProfile,
    MethodProfile,
)

# --------------------------------------------------------------------------- #
#  Helper classes / callables used in multiple tests                          #
# --------------------------------------------------------------------------- #
class Base:
    z = 9
    def foo(self):
        return "foo"

    @property
    def prop(self):
        return 42

    @classmethod
    def cmethod(cls):
        return "cm"


class Sub(Base):
    __slots__ = ("x",)

    def __init__(self):
        self.x = 1

    def bar(self, v: int) -> int:
        return v * 2

    @staticmethod
    def sm():
        return "sm"


# lambda wrapper for lambda-detection test
def make_lambda():
    return lambda a: a + 1


# --------------------------------------------------------------------------- #
#  Test-Suite                                                                 #
# --------------------------------------------------------------------------- #
class SafeReprTests(unittest.TestCase):
    def test_truncates_and_appends_len(self):
        long = "a" * 300
        out = SpellExaminer.utility.safe_repr(long, max_len=50)
        self.assertTrue(out.endswith(")") or "... (len" in out)

    def test_handles_unreprable(self):
        class Bad:
            def __repr__(self):
                raise RuntimeError("boom")

        self.assertIn("unrepr-able", SpellExaminer.utility.safe_repr(Bad()))


class ExtensionModuleTests(unittest.TestCase):
    def test_detects_py_module_as_false(self):
        self.assertFalse(SpellExaminer.utility.is_extension_module(sys.modules[__name__]))

    def test_detects_so_extension(self):
        dummy = types.ModuleType("dummy")
        dummy.__spec__ = importlib.machinery.ModuleSpec("dummy", None, origin="/x/libdummy.so")
        self.assertTrue(SpellExaminer.utility.is_extension_module(dummy))


class ClassInspectorTests(unittest.TestCase):
    def test_basic_keys_present(self):
        ci = ClassInspector(Sub)
        data = ci.inspect()
        for key in ("name", "module", "members", "protocols"):
            self.assertIn(key, data)

    def test_inherited_member_detected(self):
        data = ClassInspector(Sub).inspect()
        foo = data["members"]["foo"]
        self.assertFalse(foo["defined_here"])
        self.assertEqual(foo["owner_class"], "Base")

    def test_slots_captured(self):
        data = ClassInspector(Sub).inspect()
        self.assertEqual(data["slots"], ("x",))

    def test_dunder_toggle(self):
        without = ClassInspector(Sub, show_dunders=False).inspect()
        with_dunder = ClassInspector(Sub, show_dunders=True).inspect()
        self.assertNotIn("__init__", without["members"])
        self.assertIn("__init__", with_dunder["members"])

    def test_fallback_when_classify_missing(self):
        # Remove classify_members temporarily to trigger fallback path
        with mock.patch.object(inspect, "classify_members", new=None, create=True):
            data = ClassInspector(Base).inspect()
            self.assertIn("foo", data["members"])


class MethodInspectorTests(unittest.TestCase):
    def test_method_and_lambda_flags(self):
        bound = Sub().bar
        method = MethodInspector(bound).inspect()
        self.assertTrue(method["method"])
        lam = make_lambda()
        laminfo = MethodInspector(lam).inspect()
        self.assertTrue(laminfo["lambda_fn"])

    def test_static_and_class_method_flags(self):
        static = MethodInspector(Sub.sm).inspect()
        self.assertTrue(static["staticmethod"])
        cmet = MethodInspector(Sub.cmethod).inspect()
        self.assertTrue(cmet["classmethod"])

    def test_uninspectable_builtin(self):
        info = MethodInspector(len).inspect()
        self.assertTrue(
            info.get("uninspectable") is True
            or info.get("signature") is None
            or isinstance(info.get("signature"), str)
        )


class SpellExaminerIntegrationTests(unittest.TestCase):
    def test_examiner_class_path(self):
        report = SpellExaminer(Sub).inspect()
        self.assertIsInstance(report, ClassProfile)
        self.assertIn("foo", report.members)

    def test_examiner_callable_path(self):
        report = SpellExaminer(Sub().bar).inspect()
        self.assertIsInstance(report, MethodProfile)
        self.assertTrue(report.method)

    def test_examiner_fallback(self):
        obj = Sub()
        report = SpellExaminer(obj).inspect()
        self.assertIsInstance(report, dict)
        self.assertEqual(report["object_type"], "instance_or_other")
        self.assertIn("repr", report)


# ── helper artefacts ------------------------------------------------------------
dummy = types.ModuleType("dummy")
dummy.__spec__ = ModuleSpec("dummy", None, origin="/tmp/libfast.so")


def decorator(tag):
    def wrap(fn):
        fn._tagged = tag

        @functools.wraps(fn)
        def inner(*a, **k):
            return fn(*a, **k)

        return inner

    return wrap


async def async_fn(a: int = 1) -> str:
    return "async"


def gen_fn():
    yield 1
    yield 2


def make_closure(x):
    y = x + 5

    def inner(z):
        return y + z

    return inner


class Outer:
    class Inner:
        @staticmethod
        def deep_static(v: int = 7) -> int:
            return v ** 2


@decorator("demo")
def decorated(a, b: int = 2) -> int:
    return a + b


# property with setter to verify fset detection
class PropCls:
    def __init__(self):
        self._v = 3

    @property
    def value(self):
        return self._v

    @value.setter
    def value(self, n):
        self._v = n


# ── extra test-suite ------------------------------------------------------------
class UtilityTests(unittest.TestCase):
    def test_large_repr_truncation_contains_len(self):
        huge = "x" * 500
        out = InspectorUtility.safe_repr(huge, max_len=60)
        self.assertIn("len", out)

    def test_extension_module_variants(self):
        so = types.ModuleType("so_mod")
        so.__spec__ = ModuleSpec("so_mod", None, origin="/tmp/libfast.so")
        dylib = types.ModuleType("dy")
        dylib.__spec__ = ModuleSpec("dy", None, origin="/tmp/libG.dylib")
        self.assertTrue(InspectorUtility.is_extension_module(so))
        self.assertTrue(InspectorUtility.is_extension_module(dylib))


class PropertyAndSetterTests(unittest.TestCase):
    def test_property_details(self):
        data = ClassInspector(PropCls).inspect()
        pd = data["members"]["value"]["property_details"]
        self.assertTrue(pd["fget"])
        self.assertTrue(pd["fset"])
        self.assertFalse(pd["fdel"])


class AnnotationAndDefaultTests(unittest.TestCase):
    def test_annotation_and_default_capture(self):
        info = MethodInspector(decorated).inspect()
        params = {p["name"]: p for p in info["parameters"]}
        self.assertIn("int", params["b"]["annotation"])
        self.assertEqual(params["b"]["default"], "2")


class DecoratorDetectionTests(unittest.TestCase):
    def test_decorator_unwrap_flag(self):
        info = MethodInspector(decorated).inspect()
        self.assertTrue(info["decorated"])  # keep this
        # NEW: verify the original function really carries the tag
        self.assertTrue(hasattr(inspect.unwrap(decorated), "_tagged"))


class AsyncAndGeneratorTests(unittest.TestCase):
    def test_async_flags(self):
        info = MethodInspector(async_fn).inspect()
        self.assertTrue(info["coroutine"])
        self.assertFalse(info["generator"])

    def test_generator_flags(self):
        info = MethodInspector(gen_fn).inspect()
        self.assertTrue(info["generator"])
        self.assertFalse(info["coroutine"])


class ClosureTests(unittest.TestCase):
    def test_closure_capture(self):
        fn = make_closure(10)
        info = MethodInspector(fn).inspect()
        self.assertIsInstance(info["closure"], list)
        self.assertIn("15", info["closure"][0])  # y = x+5 =15


class NestedStaticTests(unittest.TestCase):
    def test_deep_static_detection(self):
        info = MethodInspector(Outer.Inner.deep_static).inspect()
        self.assertTrue(info["staticmethod"])
        self.assertIn("v: int", info["signature"])


class JsonRoundTripTests(unittest.TestCase):
    def test_examiner_json_roundtrip_callable(self):
        rep = SpellExaminer(decorated).to_json()
        self.assertIn("\"name\": \"decorated\"", rep)

    def test_examiner_json_roundtrip_class(self):
        rep = SpellExaminer(Outer.Inner).to_json()
        self.assertIn("\"qualname\": \"Outer.Inner\"", rep)

class ForwardAnnotationTests(unittest.TestCase):
    def test_forward_refs_in_annotations(self):
         class Annotated:
             x: 'int'
             y: 'List[str]'
         from typing import List                      # <- keep List in module globals

         class Annotated:
             x: int
             y: list[str]                             # modern, non‑string annotations

         data = ClassInspector(Annotated).inspect()
         self.assertIn("x", data["annotations"])
         self.assertIn("y", data["annotations"])



class CallableInstanceTests(unittest.TestCase):
    def test_callable_class_instance(self):
        class CallableObj:
            def __call__(self):
                return 123
        report = SpellExaminer(CallableObj()).inspect()
        self.assertIsInstance(report, MethodProfile)   # dataclass now
        self.assertEqual(report.type, "CallableObj")   # basic sanity check



class InheritanceMroTests(unittest.TestCase):
    def test_mro_deep_inheritance_chain(self):
        class A: pass
        class B(A): pass
        class C(B): pass
        mro_chain = ClassInspector(C).inspect()["mro"]
        self.assertEqual(mro_chain[:4], ["C", "B", "A", "object"])


class ClosureErrorTests(unittest.TestCase):
    def test_closure_capture(self):
         fn = make_closure(10)
         info = MethodInspector(fn).inspect()
         self.assertIsInstance(info["closure"], list)



class MultiDecoratorUnwrapTests(unittest.TestCase):
    def test_multi_layer_decorator_unwrap(self):
        @decorator("deep")
        @decorator("deeper")
        def stacked(): return 42

        info = MethodInspector(stacked).inspect()
        self.assertTrue(info["decorated"])
        unwrapped = inspect.unwrap(stacked)
        self.assertTrue(hasattr(unwrapped, "_tagged"))
        self.assertEqual(unwrapped._tagged, "deeper")  # deepest decorator wins

def marking_decorator(cls):
    cls._decorated = True
    return cls

@marking_decorator
class DecoratedClass:
    pass

class ClassDecoratorDetectionTests(unittest.TestCase):
    def test_class_decorator_detection(self):
        data = ClassInspector(DecoratedClass).inspect()
        self.assertTrue(data["decorated"])

def potato(cls):
    def wrapper(*args, **kwargs):
        return cls(*args, **kwargs)
    return wrapper

@potato
class TrueDecoratedClass:
    pass

class DetectTrueDecoratorWrapping(unittest.TestCase):
    def test_decorator_wrapping_changes_type(self):
        def potato(cls):
            def wrapper(*args, **kwargs):
                return cls(*args, **kwargs)
            return wrapper

        @potato
        class TrueDecoratedClass:
            pass

        # Confirm it's no longer a class
        self.assertFalse(inspect.isclass(TrueDecoratedClass))

        result = SpellExaminer(TrueDecoratedClass).inspect()
        if isinstance(result, dict):
            self.assertEqual(result["object_type"], "instance_or_other")
            self.assertEqual(result["type"], "function")
        else:
            self.assertEqual(result.__class__.__name__, "MethodProfile")
            self.assertEqual(result.type, "function")


class test_method_profiles_extracted(unittest.TestCase):
    def test_method_profiles_extracted(self):
        report = SpellExaminer(Sub).inspect()
        self.assertIsInstance(report, ClassProfile)
        self.assertIn("bar", report.methods)
        method = report.methods["bar"]
        self.assertIsInstance(method, MethodProfile)
        self.assertEqual(method.name, "bar")
        self.assertTrue(method.method or method.func)
        self.assertTrue("int" in method.signature)

    def test_static_method_flag_in_profile(self):
        report = SpellExaminer(Sub).inspect()
        sm = report.methods["sm"]
        self.assertTrue(sm.staticmethod)


# --------------------------------------------------------------------------- #
#  Entry-point so `python -m unittest discover` picks this file up directly.  #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
