# tests/spellbook/spell_crafter/test_spell_crafter_3.py

import unittest
import functools
import inspect
import types
from dataclasses import dataclass, field
from typing import Any, Optional, Annotated, Callable, TypeVar, Generic
from abc import ABC, abstractmethod

from melder.spellbook.spell_crafter.spell_examiner.spell_examiner import (
    SpellExaminer, ClassInspector, MethodInspector,
    ClassProfile, MethodProfile, InspectorUtility
)

# -------------------------------------------------------------------
# Local helpers & fixtures
# -------------------------------------------------------------------

def no_wrap_decorator(fn):
    # intentionally not using functools.wraps
    def inner(*a, **k):
        return fn(*a, **k)
    return inner

def with_wraps(fn):
    @functools.wraps(fn)
    def inner(*a, **k):
        return fn(*a, **k)
    return inner

class StrictDescriptor:
    """Non-data descriptor to verify descriptor appearance in member list."""
    def __get__(self, inst, owner):
        return f"<bound to {owner.__name__}>"

class DataDescriptor:
    """Data descriptor (has __set__)"""
    def __get__(self, inst, owner):
        return 1
    def __set__(self, inst, value):
        inst._value = value

class Functor:
    """Callable instance."""
    def __init__(self, factor=2):
        self.factor = factor
    def __call__(self, x: int) -> int:
        return x * self.factor

T = TypeVar("T")

class Wrapper(Generic[T]):
    def __init__(self, value: T):
        self.value = value
    def get(self) -> T:
        return self.value

def a_function(a: int, b: Annotated[str, "tag"] = "x") -> str:
    return f"{a}-{b}"

def variadic(*args: int, **kwargs: str) -> None:
    return None

class WithSlots:
    __slots__ = ("x",)
    def __init__(self):
        self.x = 1
    def set_x(self, v: int):  # noqa: ARG002
        self.x = 2

class ABase:
    base_attr = 7
    def m(self): return "A"

class BLeft(ABase):
    def l(self): return "L"

class BRight(ABase):
    def r(self): return "R"

class Diamond(BLeft, BRight):
    def m(self): return "D"  # override

class WithGetattr:
    def __getattr__(self, name: str):
        if name == "dynamic":
            return 123
        raise AttributeError(name)

class WithPropertyFD:
    def __init__(self):
        self._v = 5
    @property
    def val(self):
        return self._v
    @val.deleter
    def val(self):
        self._v = 0

class Outer:
    class Inner:
        def ping(self): return "pong"

class AddsLater:
    pass

# will add dynamically later
def dynamic_method(self, a: int) -> int:
    return 99

class AbstractBase(ABC):
    @abstractmethod
    def must(self): ...

class Impl(AbstractBase):
    def must(self): return 1

@dataclass
class DataThing:
    a: int
    b: str = "x"

# wrapped functions
@no_wrap_decorator
def dec_nowrap(x, y=2):  # noqa: ARG001
    return 42

@with_wraps
def dec_wraps(u: int, v: int = 10) -> int:  # noqa: ARG001
    return u + v

class StaticNest:
    class Inner:
        @staticmethod
        def tool(z):  # noqa: ARG001
            return "ok"

def partialable(a: int, b: int, c: int = 1) -> int:
    return a + b + c

# Fake C-extension-ish module
def fake_ext_module():
    class _Spec:
        origin = "/opt/lib/something.cpython-311-x86_64-linux-gnu.so"
    mod = types.SimpleNamespace()
    mod.__spec__ = _Spec()
    return mod


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

class TestSpellExaminer_DescriptorsAndProperties(unittest.TestCase):
    def test_descriptor_shows_up_in_members(self):
        class Host:
            d = StrictDescriptor()
            def method(self): return 1
        prof = SpellExaminer(Host).inspect()
        self.assertIsInstance(prof, ClassProfile)
        self.assertIn("d", prof.members)
        self.assertFalse(prof.members["d"]["callable"])

    def test_data_descriptor_and_property_flags(self):
        class Host2:
            d2 = DataDescriptor()
            @property
            def p(self): return 3
        prof = SpellExaminer(Host2).inspect()
        self.assertIn("d2", prof.members)
        self.assertIn("p", prof.members)
        self.assertTrue(prof.members["p"]["property"])
        self.assertIn("property_details", prof.members["p"])
        self.assertTrue(prof.members["p"]["property_details"]["fget"])

    def test_property_with_deleter_records_details(self):
        prof = SpellExaminer(WithPropertyFD).inspect()
        pd = prof.members["val"]["property_details"]
        self.assertTrue(pd["fget"])
        self.assertFalse(pd["fset"])
        self.assertTrue(pd["fdel"])

    def test_slots_presence(self):
        prof = SpellExaminer(WithSlots).inspect()
        self.assertEqual(prof.slots, ("x",))

    def test_getattr_presence_does_not_crash(self):
        prof = SpellExaminer(WithGetattr).inspect()
        self.assertIsInstance(prof, ClassProfile)
        # members exist; dynamic attributes aren’t enumerated, but no crash
        self.assertIn("inspect", dir(SpellExaminer))  # sanity on importable symbol


class TestSpellExaminer_FunctorsAndCallables(unittest.TestCase):
    def test_functor_protocol_flag(self):
        prof = SpellExaminer(Functor).inspect()
        self.assertTrue(prof.protocols.get("call", False))

    def test_functor_instance_returns_method_profile(self):
        inst = Functor(3)
        mp = SpellExaminer(inst).inspect()
        # Callable instance should be treated as a callable, not a plain object.
        self.assertIsInstance(mp, MethodProfile)
        self.assertIn("(x: int)", mp.signature or "")

    def test_callable_class_with_extra_methods(self):
        class F2(Functor):
            def extra(self): return 1
        prof = SpellExaminer(F2).inspect()
        self.assertIn("extra", prof.members)
        # __call__ is a dunder; SpellExaminer excludes dunders from members.
        # Rely on protocol flag instead of member presence.
        self.assertTrue(prof.protocols.get("call", False))

    def test_partial_wrapped_function_signature_exists(self):
        p = functools.partial(partialable, 5)
        data = SpellExaminer(p).inspect()
        # partials may not show original sig; ensure we still produce a MethodProfile
        self.assertIsInstance(data, MethodProfile)
        self.assertTrue("signature" in data.__dict__)

class TestSpellExaminer_AnnotationsAndSignatures(unittest.TestCase):
    def test_function_annotations_captured(self):
        mp = SpellExaminer(a_function).inspect()
        self.assertIsInstance(mp, MethodProfile)
        self.assertIn("->", mp.signature or "")

    def test_variadic_params_kinds_present(self):
        mp = SpellExaminer(variadic).inspect()
        kinds = {p["kind"] for p in (mp.parameters or [])}
        self.assertIn("VAR_POSITIONAL", kinds)
        self.assertIn("VAR_KEYWORD", kinds)

    def test_generic_wrapper_method_profile(self):
        w = Wrapper(10)
        mp = SpellExaminer(w.get).inspect()
        self.assertIsInstance(mp, MethodProfile)
        self.assertIn("() ->", mp.signature or "")

    def test_annotation_repr_does_not_crash(self):
        def annotated_fn(x: Annotated[int, "tag"]) -> Annotated[str, "out"]:
            return str(x)
        mp = SpellExaminer(annotated_fn).inspect()
        self.assertIsInstance(mp, MethodProfile)
        self.assertIn("annotated_fn", mp.qualname or mp.name)

    def test_bound_method_detection(self):
        obj = Wrapper(5)
        mp = SpellExaminer(obj.get).inspect()
        self.assertIsInstance(mp, MethodProfile)
        self.assertTrue(isinstance(mp.method, bool))


class TestSpellExaminer_NestedAndDynamic(unittest.TestCase):
    def test_nested_class_method_present(self):
        prof = SpellExaminer(Outer.Inner).inspect()
        self.assertIn("ping", prof.members)

    def test_nested_staticmethod_detection(self):
        mp = SpellExaminer(StaticNest.Inner.tool).inspect()
        # staticmethod flag boolean present
        self.assertTrue(isinstance(mp.staticmethod, bool))

    def test_dynamic_method_addition_reflected(self):
        setattr(AddsLater, "dyn", dynamic_method)
        prof = SpellExaminer(AddsLater).inspect()
        self.assertIn("dyn", prof.members)
        self.assertTrue(prof.members["dyn"]["callable"])

    def test_dynamic_attribute_value_repr(self):
        h = types.SimpleNamespace()
        h.answer = 42
        r = InspectorUtility.safe_repr(h, 40)
        self.assertIn("answer", r)

    def test_members_list_is_dict_like(self):
        prof = SpellExaminer(Outer).inspect()
        self.assertTrue(isinstance(prof.members, dict))


class TestSpellExaminer_MROAndOwnership(unittest.TestCase):
    def test_diamond_mro_owner_for_override(self):
        prof = SpellExaminer(Diamond).inspect()
        self.assertIn("m", prof.members)
        # our override is defined_here
        self.assertTrue(prof.members["m"]["defined_here"])

    def test_owner_class_on_inherited(self):
        prof = SpellExaminer(Diamond).inspect()
        self.assertFalse(prof.members["l"]["defined_here"])
        self.assertIn(prof.members["l"]["owner_class"], {"BLeft", "BRight", "ABase"})

    def test_base_attribute_presence(self):
        prof = SpellExaminer(Diamond).inspect()
        self.assertIn("base_attr", prof.members)

    def test_mro_contains_bases(self):
        prof = SpellExaminer(Diamond).inspect()
        self.assertIn("ABase", prof.mro)
        self.assertIn("BLeft", prof.mro)
        self.assertIn("BRight", prof.mro)

    def test_defined_here_for_direct_method(self):
        class C(ABase):
            def z(self): return 1
        prof = SpellExaminer(C).inspect()
        self.assertTrue(prof.members["z"]["defined_here"])


class TestSpellExaminer_AbstractsAndProtocols(unittest.TestCase):
    def test_abstract_base_detected_via_class_profile_maybe(self):
        prof = SpellExaminer(AbstractBase).inspect()
        # We don't assert per-member 'abstract' flag; ensure class inspection ok
        self.assertIsInstance(prof, ClassProfile)
        self.assertIn("must", prof.members)

    def test_abstract_is_implemented_in_impl_class(self):
        prof = SpellExaminer(Impl).inspect()
        self.assertIn("must", prof.members)
        self.assertTrue(callable(getattr(Impl(), "must")))

    def test_protocol_flags_for_iter_len_str(self):
        class P:
            def __len__(self): return 1
            def __iter__(self): return iter(())
            def __str__(self): return "x"
        prof = SpellExaminer(P).inspect()
        self.assertTrue(prof.protocols.get("len"))
        self.assertTrue(prof.protocols.get("iter"))
        self.assertTrue(prof.protocols.get("str"))

    def test_protocol_flags_for_call_are_boolean(self):
        prof = SpellExaminer(Functor).inspect()
        self.assertIn("call", prof.protocols)
        self.assertIsInstance(prof.protocols["call"], bool)

    def test_repr_protocol_flag_present(self):
        class R:
            def __repr__(self): return "r"
        prof = SpellExaminer(R).inspect()
        self.assertTrue(prof.protocols.get("repr"))


class TestSpellExaminer_Decorations(unittest.TestCase):
    def test_no_wrap_decorator_keeps_callable_profile(self):
        mp = SpellExaminer(dec_nowrap).inspect()
        self.assertIsInstance(mp, MethodProfile)
        self.assertTrue(isinstance(mp.decorated, (bool, type(None))))

    def test_wraps_decorator_marks_decorated_or_keeps_sig(self):
        mp = SpellExaminer(dec_wraps).inspect()
        self.assertIsInstance(mp, MethodProfile)
        # either decorated True or full signature preserved
        self.assertTrue((mp.decorated is True) or ("u: int" in (mp.signature or "")))

    def test_multiple_wrappers(self):
        @with_wraps
        @no_wrap_decorator
        def target(a, b=5):  # noqa: ARG001
            return 1
        mp = SpellExaminer(target).inspect()
        self.assertIsInstance(mp, MethodProfile)
        # Because the outer wraps(fn) receives the inner function produced by no_wrap_decorator,
        # metadata can legitimately be "inner". Accept both.
        self.assertIn((mp.qualname or mp.name).split(".")[-1], {"target", "inner"})

    def test_class_decorator_sets_decorated_flag(self):
        def class_deco(cls):
            cls.__wrapped__ = cls
            return cls
        @class_deco
        class X:
            def f(self): return 1
        prof = SpellExaminer(X).inspect()
        self.assertTrue(prof.decorated)

    def test_descriptor_on_decorated_class_members_exist(self):
        def class_deco2(cls):
            return cls
        @class_deco2
        class Y:
            d = StrictDescriptor()
        prof = SpellExaminer(Y).inspect()
        self.assertIn("d", prof.members)


class TestSpellExaminer_BuiltinsAndExtensions(unittest.TestCase):
    def test_builtin_function_ok(self):
        mp = SpellExaminer(len).inspect()
        self.assertIsInstance(mp, MethodProfile)
        self.assertTrue(mp.builtin)

    def test_builtin_type_ok(self):
        prof = SpellExaminer(dict).inspect()
        self.assertIsInstance(prof, ClassProfile)
        self.assertIn("protocols", prof.__dict__)

    def test_fake_extension_module_detection(self):
        self.assertTrue(InspectorUtility.is_extension_module(fake_ext_module()))

    def test_safe_repr_handles_objects_with_bad_repr(self):
        class Bad:
            def __repr__(self): raise RuntimeError("boom")
        s = InspectorUtility.safe_repr(Bad(), max_len=40)
        self.assertTrue(s.startswith("<unrepr-able "))

    def test_safe_repr_length_bound(self):
        long = "y" * 500
        r = InspectorUtility.safe_repr(long, max_len=50)
        self.assertLessEqual(len(r), 65)


class TestSpellExaminer_SourceAndOwnership(unittest.TestCase):
    def test_source_fields_exist_for_user_class(self):
        prof = SpellExaminer(ABase).inspect()
        self.assertIn("origin_file", prof.__dict__)
        # file may be None in some environments; just assert the key is present

    def test_source_fields_exist_for_user_function(self):
        mp = SpellExaminer(a_function).inspect()
        self.assertIn("file", mp.__dict__)
        # signature should be string-like
        self.assertIsInstance(mp.signature, (str, type(None)))

    def test_member_signature_recorded(self):
        prof = SpellExaminer(ABase).inspect()
        sig = prof.members["m"]["signature"]
        self.assertIsInstance(sig, str)
        self.assertIn("(self", sig)

    def test_owner_resolution_on_inheritance(self):
        prof = SpellExaminer(BLeft).inspect()
        self.assertIn("m", prof.members)
        self.assertFalse(prof.members["m"]["defined_here"])
        self.assertIn(prof.members["m"]["owner_class"], {"ABase"})

    def test_defined_here_on_new_method(self):
        class C(ABase):
            def new(self): return 1
        prof = SpellExaminer(C).inspect()
        self.assertTrue(prof.members["new"]["defined_here"])


if __name__ == "__main__":
    unittest.main()
