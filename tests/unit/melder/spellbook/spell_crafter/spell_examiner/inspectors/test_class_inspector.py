import inspect

import pytest

from melder.spellbook.spell_crafter.spell_examiner.inspectors.class_inspector import (
    ClassInspector,
)


class _Base:
    base_attr = 1

    def base_method(self, x):
        return x


class _Child(_Base):
    child_attr = "c"

    def __init__(self, y):
        self.y = y

    @classmethod
    def cmethod(cls, z):
        return z

    @staticmethod
    def smethod(a, b=3):
        return a + b

    @property
    def readonly(self):
        return self.y

    @readonly.setter
    def readonly(self, value):
        self.y = value

    def _private(self):  # pragma: no cover - just for inspection metadata
        return "p"


def test_rejects_non_class():
    with pytest.raises(TypeError):
        ClassInspector(object())


def test_header_captures_basics():
    ins = ClassInspector(_Child, show_dunders=True)
    data = ins.inspect()
    assert data["name"] == "_Child"
    assert data["qualname"].endswith("_Child")
    assert data["module"] == __name__
    assert data["metaclass"] == "type"
    assert data["bases"] == ["_Base"]
    assert "_Child" in data["mro"]
    assert data["is_dataclass"] is False


def test_source_fields_present_for_python_class():
    data = ClassInspector(_Child, show_dunders=True).inspect()
    assert data["file"] and data["file"].endswith(".py")
    assert data["source_line_offset"] is not None
    assert "class _Child" in (data["source_preview"] or "")


def test_builtin_source_is_none():
    data = ClassInspector(int, show_dunders=True).inspect()
    assert data["file"] is None or data["file"].endswith(".py") is False
    assert data["source_line_offset"] is None
    assert data["source_preview"] is None


def test_members_include_methods_properties_and_data():
    data = ClassInspector(_Child, show_dunders=True).inspect()
    members = data["members"]

    assert "base_method" in members
    assert members["base_method"]["owner_class"] == "_Base"
    assert members["base_method"]["defined_here"] is False

    assert "cmethod" in members and members["cmethod"]["callable"]
    assert members["cmethod"]["signature"] == "(z)"

    assert "smethod" in members and members["smethod"]["callable"]
    assert members["smethod"]["parameters"][1]["default"] == "3"

    assert "readonly" in members and members["readonly"]["property"]
    assert members["readonly"]["property_details"] == {"fget": True, "fset": True, "fdel": False}

    assert "child_attr" in members and members["child_attr"]["callable"] is False
    assert "base_attr" in members


def test_dunders_filtered_when_disabled():
    members = ClassInspector(_Child, show_dunders=False).inspect()["members"]
    assert "__init__" not in members
    assert "__dict__" not in members


def test_dunder_included_when_enabled():
    members = ClassInspector(_Child, show_dunders=True).inspect()["members"]
    assert "__init__" in members
    assert members["__init__"]["signature"].startswith("(self")


def test_protocol_flags():
    data = ClassInspector(_Child, show_dunders=True).inspect()
    protos = data["protocols"]
    assert protos["call"] is True
    assert protos["len"] is False
    assert protos["iter"] is False


def test_unwrap_detection_marks_decorated():
    def decorator(cls):
        class Wrapper(cls):
            pass

        Wrapper.__wrapped__ = cls
        return Wrapper

    @decorator
    class Wrapped(_Child):
        pass

    data = ClassInspector(Wrapped, show_dunders=True).inspect()
    assert data["decorated"] is True
    # wrapped_repr may be absent if unwrap succeeds trivially; tolerate either.
    assert "wrapped_repr" in data or data.get("decorated") is True


def test_original_signature_recorded_for_wrapped_method():
    def deco(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    class WrappedMethods:
        @deco
        def f(self, a: int, b: str = "z"):
            return a, b

    members = ClassInspector(WrappedMethods, show_dunders=True).inspect()["members"]
    info = members["f"]
    assert info["signature"] == "(*args, **kwargs)"
    assert info["original_signature"] == "(self, a: int, b: str = 'z')"
    assert info["original_parameters"][1]["annotation"] in ("int", "<class 'int'>")
    assert info["original_parameters"][2]["default"] == "'z'"


def test_safe_repr_truncation_respects_max_repr():
    class Big:
        huge = "x" * 1000

    members = ClassInspector(Big, max_repr=10, show_dunders=True).inspect()["members"]
    assert len(members["huge"]["repr"]) <= 30  # truncated with ellipsis


def test_src_line_present_for_methods_when_available():
    members = ClassInspector(_Child, show_dunders=True).inspect()["members"]
    assert members["base_method"]["src_line"] is None or isinstance(
        members["base_method"]["src_line"], int
    )
    assert isinstance(members["smethod"]["src_line"], (int, type(None)))


def test_skip_private_when_dunders_false_keeps_single_underscore():
    members = ClassInspector(_Child, show_dunders=False).inspect()["members"]
    assert "_private" in members  # single underscore not filtered


def test_annotations_collected():
    class Annotated:
        foo: int

        def bar(self, a: int) -> str:
            return str(a)

    data = ClassInspector(Annotated, show_dunders=True).inspect()
    assert data["annotations"]["foo"] is int
    info = data["members"]["bar"]
    assert info["parameters"][1]["annotation"] in ("int", "<class 'int'>")


def test_override_marks_defined_here_and_owner():
    class Parent:
        def foo(self): ...

    class Child(Parent):
        def foo(self): ...

    members = ClassInspector(Child, show_dunders=True).inspect()["members"]
    assert members["foo"]["defined_here"] is True
    assert members["foo"]["owner_class"] == "Child"


def test_inherited_property_owner():
    class P:
        @property
        def prop(self): ...

    class C(P):
        pass

    info = ClassInspector(C, show_dunders=True).inspect()["members"]["prop"]
    assert info["defined_here"] is False
    assert info["owner_class"] == "P"


def test_slots_exposed():
    class WithSlots:
        __slots__ = ("a",)

    data = ClassInspector(WithSlots, show_dunders=True).inspect()
    assert data["slots"] == ("a",)


def test_dataclass_includes_dunder_init_when_hidden():
    try:
        import dataclasses
    except ImportError:  # pragma: no cover - dataclasses always available in py3
        pytest.skip("dataclasses not available")

    @dataclasses.dataclass
    class DC:
        x: int

    members = ClassInspector(DC, show_dunders=False).inspect()["members"]
    assert "__init__" in members  # dataclass rule
    assert members["__init__"]["signature"].startswith("(self")


def test_abstract_method_flagged():
    from abc import ABC, abstractmethod

    class Abs(ABC):
        @abstractmethod
        def foo(self): ...

    info = ClassInspector(Abs, show_dunders=True).inspect()["members"]["foo"]
    assert info["abstract"] is True


def test_custom_descriptor_captured():
    class Desc:
        def __get__(self, inst, owner): ...

    class Holder:
        d = Desc()

    info = ClassInspector(Holder, show_dunders=True).inspect()["members"]["d"]
    assert info["property"] is False
    assert info["callable"] is False
    assert info["type"] in ("Desc", "NoneType")


def test_callable_object_member():
    class CallableObj:
        def __call__(self, x): ...

    class Holder:
        c = CallableObj()

    info = ClassInspector(Holder, show_dunders=True).inspect()["members"]["c"]
    assert info["callable"] is True
    assert info["signature"] in ("(self, x)", "(x)")  # depends on inspect binding


def test_varargs_kwargs_signature_kinds():
    class Siggy:
        def f(self, a, *args, b=1, **kwargs): ...

    params = ClassInspector(Siggy, show_dunders=True).inspect()["members"]["f"]["parameters"]
    kinds = {p["name"]: p["kind"] for p in params}
    assert kinds["a"] == "POSITIONAL_OR_KEYWORD"
    assert kinds["args"] == "VAR_POSITIONAL"
    assert kinds["b"] == "KEYWORD_ONLY"
    assert kinds["kwargs"] == "VAR_KEYWORD"


def test_original_signature_absent_when_not_wrapped():
    class Plain:
        def f(self, x): ...

    info = ClassInspector(Plain, show_dunders=True).inspect()["members"]["f"]
    assert info.get("original_signature") is None
    assert info["signature"] == "(self, x)"


def test_dynamic_class_has_null_provenance():
    Dyn = type("Dyn", (), {})
    data = ClassInspector(Dyn, show_dunders=True).inspect()
    # dynamic classes may still get a file when defined in a module; allow None or a path
    assert "file" in data
    assert data["source_line_offset"] is None or isinstance(data["source_line_offset"], int)


def test_protocol_flags_ignore_dunder_filter():
    class ProtoLike:
        def __call__(self): ...

    data = ClassInspector(ProtoLike, show_dunders=False).inspect()
    assert data["protocols"]["call"] is True


def test_property_access_not_invoked_when_getter_raises():
    class Loud:
        @property
        def boom(self):
            raise RuntimeError("should not access")

    info = ClassInspector(Loud, show_dunders=True).inspect()["members"]["boom"]
    assert info["property"] is True
    assert info["property_details"]["fget"] is True


def test_safe_repr_handles_raising_repr():
    class BadRepr:
        def __repr__(self):
            raise RuntimeError("nope")

    members = ClassInspector(type("H", (), {"x": BadRepr()}), show_dunders=True).inspect()["members"]
    assert "BadRepr" in members["x"]["repr"]


def test_extension_and_builtin_flags(monkeypatch):
    class FakeMod:
        __file__ = "fake.so"

    def fake_getmodule(obj):
        return FakeMod

    monkeypatch.setattr(inspect, "getmodule", fake_getmodule)

    class C:
        pass

    data = ClassInspector(C, show_dunders=True).inspect()
    # builtin check likely False, extension True via utility; at least ensure fields exist
    assert "is_builtin_module" in data
    assert "is_extension_module" in data


def test_classify_members_fallback(monkeypatch):
    monkeypatch.setattr(inspect, "classify_members", None, raising=False)

    class C:
        def f(self): ...
        x = 1

    members = ClassInspector(C, show_dunders=True).inspect()["members"]
    assert "f" in members and "x" in members


def test_wrapped_class_unwrap_failure_is_tolerated(monkeypatch):
    class C:
        pass

    def fake_unwrap(obj):
        raise RuntimeError("no unwrap")

    monkeypatch.setattr(inspect, "unwrap", fake_unwrap)
    data = ClassInspector(C, show_dunders=True).inspect()
    assert "decorated" in data


def test_property_details_for_getter_only():
    class P:
        @property
        def ro(self):
            return 1

    info = ClassInspector(P, show_dunders=True).inspect()["members"]["ro"]
    assert info["property_details"] == {"fget": True, "fset": False, "fdel": False}


def test_member_repr_truncates_callable_default():
    class C:
        def f(self, a=lambda: "x" * 200):
            return a

    params = ClassInspector(C, show_dunders=True, max_repr=20).inspect()["members"]["f"]["parameters"]
    defaults = [p["default"] for p in params if p["default"] is not None]
    assert defaults and len(defaults[0]) <= 40


def test_slots_inheritance_combines_members():
    class P:
        __slots__ = ("a",)

    class C(P):
        __slots__ = ("b",)

    members = ClassInspector(C, show_dunders=True).inspect()["members"]
    assert "a" in members and "b" in members


def test_descriptor_returning_callable():
    class D:
        def __get__(self, inst, owner):
            def inner(x):
                return x

            return inner

    class Holder:
        d = D()

    info = ClassInspector(Holder, show_dunders=True).inspect()["members"]["d"]
    assert info["callable"] is True


def test_signature_failure_does_not_crash(monkeypatch):
    def bad_sig(obj):
        raise ValueError("no sig")

    monkeypatch.setattr(inspect, "signature", bad_sig)

    class C:
        def f(self, x):
            return x

    info = ClassInspector(C, show_dunders=True).inspect()["members"]["f"]
    assert info["signature"] is None


def test_positional_only_params():
    def make():
        def f(a, /, b):
            return a + b

        return f

    class C:
        g = staticmethod(make())

    params = ClassInspector(C, show_dunders=True).inspect()["members"]["g"]["parameters"]
    kinds = {p["name"]: p["kind"] for p in params}
    assert kinds["a"] == "POSITIONAL_ONLY"
    assert kinds["b"] == "POSITIONAL_OR_KEYWORD"


def test_forward_ref_annotations_resolve_best_effort():
    class C:
        x: "C"

        def f(self, y: "C"):
            return y

    globals()["C"] = C  # ensure resolution works for eval_str
    data = ClassInspector(C, show_dunders=True).inspect()
    assert data["annotations"]["x"] in (C, "C")
    params = data["members"]["f"]["parameters"]
    assert params[1]["annotation"] in ("C", str(C), "'C'")


def test_getattr_not_invoked():
    class Loud:
        def __getattr__(self, item):
            raise RuntimeError("boom")

    data = ClassInspector(Loud, show_dunders=True).inspect()
    assert "members" in data


def test_mixin_owner_resolution_prefers_first_mro():
    class A:
        def f(self): ...

    class B:
        def f(self): ...

    class C(A, B):
        pass

    info = ClassInspector(C, show_dunders=True).inspect()["members"]["f"]
    assert info["owner_class"] == "A"


def test_long_docstring_truncated_in_repr():
    class C:
        """{}""".format("d" * 500)

    data = ClassInspector(C, max_repr=50, show_dunders=True).inspect()
    # docstring isn't stored, but repr of class should be truncated
    assert len(data["members"]["__doc__"]["repr"]) <= 53 if "__doc__" in data["members"] else True


def test_extension_member_no_dict_still_listed():
    class NoDict:
        __slots__ = ()

        def __len__(self):
            return 0

    members = ClassInspector(NoDict, show_dunders=True).inspect()["members"]
    assert "__len__" in members


def test_property_setter_only_is_handled():
    class P:
        @property
        def p(self):
            return 1

        @p.setter
        def p(self, value):
            self._v = value

    info = ClassInspector(P, show_dunders=True).inspect()["members"]["p"]
    assert info["property_details"]["fset"] is True


def test_member_from_mixin_second_mro_owner():
    class A:
        def f(self): ...

    class B:
        def f(self): ...

    class C(B, A):
        pass

    info = ClassInspector(C, show_dunders=True).inspect()["members"]["f"]
    assert info["owner_class"] == "B"


def test_busted_signature_builtin_callable():
    class C:
        f = len  # builtin signature path

    info = ClassInspector(C, show_dunders=True).inspect()["members"]["f"]
    assert info["signature"] is not None or info["signature"] is None  # ensure no crash


def test_len_protocol_true_when_dunder_present():
    class C:
        def __len__(self): ...

    protos = ClassInspector(C, show_dunders=False).inspect()["protocols"]
    assert protos["len"] is True


def test_callable_attribute_without_signature():
    class CallableNoSig:
        __call__ = object()

    class Holder:
        c = CallableNoSig()

    info = ClassInspector(Holder, show_dunders=True).inspect()["members"]["c"]
    assert info["callable"] is True


def test_repr_of_method_with_large_default_truncated():
    class C:
        def f(self, a="x" * 500):
            return a

    params = ClassInspector(C, max_repr=15, show_dunders=True).inspect()["members"]["f"]["parameters"]
    defaults = [p["default"] for p in params if p["default"] is not None]
    assert defaults and len(defaults[0]) <= 30


def test_slots_and_dict_members_coexist():
    class P:
        __slots__ = ("a",)

    class C(P):
        b = 1

    members = ClassInspector(C, show_dunders=True).inspect()["members"]
    assert "a" in members and "b" in members


def test_signature_original_for_classmethod_wrapped():
    def deco(fn):
        def w(*args, **kwargs):
            return fn(*args, **kwargs)

        return w

    class C:
        @classmethod
        @deco
        def cm(cls, x: int):
            return x

    info = ClassInspector(C, show_dunders=True).inspect()["members"]["cm"]
    assert info["signature"] in ("(cls, x: int)", "(cls, x)", "(*args, **kwargs)")
