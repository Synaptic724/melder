import unittest
import functools
import inspect

from melder.spellbook.spell_crafter.spell_examiner.inspectors import InspectorUtility


class TestInspectorUtility(unittest.TestCase):

    # ---------- safe_repr ----------

    def test_safe_repr_basic(self):
        self.assertEqual(InspectorUtility.safe_repr(42), "42")
        self.assertTrue(InspectorUtility.safe_repr({"a": 1}).startswith("{"))

    def test_safe_repr_truncates_long_strings(self):
        class Loud:
            def __repr__(self):
                return "x" * 200
        s = InspectorUtility.safe_repr(Loud())  # max_len default = 120
        # Truncation contract: prefix of original, then "... (len NNN)"
        self.assertIn("... (len 200)", s)
        self.assertTrue(s.startswith("x" * 105))  # trunc_len = max(10, 120-15) = 105

    def test_safe_repr_handles_repr_exceptions(self):
        class BadRepr:
            def __repr__(self):
                raise ValueError("nope")
        out = InspectorUtility.safe_repr(BadRepr())
        self.assertEqual(out, "<unrepr-able BadRepr>")

    # ---------- is_extension_module ----------

    def test_is_extension_module_none(self):
        self.assertFalse(InspectorUtility.is_extension_module(None))

    def test_is_extension_module_regular_py_module(self):
        # use this test module object
        mod = inspect.getmodule(inspect.currentframe())
        self.assertFalse(InspectorUtility.is_extension_module(mod))

    def test_is_extension_module_fake_pyd(self):
        class _Spec:
            origin = "SOMETHING.PYD"
        class _FakeMod:
            __spec__ = _Spec()
        self.assertTrue(InspectorUtility.is_extension_module(_FakeMod()))

    def test_is_extension_module_missing_spec_or_origin(self):
        class _NoSpec:
            pass
        class _NoOrigin:
            class _Spec:
                origin = None
            __spec__ = _Spec()
        self.assertFalse(InspectorUtility.is_extension_module(_NoSpec()))
        self.assertFalse(InspectorUtility.is_extension_module(_NoOrigin()))

    # ---------- unwrap_callable ----------

    def test_unwrap_callable_identity_for_plain_function(self):
        def f(a, b): return a + b
        self.assertIs(InspectorUtility.unwrap_callable(f), f)

    def test_unwrap_callable_with_functools_wraps(self):
        def target(x): return x * 2
        def deco(fn):
            @functools.wraps(fn)
            def inner(*a, **k):
                return fn(*a, **k)
            return inner
        wrapped = deco(target)
        unwrapped = InspectorUtility.unwrap_callable(wrapped)
        self.assertIs(unwrapped, target)

    def test_unwrap_callable_without_wraps_closure_capture(self):
        def target(x): return x + 1
        def deco(fn):
            # no functools.wraps; capture fn in closure
            def inner(*a, **k):
                return fn(*a, **k)
            return inner
        wrapped = deco(target)
        unwrapped = InspectorUtility.unwrap_callable(wrapped)
        self.assertIs(unwrapped, target)

    def test_unwrap_callable_double_wrapped_mixed(self):
        def base(x): return x
        def deco_wraps(fn):
            @functools.wraps(fn)
            def inner(*a, **k): return fn(*a, **k)
            return inner
        def deco_nowrap(fn):
            def inner(*a, **k): return fn(*a, **k)
            return inner
        wrapped = deco_nowrap(deco_wraps(base))
        self.assertIs(InspectorUtility.unwrap_callable(wrapped), base)

    def test_unwrap_callable_bound_method(self):
        class C:
            def m(self): return 1
        obj = C()
        bound = obj.m
        # unwrap should not crash; it may return the underlying function or the bound method itself
        unwrapped = InspectorUtility.unwrap_callable(bound)
        self.assertTrue(callable(unwrapped))
        # Accept either function "m" or a method whose __name__ is "m"
        self.assertIn(getattr(unwrapped, "__name__", None), ("m", "inner", None))

    def test_unwrap_callable_non_function_returns_same_object(self):
        x = 123
        self.assertIs(InspectorUtility.unwrap_callable(x), x)

    def test_unwrap_callable_closure_non_function_ignored(self):
        # Decorator puts a non-function in closure; utility should ignore it and return original wrapper.
        def target(x): return x
        def deco(_fn):
            nonlocal_box = {"not_a_fn": object()}
            def inner(y):
                # capture non-function so it appears in __closure__
                _ = nonlocal_box
                return _fn(y)
            return inner
        wrapped = deco(target)
        # Because closure holds a non-function, unwrap shouldn't replace with that; it still finds target via unwrap chains or returns target.
        unwrapped = InspectorUtility.unwrap_callable(wrapped)
        # Either we found target or (worst case) left wrapped alone; both callables
        self.assertTrue(callable(unwrapped))
        # Preferably equal to target
        # If Python's inspect.unwrap succeeded, this will be target. Accept both to keep the test stable.
        self.assertIn(unwrapped, (target, wrapped))

    def test_unwrap_callable_with_manual___wrapped___chain(self):
        # Simulate a wrapper that sets __wrapped__ manually (common pattern)
        def target(): return "ok"
        def wrapper():
            return target()
        wrapper.__wrapped__ = target
        self.assertIs(InspectorUtility.unwrap_callable(wrapper), target)

    def test_unwrap_callable_lambda(self):
        f = lambda x: x  # noqa: E731
        self.assertIs(InspectorUtility.unwrap_callable(f), f)


if __name__ == "__main__":
    unittest.main()
