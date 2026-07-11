import pytest

from melder.mutation_research.diff.strategies.structural_diff_strategy import (
    StructuralDiffStrategy,
)


def _material(sources=None, fingerprints=None):
    """
    Build one resolver-material payload for strategy tests.

    Args:
        sources:
            Optional module name -> source text mapping.
        fingerprints:
            Optional module name -> SHA256 mapping.

    Returns:
        dict: Material payload.
    """
    return {
        "spell_id": "sha-x",
        "sources": sources or {},
        "fingerprints": fingerprints or {},
    }


LEFT_MODULE = '''
"""Module doc."""


def helper(a, b):
    """Add."""
    return a + b


class Service:
    """Service doc."""

    def run(self, x):
        """Run."""
        return x * 2

    def retired(self):
        """Going away."""
        return None
'''

RIGHT_MODULE = '''
"""Module doc."""


def helper(a, b, scale=1):
    """Add."""
    return (a + b) * scale


class Service:
    """Service doc."""

    def run(self, x):
        """Run twice as hard."""
        return x * 4

    def fresh(self):
        """New capability."""
        return True
'''


def test_identical_structure_reports_identical() -> None:
    """
    Verify byte-different but structurally identical modules roll up as
    identical (comments and spacing are not structure).
    """
    strategy = StructuralDiffStrategy()
    left = _material(sources={"mod.a": "def f(x):\n    return x\n"})
    right = _material(
        sources={"mod.a": "# a comment\ndef f(x):\n    return x\n"},
    )

    result = strategy.diff(left, right)

    assert result["identical"] is True
    assert result["identical_modules"] == ["mod.a"]


def test_structural_aspects_classify_per_callable() -> None:
    """
    Verify signature/docstring/body aspects and method add/remove land on
    the right names.
    """
    strategy = StructuralDiffStrategy()
    left = _material(sources={"mod.svc": LEFT_MODULE})
    right = _material(sources={"mod.svc": RIGHT_MODULE})

    result = strategy.diff(left, right)

    assert result["changed_modules"] == ["mod.svc"]
    report = result["module_reports"]["mod.svc"]
    assert report["changed_functions"]["helper"] == {
        "signature_changed": True,
        "body_changed": True,
    }
    service = report["changed_classes"]["Service"]
    assert service["added_methods"] == ["fresh"]
    assert service["removed_methods"] == ["retired"]
    assert service["changed_methods"]["run"] == {
        "docstring_changed": True,
        "body_changed": True,
    }


def test_docstring_only_change_is_isolated() -> None:
    """
    Verify a docstring edit never reports as a body change.
    """
    strategy = StructuralDiffStrategy()
    left = _material(
        sources={"mod.a": 'def f():\n    """Old."""\n    return 1\n'},
    )
    right = _material(
        sources={"mod.a": 'def f():\n    """New."""\n    return 1\n'},
    )

    result = strategy.diff(left, right)

    report = result["module_reports"]["mod.a"]
    assert report["changed_functions"]["f"] == {
        "docstring_changed": True,
    }


def test_parse_errors_stay_loud_and_named() -> None:
    """
    Verify unparseable source reports the failing side instead of crashing.
    """
    strategy = StructuralDiffStrategy()
    left = _material(sources={"mod.a": "def broken(:\n"})
    right = _material(sources={"mod.a": "def fine():\n    return 1\n"})

    result = strategy.diff(left, right)

    report = result["module_reports"]["mod.a"]
    assert report["parse_error"].startswith("left:")
    assert result["identical"] is False


def test_text_unavailable_modules_are_reported_not_judged() -> None:
    """
    Verify fingerprint-only modules land in the honesty bucket without a
    structural verdict.
    """
    strategy = StructuralDiffStrategy()
    left = _material(fingerprints={"mod.bin": "print-1"})
    right = _material(fingerprints={"mod.bin": "print-2"})

    result = strategy.diff(left, right)

    assert result["text_unavailable_modules"] == ["mod.bin"]
    assert result["module_reports"] == {}
    assert result["identical"] is True


def test_strategy_cleanup_guards_use() -> None:
    """
    Verify cleanup semantics and use-after-clean guards.
    """
    strategy = StructuralDiffStrategy()
    strategy.cleanup()
    strategy.cleanup()

    assert strategy.cleaned is True
    with pytest.raises(RuntimeError):
        strategy.diff(_material(), _material())
