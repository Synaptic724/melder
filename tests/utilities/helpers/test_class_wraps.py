import unittest
import inspect
from melder.utilities.helpers.class_wraps import class_wraps

class BaseA: ...
class BaseB: ...


class TestClassWraps(unittest.TestCase):

    # 1 — basic metadata is attached
    def test_metadata_flags_and_wrapped_target(self):
        def dec(c):  # trivial class decorator
            return c
        wrapped = class_wraps(BaseA, "demo")(dec)

        self.assertTrue(getattr(wrapped, "__is_wrapped__", False))
        self.assertIs(getattr(wrapped, "__wrapped__", None), BaseA)
        self.assertEqual(getattr(wrapped, "__decorator_name__", None), "demo")

    # 2 — decorator_name is optional and absent when not provided
    def test_decorator_name_optional(self):
        def dec(c): return c
        wrapped = class_wraps(BaseB)(dec)
        self.assertTrue(getattr(wrapped, "__is_wrapped__", False))
        self.assertIs(getattr(wrapped, "__wrapped__", None), BaseB)
        self.assertFalse(hasattr(wrapped, "__decorator_name__"))

    # 3 — update_wrapper() preserves name and docstring from the original decorator
    def test_update_wrapper_propagates_name_and_doc(self):
        def original_decorator(c):
            """original-doc"""
            return c
        original_decorator.__name__ = "original_decorator"

        wrapped = class_wraps(BaseA, "x")(original_decorator)

        self.assertEqual(wrapped.__name__, "original_decorator")
        self.assertEqual(wrapped.__doc__, "original-doc")

    # 4 — inspect.unwrap prefers our __wrapped__ (the original class), not the decorator fn
    def test_inspect_unwrap_targets_original_class(self):
        def dec(c): return c
        wrapped = class_wraps(BaseA, "u")(dec)
        self.assertIs(inspect.unwrap(wrapped), BaseA)

    # 5 — using as a class decorator that mutates in place
    def test_usage_mutate_in_place(self):
        def add_tag(cls):
            cls.TAG = "T"
            return cls

        add_tag_wrapped = class_wraps(BaseA, "add_tag")(add_tag)

        @add_tag_wrapped
        class Child(BaseA):
            pass

        self.assertTrue(hasattr(Child, "TAG"))
        self.assertEqual(Child.TAG, "T")
        # base class untouched
        self.assertFalse(hasattr(BaseA, "TAG"))

    # 6 — using as a class decorator that returns a new class
    def test_usage_return_new_class(self):
        def replace_with_subclass(cls):
            class NewCls(cls):
                REPLACED = True
            return NewCls

        deco = class_wraps(BaseB, "replace")(replace_with_subclass)

        @deco
        class Something(BaseB):
            pass

        # The resulting class is a new subclass with the marker attribute
        self.assertTrue(getattr(Something, "REPLACED", False))
        self.assertTrue(issubclass(Something, BaseB))

    # 7 — multiple different original_cls do not cross-contaminate
    def test_independent_wrapped_targets(self):
        def d1(c): return c
        def d2(c): return c

        w1 = class_wraps(BaseA, "A")(d1)
        w2 = class_wraps(BaseB, "B")(d2)

        self.assertIs(w1.__wrapped__, BaseA)
        self.assertIs(w2.__wrapped__, BaseB)
        self.assertEqual(w1.__decorator_name__, "A")
        self.assertEqual(w2.__decorator_name__, "B")

    # 8 — decorated class identity equals decorator return value
    def test_result_class_is_decorator_return(self):
        sentinel = object()

        def dec(cls):
            # attach sentinel to ensure exact returned object is used
            cls.__sentinel__ = sentinel
            return cls

        wrapped = class_wraps(BaseA, "sent")(dec)

        @wrapped
        class Foo(BaseA):
            pass

        self.assertIs(getattr(Foo, "__sentinel__", None), sentinel)

    # 9 — works with classes not related to original_cls (no enforcement; just metadata)
    def test_wrapped_original_cls_is_metadata_only(self):
        def add_attr(cls):
            cls.X = 1
            return cls

        wrapped = class_wraps(BaseA, "meta-only")(add_attr)

        class Unrelated:  # not subclassing BaseA
            pass

        Decorated = wrapped(Unrelated)
        self.assertEqual(Decorated.X, 1)
        self.assertIs(wrapped.__wrapped__, BaseA)  # still points to BaseA

    # 10 — multiple stacked uses of class_wraps preserve each one’s metadata independently
    def test_stacking_two_wrappers(self):
        def dec1(c):
            c.A = True
            return c

        def dec2(c):
            c.B = True
            return c

        w1 = class_wraps(BaseA, "first")(dec1)
        w2 = class_wraps(BaseB, "second")(dec2)

        @w2
        @w1
        class Target(BaseA):
            pass

        self.assertTrue(Target.A)
        self.assertTrue(Target.B)
        self.assertIs(w1.__wrapped__, BaseA)
        self.assertIs(w2.__wrapped__, BaseB)
        self.assertEqual(w1.__decorator_name__, "first")
        self.assertEqual(w2.__decorator_name__, "second")


if __name__ == "__main__":
    unittest.main()
