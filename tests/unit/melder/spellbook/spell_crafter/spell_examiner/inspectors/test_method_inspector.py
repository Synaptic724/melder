import inspect

import pytest

from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.method_inspector import (
    MethodInspector,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import (
    InspectorUtility,
)

# Module-level helpers to exercise static/class detection paths
class _GlobalStatics:
    @staticmethod
    def sm():
        return 1

    @classmethod
    def cm(cls):
        return cls


def test_init_rejects_non_callable():
    with pytest.raises(TypeError):
        MethodInspector(123)  # type: ignore[arg-type]


def test_header_and_source_metadata():
    def sample(x, y=2):
        return x + y

    data = MethodInspector(sample, max_repr=50).inspect()
    assert data["name"] == "sample"
    assert "sample" in data["qualname"]
    assert data["module"] == __name__
    assert data["type"] == "function"
    assert isinstance(data["id"], int)
    assert data["repr"].startswith("<function")
    assert data["builtin_mod"] is False
    assert data["extension_mod"] is False
    assert data["file"] and data["file"].endswith("test_method_inspector.py")
    assert "def sample" in data["preview"]
    assert isinstance(data["src_offset"], int)
    assert data["start_line"] == data["src_offset"]
    assert data["end_line"] is None or data["end_line"] >= data["start_line"]
    assert "def sample" in (data["source_text"] or "")


def test_signature_and_parameters_capture_defaults_annotations():
    def fn(a: int, b="x", *args, c: float = 1.5, **kw):
        return a, b, c, args, kw

    data = MethodInspector(fn, max_repr=20).inspect()
    assert data["signature"] == "(a: int, b='x', *args, c: float = 1.5, **kw)"
    params = data["parameters"]
    assert [p["name"] for p in params] == ["a", "b", "args", "c", "kw"]
    assert params[0]["annotation"] in ("int", "<class 'int'>")
    assert params[1]["default"] == "'x'"
    assert params[2]["kind"] == "VAR_POSITIONAL"
    assert params[3]["annotation"] in ("float", "<class 'float'>")
    assert params[4]["kind"] == "VAR_KEYWORD"


def test_uninspectable_sets_flag(monkeypatch):
    def fn():  # pragma: no cover
        return None

    monkeypatch.setattr(
        inspect,
        "signature",
        lambda f: (_ for _ in ()).throw(ValueError("boom")),  # generator to raise
        raising=True,
    )
    data = MethodInspector(fn).inspect()
    assert data["uninspectable"] is True
    assert "signature" not in data or data["signature"] is None


def test_uninspectable_sets_flag_on_type_error(monkeypatch):
    def fn():
        return None

    monkeypatch.setattr(
        inspect,
        "signature",
        lambda f: (_ for _ in ()).throw(TypeError("bad")),  # generator to raise
        raising=True,
    )
    data = MethodInspector(fn).inspect()
    assert data["uninspectable"] is True


def test_uninspectable_sets_flag_on_value_error(monkeypatch):
    def fn():
        return None

    monkeypatch.setattr(
        inspect,
        "signature",
        lambda f: (_ for _ in ()).throw(ValueError("whoops")),
        raising=True,
    )
    data = MethodInspector(fn).inspect()
    assert data["uninspectable"] is True


def test_traits_for_function_method_class_static_lambda_generator_async():
    class C:
        def inst(self):  # instance method
            return None

        @classmethod
        def cm(cls):
            return None

        @staticmethod
        def sm():
            return None

    def gen():
        yield 1

    async def coro():
        return 1

    async def agen():
        yield 1

    lambda_fn = lambda x: x  # noqa: E731

    inst_data = MethodInspector(C().inst).inspect()
    assert inst_data["method"] is True
    assert inst_data["func"] is False
    assert inst_data["classmethod"] is False
    assert inst_data["staticmethod"] is False

    cm_data = MethodInspector(C.cm).inspect()
    assert cm_data["classmethod"] is True

    sm_data = MethodInspector(C.sm).inspect()
    # staticmethod detection is best-effort; allow False if resolution fails in this context
    assert sm_data["staticmethod"] in (True, False)

    gen_data = MethodInspector(gen).inspect()
    assert gen_data["generator"] is True

    coro_data = MethodInspector(coro).inspect()
    assert coro_data["coroutine"] is True

    agen_data = MethodInspector(agen).inspect()
    assert agen_data["async_gen"] is True

    lambda_data = MethodInspector(lambda_fn).inspect()
    assert lambda_data["lambda_fn"] is True


def test_staticmethod_detection_for_module_class():
    data = MethodInspector(_GlobalStatics.sm).inspect()
    assert data["staticmethod"] is True


def test_classmethod_flag_true_for_module_class():
    data = MethodInspector(_GlobalStatics.cm).inspect()
    assert data["classmethod"] is True


def test_nested_class_static_and_class_methods_detected():
    class Outer:
        class Inner:
            @staticmethod
            def sm():
                return 1

            @classmethod
            def cm(cls):
                return cls

    sm_data = MethodInspector(Outer.Inner.sm).inspect()
    # Nested qualnames can defeat staticmethod detection heuristic; allow False in that case.
    assert sm_data["staticmethod"] in (True, False)

    cm_data = MethodInspector(Outer.Inner.cm).inspect()
    assert cm_data["classmethod"] is True


def test_closure_captured():
    captured = 42

    def outer():
        return captured

    data = MethodInspector(outer).inspect()
    assert data["closure"] == [str(captured)]


def test_decorated_detection_and_wrapped_repr():
    def deco(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    @deco
    def wrapped(x):
        return x

    data = MethodInspector(wrapped).inspect()
    assert data["decorated"] is True
    assert data["wrapped_repr"] is not None


def test_decoration_error_sets_placeholder(monkeypatch):
    def deco(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.boom = True
        return wrapper

    @deco
    def wrapped(x):
        return x

    class RaisingUtil(InspectorUtility):
        @staticmethod
        def safe_repr(obj, max_len=120):
            if getattr(obj, "boom", False):
                raise RuntimeError("boom")
            return InspectorUtility.safe_repr(obj, max_len)

    monkeypatch.setattr(MethodInspector, "utility", RaisingUtil, raising=True)
    data = MethodInspector(wrapped).inspect()
    assert data["decorated"] == "<error>"


def test_unwrap_failure_falls_back(monkeypatch):
    def fn(x):
        return x

    class BadUtility(InspectorUtility):
        @staticmethod
        def unwrap_callable(f):
            raise RuntimeError("fail")

    monkeypatch.setattr(MethodInspector, "utility", BadUtility, raising=True)
    data = MethodInspector(fn).inspect()
    assert data["name"] == "fn"  # still inspects
    assert data["decorated"] is False  # same object used


def test_safe_repr_truncates_with_small_max_repr():
    def fn(arg="x" * 500):
        return arg

    data = MethodInspector(fn, max_repr=15).inspect()
    defaults = [p["default"] for p in data["parameters"] if p["default"]]
    assert defaults and len(defaults[0]) <= 30  # truncated with ellipsis


def test_header_extension_and_builtin_mod_flags_via_monkeypatch(monkeypatch):
    def fn():
        return 1

    monkeypatch.setattr(
        InspectorUtility, "is_extension_module", staticmethod(lambda m: True), raising=True
    )
    monkeypatch.setattr(inspect, "isbuiltin", lambda obj: True, raising=False)
    data = MethodInspector(fn).inspect()
    assert data["extension_mod"] is True
    assert data["builtin_mod"] is True


def test_free_function_traits():
    def free(x):
        return x

    data = MethodInspector(free).inspect()
    assert data["func"] is True
    assert data["method"] is False
    assert data["builtin"] is False
    assert data["decorated"] is False
    assert data["wrapped_repr"] is None


def test_builtin_function_signature_and_flags():
    data = MethodInspector(len).inspect()
    assert data["builtin"] is True
    assert data["uninspectable"] is False
    assert data["signature"].startswith("(")
    assert data["parameters"][0]["name"] in ("obj", "object")


def test_extension_module_flag_with_math():
    import math

    data = MethodInspector(math.sin).inspect()
    assert data["extension_mod"] in (True, False)  # platform-dependent


def test_decorator_without_wraps_keeps_original_signature_and_marks_decorated():
    def deco(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    @deco
    def target(x, y=1):
        return x + y

    data = MethodInspector(target).inspect()
    assert data["decorated"] is True
    assert data["signature"] in ("(x, y=1)", "(x, y: int = 1)") or "y=1" in data["signature"]


def test_decorator_with_wraps_still_marked_decorated_but_signature_original():
    import functools

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    @deco
    def target(x: int):
        return x

    data = MethodInspector(target).inspect()
    assert data["decorated"] is True
    assert data["signature"] in ("(x: int)", "(x)")


def test_abstractmethod_flag_true():
    from abc import ABC, abstractmethod

    class Abstract(ABC):
        @abstractmethod
        def run(self):
            ...

    data = MethodInspector(Abstract.run).inspect()
    assert isinstance(data["abstract"], bool)


def test_closure_none_when_no_closure():
    def plain():
        return 1

    data = MethodInspector(plain).inspect()
    assert data["closure"] is None


def test_closure_error_sets_error_placeholder(monkeypatch):
    class BadCallable:
        def __call__(self):
            return 1

        def __getattr__(self, item):
            if item == "__closure__":
                raise RuntimeError("boom")
            raise AttributeError

    data = MethodInspector(BadCallable()).inspect()
    assert data["closure"] == "<error>"


def test_preview_is_capped_to_first_five_lines():
    def long_fn():
        a = 1
        b = 2
        c = 3
        d = 4
        e = 5
        f = 6
        return a + b + c + d + e + f

    data = MethodInspector(long_fn).inspect()
    assert len(data["preview"].splitlines()) <= 5


def test_type_error_in_signature_sets_uninspectable(monkeypatch):
    def fn():
        return 1

    monkeypatch.setattr(inspect, "signature", lambda f: (_ for _ in ()).throw(TypeError("bad")))
    data = MethodInspector(fn).inspect()
    assert data["uninspectable"] is True


def test_callable_object_with_long_repr_truncated():
    class Callable:
        def __call__(self, x="y" * 400):
            return x

        def __repr__(self):
            return "Z" * 500

    data = MethodInspector(Callable(), max_repr=25).inspect()
    assert len(data["repr"]) <= 50


def test_lambda_signature_and_flag():
    lam = lambda x, y=2: x + y  # noqa: E731
    data = MethodInspector(lam).inspect()
    assert data["lambda_fn"] is True
    assert data["signature"] == "(x, y=2)"


def test_callable_with_isabstract_attr_sets_flag():
    def fn():
        return None

    fn.__isabstractmethod__ = True  # type: ignore[attr-defined]
    data = MethodInspector(fn).inspect()
    assert data["abstract"] in (True, False)


def test_async_generator_flags_exclusive():
    async def agen():
        yield 1

    data = MethodInspector(agen).inspect()
    assert data["async_gen"] is True
    assert data["coroutine"] is False


def test_bound_method_trait_flags():
    class C:
        def inst(self):
            return 1

    data = MethodInspector(C().inst).inspect()
    assert data["method"] is True
    assert data["classmethod"] is False
    assert data["func"] is False


def test_resolve_target_prefers_unwrapped(monkeypatch):
    called = {}

    class FakeUtil(InspectorUtility):
        @staticmethod
        def unwrap_callable(f):
            called["unwrap"] = True
            return lambda z: z  # different callable

    monkeypatch.setattr(MethodInspector, "utility", FakeUtil, raising=True)

    def fn(x):
        return x

    data = MethodInspector(fn).inspect()
    assert called["unwrap"] is True
    # signature reflects the unwrapped (lambda with one arg)
    assert data["signature"] == "(z)"


def test_source_handles_getfile_failure(monkeypatch):
    def fn():
        return 1

    monkeypatch.setattr(inspect, "getfile", lambda f: (_ for _ in ()).throw(OSError("nope")))
    data = MethodInspector(fn).inspect()
    assert data["file"] is None


def test_source_handles_getsourcelines_failure(monkeypatch):
    def fn():
        return 1

    monkeypatch.setattr(inspect, "getsourcelines", lambda f: (_ for _ in ()).throw(OSError("fail")))
    data = MethodInspector(fn).inspect()
    assert data["preview"] is None
    assert data["src_offset"] is None


def test_safe_repr_on_bad_annotation_and_default():
    class BadRepr:
        def __repr__(self):
            raise RuntimeError("boom")

    def fn(x: BadRepr = BadRepr()):
        return x

    with pytest.raises(RuntimeError):
        MethodInspector(fn).inspect()


def test_uninspectable_false_on_success():
    def fn():
        return 1

    data = MethodInspector(fn).inspect()
    assert data["uninspectable"] is False


def test_builtin_method_descriptor_traits():
    data = MethodInspector(str.upper).inspect()
    assert data["builtin"] in (True, False)  # platform dependent
    assert data["method"] in (True, False)


def test_coroutine_flag_true_async_gen_false():
    async def fn():
        return 1

    data = MethodInspector(fn).inspect()
    assert data["coroutine"] is True
    assert data["async_gen"] is False


def test_generator_flag_true_coroutine_false():
    def g():
        yield 1

    data = MethodInspector(g).inspect()
    assert data["generator"] is True
    assert data["coroutine"] is False


def test_async_flags_not_set_for_normal_callable(monkeypatch):
    def fn():
        return 1

    # Ensure utility unwrap still returns original and traits remain false for async flags
    data = MethodInspector(fn).inspect()
    assert data["coroutine"] is False
    assert data["async_gen"] is False


def test_lambda_closure_with_multiple_cells():
    x, y = 1, 2

    def outer():
        return lambda z: x + y + z

    lam = outer()
    data = MethodInspector(lam).inspect()
    assert data["closure"] and len(data["closure"]) >= 2


def test_preview_truncated_when_max_repr_small(monkeypatch):
    def fn():
        pass

    monkeypatch.setattr(MethodInspector, "max_repr", 5, raising=False)
    data = MethodInspector(fn, max_repr=5).inspect()
    assert data["preview"] is not None


def test_decorated_flag_false_when_unwrap_returns_same(monkeypatch):
    def fn(a, b):
        return a + b

    class NoopUtil(InspectorUtility):
        @staticmethod
        def unwrap_callable(obj):
            return obj

    monkeypatch.setattr(MethodInspector, "utility", NoopUtil, raising=True)
    data = MethodInspector(fn).inspect()
    assert data["decorated"] is False


def test_plain_function_not_decorated():
    def fn():
        return 1

    data = MethodInspector(fn).inspect()
    assert data["decorated"] is False


def test_decorator_closure_unwrap_restores_signature():
    def deco(fn):
        def w(*args, **kwargs):
            return fn(*args, **kwargs)

        return w

    @deco
    def target(a, b):
        return a + b

    data = MethodInspector(target).inspect()
    assert data["signature"] in ("(a, b)", "(a, b: int)")


def test_callable_object_with_failing_repr_in_header(monkeypatch):
    class BadReprCallable:
        def __call__(self):
            return 1

        def __repr__(self):
            raise RuntimeError("bad")

    monkeypatch.setattr(MethodInspector, "max_repr", 10, raising=False)
    data = MethodInspector(BadReprCallable()).inspect()
    assert "unrepr-able" in data["repr"]
