import pytest

from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)


def _diag(**kwargs) -> SystemDiagnostic:
    return SystemDiagnostic(code="X", message="msg", **kwargs)


def test_constructor_sets_defaults_and_fields():
    diag = SystemDiagnostic("C1", "hello")
    assert diag.code == "C1"
    assert diag.message == "hello"
    assert diag.severity is SystemDiagnosticSeverity.ERROR
    assert diag.spell_id is None
    assert diag.root_id is None
    assert diag.source is None
    assert diag.details is None


def test_constructor_accepts_custom_severity_and_ids():
    diag = SystemDiagnostic(
        "C2",
        "warn",
        severity=SystemDiagnosticSeverity.WARNING,
        spell_id="sid",
        root_id="rid",
        source="StrategyName",
        details={"a": 1},
    )
    assert diag.severity is SystemDiagnosticSeverity.WARNING
    assert diag.spell_id == "sid"
    assert diag.root_id == "rid"
    assert diag.source == "StrategyName"
    assert diag.details == {"a": 1}


@pytest.mark.parametrize("bad_code", [None, ""])
def test_constructor_rejects_empty_code(bad_code):
    with pytest.raises(ValueError):
        SystemDiagnostic(bad_code, "msg")


def test_constructor_rejects_none_message():
    with pytest.raises(ValueError):
        SystemDiagnostic("C", None)


def test_constructor_rejects_none_severity():
    with pytest.raises(ValueError):
        SystemDiagnostic("C", "m", severity=None)


def test_details_are_copied_from_input_and_not_shared():
    payload = {"k": 1}
    diag = _diag(details=payload)
    payload["k"] = 2
    assert diag.details == {"k": 1}
    assert diag.details is not payload


def test_details_property_returns_copy_each_time():
    diag = _diag(details={"k": 1})
    first = diag.details
    first["k"] = 5
    second = diag.details
    assert second == {"k": 1}
    assert first is not second


def test_details_none_when_not_provided():
    diag = _diag()
    assert diag.details is None


def test_empty_details_preserved_as_empty_dict():
    diag = _diag(details={})
    assert diag.details is None


def test_cleanup_clears_fields_and_marks_cleaned():
    diag = _diag(details={"a": 1}, spell_id="sid", root_id="rid")
    diag.cleanup()
    assert diag._cleaned is True  # noqa: SLF001
    assert diag._code is None  # noqa: SLF001
    assert diag._message is None  # noqa: SLF001
    assert diag._severity is None  # noqa: SLF001
    assert diag._spell_id is None  # noqa: SLF001
    assert diag._root_id is None  # noqa: SLF001
    assert diag._details is None  # noqa: SLF001


def test_cleanup_idempotent():
    diag = _diag(details={"a": 1})
    diag.cleanup()
    diag.cleanup()  # should not raise
    assert diag._cleaned is True  # noqa: SLF001


@pytest.mark.parametrize(
    "getter",
    [
        lambda d: d.code,
        lambda d: d.message,
        lambda d: d.severity,
        lambda d: d.spell_id,
        lambda d: d.root_id,
        lambda d: d.source,
        lambda d: d.details,
    ],
)
def test_properties_raise_after_cleanup(getter):
    diag = _diag(details={"a": 1})
    diag.cleanup()
    with pytest.raises(RuntimeError):
        getter(diag)


def test_repr_includes_core_fields():
    diag = _diag(spell_id="s1", root_id="r1")
    text = repr(diag)
    assert "SystemDiagnostic" in text
    assert "s1" in text and "r1" in text
    assert "code='X'" in text


def test_repr_after_cleanup_handles_none_fields():
    diag = _diag()
    diag.cleanup()
    text = repr(diag)
    assert "None" in text


def test_details_from_mapping_subclass_is_copied():
    class MappingSub(dict):
        pass

    payload = MappingSub({"x": 2})
    diag = _diag(details=payload)
    assert diag.details == {"x": 2}
    assert diag.details is not payload


def test_original_details_not_cleared_on_cleanup():
    payload = {"x": 1}
    diag = _diag(details=payload)
    diag.cleanup()
    assert payload == {"x": 1}


def test_multiple_diagnostics_clean_independently():
    d1 = _diag(details={"a": 1})
    d2 = _diag(details={"b": 2})
    d1.cleanup()
    assert d2.details == {"b": 2}
    assert d1._cleaned is True  # noqa: SLF001
    assert d2._cleaned is False  # noqa: SLF001
