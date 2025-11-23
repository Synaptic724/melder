import unittest
import functools
import inspect

from melder.spellbook.spell_crafter.spell_examiner.inspectors.method_inspector import MethodInspector


# ---- Sample targets ----

def plain_fn(a, b=2) -> int:
    return a + b

def _no_wrap_decorator(fn):
    # no functools.wraps; forces closure-based unwrapping
    def inner(*a, **k):
        return fn(*a, **k)
    return inner

def _wraps_decorator(fn):
    @functools.wraps(fn)
    def inner(*a, **k):
        return fn(*a, **k)
    return inner

@_no_wrap_decorator
def wrapped_no_wrap(x, y=3):
    return x + y

@_wraps_decorator
def wrapped_with_wraps(x, y=4):
    return x + y

def gen_fn(n):
    for i in range(n):
        yield i

async def coro_fn(x):
    return x * 2

async def async_gen_fn(n):
    for i in range(n):
        yield i

lambda_fn = lambda x, y=1: x + y  # noqa: E731


class MethodBag:
    def inst(self, a, b=1):
        return a + b

    @staticmethod
    def sm(z=3):
        return z * 10

    @classmethod
    def cm(cls, z=3):
        return z


def make_closure_fn():
    outside = {"v": 123}
    def inner(t):
        # capture outside into closure
        return t + outside["v"]
    return inner


class TestMethodInspector(unittest.TestCase):

    # ---------- Basic header/meta ----------

    def test_header_fields_present_for_plain(self):
        mi = MethodInspector(plain_fn).inspect()
        self.assertEqual(mi["name"], "plain_fn")
        self.assertIn("qualname", mi)
        self.assertEqual(mi["module"], plain_fn.__module__)
        self.assertIsInstance(mi["id"], int)
        self.assertEqual(mi["type"], type(plain_fn).__name__)
        self.assertIn("repr", mi)
        self.assertIn("builtin_mod", mi)
        self.assertIn("extension_mod", mi)

    # ---------- Source info ----------

    def test_source_fields_present(self):
        mi = MethodInspector(plain_fn).inspect()
        self.assertEqual(mi["file"], inspect.getfile(plain_fn))
        self.assertIsInstance(mi["src_offset"], int)
        self.assertIsInstance(mi["preview"], str)
        self.assertTrue(len(mi["preview"]) > 0)

    # ---------- Signature & parameters (unwrapped is primary) ----------

    def test_signature_for_plain(self):
        mi = MethodInspector(plain_fn).inspect()
        # includes return annotation
        self.assertEqual(mi["signature"], "(a, b=2) -> int")
        ps = mi["parameters"]
        self.assertEqual([p["name"] for p in ps], ["a", "b"])
        self.assertEqual(ps[1]["default"], "2")

    def test_signature_unwraps_no_wrap_decorator(self):
        mi = MethodInspector(wrapped_no_wrap).inspect()
        self.assertEqual(mi["signature"], "(x, y=3)")
        self.assertTrue(mi["decorated"])
        self.assertIn("wrapped_repr", mi)
        self.assertIsNotNone(mi["wrapped_repr"])

    def test_signature_unwraps_with_wraps(self):
        mi = MethodInspector(wrapped_with_wraps).inspect()
        self.assertEqual(mi["signature"], "(x, y=4)")
        self.assertTrue(mi["decorated"])
        self.assertIn("wrapped_repr", mi)
        self.assertIsNotNone(mi["wrapped_repr"])

    # ---------- Traits for different callable kinds ----------

    def test_traits_plain_function(self):
        mi = MethodInspector(plain_fn).inspect()
        self.assertTrue(mi["func"])
        self.assertFalse(mi["method"])
        self.assertFalse(mi["staticmethod"])
        self.assertFalse(mi["classmethod"])
        self.assertFalse(mi["generator"])
        self.assertFalse(mi["async_gen"])
        self.assertFalse(mi["coroutine"])
        self.assertFalse(mi["lambda_fn"])
        self.assertFalse(mi["abstract"])

    def test_traits_bound_method(self):
        obj = MethodBag()
        mi = MethodInspector(obj.inst).inspect()
        self.assertTrue(mi["method"])
        self.assertFalse(mi["func"])
        self.assertFalse(mi["staticmethod"])
        self.assertFalse(mi["classmethod"])

    def test_traits_staticmethod_detection(self):
        mi = MethodInspector(MethodBag.sm).inspect()
        self.assertFalse(mi["method"])
        self.assertTrue(mi["staticmethod"])
        self.assertFalse(mi["classmethod"])
        self.assertEqual(mi["name"], "sm")
        self.assertEqual(mi["signature"], "(z=3)")

    def test_traits_classmethod_detection_bound(self):
        mi = MethodInspector(MethodBag.cm).inspect()
        # Depending on how inspect binds it, classmethod is detected by ismethod + __self__ being a type
        self.assertTrue(mi["classmethod"])
        self.assertEqual(mi["name"], "cm")
        # Accessed via the class => signature hides 'cls'
        self.assertEqual(mi["signature"], "(z=3)")

    def test_lambda_detection(self):
        mi = MethodInspector(lambda_fn).inspect()
        self.assertTrue(mi["lambda_fn"])
        self.assertEqual(mi["signature"], "(x, y=1)")

    def test_generator_detection(self):
        mi = MethodInspector(gen_fn).inspect()
        self.assertTrue(mi["generator"])
        self.assertFalse(mi["coroutine"])
        self.assertFalse(mi["async_gen"])

    def test_coroutine_detection(self):
        mi = MethodInspector(coro_fn).inspect()
        self.assertTrue(mi["coroutine"])
        self.assertFalse(mi["generator"])
        self.assertFalse(mi["async_gen"])

    def test_async_gen_detection(self):
        mi = MethodInspector(async_gen_fn).inspect()
        self.assertTrue(mi["async_gen"])
        self.assertFalse(mi["generator"])
        self.assertFalse(mi["coroutine"])

    # ---------- Closure capture ----------

    def test_closure_preview_present(self):
        f = make_closure_fn()
        mi = MethodInspector(f).inspect()
        self.assertIn("closure", mi)
        self.assertIsInstance(mi["closure"], list)
        self.assertTrue(len(mi["closure"]) >= 1)
        self.assertTrue(all(isinstance(x, str) for x in mi["closure"]))

    # ---------- Decoration bookkeeping ----------

    def test_decorated_false_for_plain(self):
        mi = MethodInspector(plain_fn).inspect()
        self.assertFalse(mi["decorated"])
        self.assertIsNone(mi["wrapped_repr"])

    def test_decorated_true_for_manual_wrapped_chain(self):
        def base(): return "ok"
        def wrapper(): return base()
        wrapper.__wrapped__ = base  # simulate manual tagging
        mi = MethodInspector(wrapper).inspect()
        self.assertTrue(mi["decorated"])
        self.assertIn("wrapped_repr", mi)
        self.assertIsNotNone(mi["wrapped_repr"])

    # ---------- Repr safety routed through utility ----------

    def test_repr_is_safe_and_short(self):
        def very_long_name_function_with_many_characters_and_params(
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=1,
        ):
            return 1
        mi = MethodInspector(very_long_name_function_with_many_characters_and_params).inspect()
        self.assertIn("repr", mi)
        self.assertIsInstance(mi["repr"], str)
        self.assertTrue(len(mi["repr"]) <= 120 or "... (len " in mi["repr"])

    # ---------- Uninspectable fallback (robustness) ----------

    def test_uninspectable_flag_when_signature_raises(self):
        original = inspect.signature

        def boom_signature(_):
            raise ValueError("no sig for you")

        try:
            inspect.signature = boom_signature
            mi = MethodInspector(plain_fn).inspect()
            self.assertTrue(mi["uninspectable"])
        finally:
            inspect.signature = original


if __name__ == "__main__":
    unittest.main()
