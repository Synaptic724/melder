import types
import pytest

from melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility import (
    InspectorUtility,
)


def test_safe_repr_short_string_returns_full():
    text = "hello"
    result = InspectorUtility.safe_repr(text, max_len=50)
    assert result == repr(text)


def test_safe_repr_truncates_and_reports_length():
    payload = "x" * 200
    result = InspectorUtility.safe_repr(payload, max_len=25)
    # should include ellipsis and the original length metadata
    assert result.startswith("'xxxxx")
    # length reported includes the surrounding quotes InspectorUtility adds
    assert "... (len 202)" in result
    # the truncation should respect the defensive lower bound of 10 chars
    assert len(result) <= 25


def test_safe_repr_handles_bad_repr():
    class Boom:
        def __repr__(self):
            raise RuntimeError("boom")

    result = InspectorUtility.safe_repr(Boom(), max_len=30)
    assert result == "<unrepr-able Boom>"


def test_is_extension_module_detects_pyd():
    module = types.SimpleNamespace(
        __spec__=types.SimpleNamespace(origin="C:/path/native.PYD")
    )
    assert InspectorUtility.is_extension_module(module) is True


def test_is_extension_module_handles_missing_spec_and_py():
    plain = types.SimpleNamespace()
    py_mod = types.SimpleNamespace(
        __spec__=types.SimpleNamespace(origin="c:/code/module.py")
    )
    assert InspectorUtility.is_extension_module(None) is False
    assert InspectorUtility.is_extension_module(plain) is False
    assert InspectorUtility.is_extension_module(py_mod) is False


def test_unwrap_callable_follows_wrapped_attribute():
    def original(x):
        return x + 1

    def wrapper(x):
        return original(x)

    wrapper.__wrapped__ = original
    assert InspectorUtility.unwrap_callable(wrapper) is original


def test_unwrap_callable_walks_closure_without_wraps():
    def decorator(fn):
        def inner(*args, **kwargs):
            return fn(*args, **kwargs)

        return inner

    @decorator
    def target():
        return "hit"

    unwrapped = InspectorUtility.unwrap_callable(target)
    assert unwrapped is not target
    assert unwrapped() == "hit"


def test_unwrap_callable_returns_input_on_failure(monkeypatch):
    class Opaque:
        pass

    obj = Opaque()
    # Simulate inspect.unwrap exploding to exercise fallback
    monkeypatch.setattr(
        "melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility.inspect.unwrap",
        lambda o: (_ for _ in ()).throw(RuntimeError("fail")),
    )
    assert InspectorUtility.unwrap_callable(obj) is obj
