# tests/test_spell_inspector_unittest.py
import importlib
import inspect
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


# --------------------------------------------------------------------------- #
#  Load the module under test dynamically (adjust path if needed)             #
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]          # project root
MOD_FILE = ROOT / "spell_inspector.py"              # your inspector module

spec = importlib.util.spec_from_file_location("spell_inspector", MOD_FILE)
spell_inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spell_inspector)

# pull symbols
SpellExaminer        = spell_inspector.SpellExaminer
ClassInspector       = spell_inspector.ClassInspector
MethodInspector      = spell_inspector.MethodInspector
safe_repr            = spell_inspector.safe_repr
_is_extension_module = spell_inspector._is_extension_module


# --------------------------------------------------------------------------- #
#  Helper classes / callables used in multiple tests                          #
# --------------------------------------------------------------------------- #
class Base:
    z = 9
    def foo(self): return "foo"
    @property
    def prop(self): return 42
    @classmethod
    def cmethod(cls): return "cm"

class Sub(Base):
    __slots__ = ("x",)
    def __init__(self): self.x = 1
    def bar(self, v: int) -> int: return v * 2
    @staticmethod
    def sm(): return "sm"

# lambda wrapper for lambda-detection test
def make_lambda():
    return lambda a: a + 1


# --------------------------------------------------------------------------- #
#  Test-Suite                                                                 #
# --------------------------------------------------------------------------- #
class SafeReprTests(unittest.TestCase):
    def test_truncates_and_appends_len(self):
        long = "a" * 300
        out  = safe_repr(long, max_len=50)
        self.assertTrue(out.endswith(")") or "... (len" in out)

    def test_handles_unreprable(self):
        class Bad:
            def __repr__(self): raise RuntimeError("boom")
        self.assertIn("unrepr-able", safe_repr(Bad()))


class ExtensionModuleTests(unittest.TestCase):
    def test_detects_py_module_as_false(self):
        self.assertFalse(_is_extension_module(sys.modules[__name__]))

    def test_detects_so_extension(self):
        dummy = types.ModuleType("dummy")
        dummy.__spec__ = importlib.machinery.ModuleSpec(
            "dummy", None, origin="/x/libdummy.so"
        )
        self.assertTrue(_is_extension_module(dummy))


class ClassInspectorTests(unittest.TestCase):
    def test_basic_keys_present(self):
        ci   = ClassInspector(Sub)
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
        bound   = Sub().bar
        method  = MethodInspector(bound).inspect()
        self.assertTrue(method["method"])
        lam     = make_lambda()
        laminfo = MethodInspector(lam).inspect()
        self.assertTrue(laminfo["lambda_fn"])

    def test_static_and_class_method_flags(self):
        static = MethodInspector(Sub.sm).inspect()
        self.assertTrue(static["staticmethod"])
        cmet   = MethodInspector(Sub.cmethod).inspect()
        self.assertTrue(cmet["classmethod"])

    def test_uninspectable_builtin(self):
        info = MethodInspector(len).inspect()
        self.assertTrue(info.get("uninspectable", False) or info["signature"] is None)


class SpellExaminerIntegrationTests(unittest.TestCase):
    def test_examiner_class_path(self):
        report = SpellExaminer(Sub).inspect()
        self.assertEqual(report["object_type"], "class")
        self.assertIn("members", report["class_data"])

    def test_examiner_callable_path(self):
        report = SpellExaminer(Sub().bar).inspect()
        self.assertEqual(report["object_type"], "callable")
        self.assertTrue(report["callable_data"]["method"])

    def test_examiner_fallback(self):
        obj    = Sub()
        report = SpellExaminer(obj).inspect()
        self.assertEqual(report["object_type"], "instance_or_other")
        self.assertIn("repr", report)


# --------------------------------------------------------------------------- #
#  Entry-point so `python -m unittest discover` picks this file up directly.  #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
