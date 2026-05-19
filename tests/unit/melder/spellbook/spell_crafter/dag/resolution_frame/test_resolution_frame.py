import pytest

from melder.aether.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)


def test_init_copies_overrides():
    original = {"a": 1}
    frame = ResolutionFrame(original)
    assert frame.overrides == original
    original["a"] = 2
    assert frame.overrides == {"a": 1}


def test_has_and_get_override():
    frame = ResolutionFrame({"x": "y"})
    assert frame.has_override("x") is True
    assert frame.get_override("x") == "y"
    assert frame.has_override("missing") is False
    with pytest.raises(KeyError):
        frame.get_override("missing")


def test_set_get_has_result():
    frame = ResolutionFrame()
    frame.set_result("n1", 123)
    assert frame.has_result("n1") is True
    assert frame.get_result("n1") == 123
    assert frame.results == {"n1": 123}
    with pytest.raises(KeyError):
        frame.get_result("missing")
    with pytest.raises(ValueError):
        frame.set_result("", 1)


def test_register_and_get_error():
    frame = ResolutionFrame()
    err = RuntimeError("boom")
    frame.register_error("n1", err)
    assert frame.get_error("n1") is err
    assert frame.errors == {"n1": err}
    assert frame.get_error("missing") is None
    with pytest.raises(ValueError):
        frame.register_error("", err)
    with pytest.raises(ValueError):
        frame.register_error("n1", None)  # type: ignore[arg-type]


def test_repr_contains_counts():
    frame = ResolutionFrame({"o": 1})
    frame.set_result("n1", 2)
    frame.register_error("n2", RuntimeError("x"))
    text = repr(frame)
    assert "overrides=1" in text
    assert "results=1" in text
    assert "errors=1" in text


def test_properties_return_copies():
    frame = ResolutionFrame({"a": 1})
    frame.set_result("n1", 2)
    frame.register_error("n2", RuntimeError("x"))
    overrides = frame.overrides
    results = frame.results
    errors = frame.errors
    overrides["a"] = 10
    results["n1"] = 20
    errors["n2"] = RuntimeError("mutate")
    assert frame.get_override("a") == 1
    assert frame.get_result("n1") == 2
    assert isinstance(frame.get_error("n2"), RuntimeError)


def test_cleanup_is_terminal_and_repr_stays_stable():
    frame = ResolutionFrame({"a": 1})
    frame.set_result("n1", 2)
    frame.register_error("n2", RuntimeError("x"))
    frame_id = frame.id

    frame.cleanup()
    frame.cleanup()

    assert frame.cleaned is True
    assert repr(frame) == f'ResolutionFrame(id={frame_id!r}, cleaned=True)'

    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = frame.overrides
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = frame.results
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = frame.errors
    with pytest.raises(RuntimeError, match="already been cleaned"):
        frame.has_override("a")
    with pytest.raises(RuntimeError, match="already been cleaned"):
        frame.get_override("a")
    with pytest.raises(RuntimeError, match="already been cleaned"):
        frame.has_result("n1")
    with pytest.raises(RuntimeError, match="already been cleaned"):
        frame.get_result("n1")
    with pytest.raises(RuntimeError, match="already been cleaned"):
        frame.get_error("n2")
    with pytest.raises(RuntimeError, match="already been cleaned"):
        frame.set_result("n3", 3)
    with pytest.raises(RuntimeError, match="already been cleaned"):
        frame.register_error("n3", RuntimeError("boom"))
