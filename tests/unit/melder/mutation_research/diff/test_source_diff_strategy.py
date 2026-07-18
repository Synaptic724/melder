import pytest

from melder.mutation_research.diff.strategies.source_diff_strategy import (
    SourceDiffStrategy,
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


def test_identical_sources_report_identical() -> None:
    """
    Verify byte-equal text on both sides rolls up as identical.
    """
    strategy = SourceDiffStrategy()
    left = _material(sources={"mod.a": "x = 1\n"})
    right = _material(sources={"mod.a": "x = 1\n"})

    result = strategy.diff(left, right)

    assert result["identical"] is True
    assert result["identical_modules"] == ["mod.a"]
    assert result["module_diffs"] == {}


def test_changed_source_produces_unified_diff() -> None:
    """
    Verify text-on-both-sides changes carry a real unified diff.
    """
    strategy = SourceDiffStrategy()
    left = _material(sources={"mod.a": "x = 1\ny = 2\n"})
    right = _material(sources={"mod.a": "x = 1\ny = 3\n"})

    result = strategy.diff(left, right)

    assert result["identical"] is False
    assert result["changed_modules"] == ["mod.a"]
    detail = result["module_diffs"]["mod.a"]
    assert detail["text_unavailable"] is False
    assert any(line.startswith("-y = 2") for line in detail["unified_diff"])
    assert any(line.startswith("+y = 3") for line in detail["unified_diff"])


def test_added_and_removed_modules_orient_left_to_right() -> None:
    """
    Verify one-sided modules classify as added (right-only) and removed
    (left-only).
    """
    strategy = SourceDiffStrategy()
    left = _material(sources={"mod.old": "a\n"})
    right = _material(sources={"mod.new": "b\n"})

    result = strategy.diff(left, right)

    assert result["added_modules"] == ["mod.new"]
    assert result["removed_modules"] == ["mod.old"]
    assert result["identical"] is False


def test_fingerprint_only_modules_stay_honest() -> None:
    """
    Verify no-text modules compare by fingerprint and never fabricate a
    diff body.
    """
    strategy = SourceDiffStrategy()
    left = _material(fingerprints={"mod.p": "print-1", "mod.q": "same"})
    right = _material(fingerprints={"mod.p": "print-2", "mod.q": "same"})

    result = strategy.diff(left, right)

    assert result["changed_modules"] == ["mod.p"]
    assert result["identical_modules"] == ["mod.q"]
    detail = result["module_diffs"]["mod.p"]
    assert detail["text_unavailable"] is True
    assert detail["left_fingerprint"] == "print-1"
    assert detail["right_fingerprint"] == "print-2"
    assert "unified_diff" not in detail


def test_strategy_cleanup_guards_use() -> None:
    """
    Verify cleanup semantics and use-after-clean guards.
    """
    strategy = SourceDiffStrategy()
    strategy.cleanup()
    strategy.cleanup()

    assert strategy.cleaned is True
    with pytest.raises(RuntimeError):
        strategy.diff(_material(), _material())


def test_terminal_newline_delta_reports_changed() -> None:
    """
    Regression (BUG-042): splitlines() erased a terminal-newline delta, so
    "x = 1\n" versus "x = 1" reported identical=True with no changed
    modules. Corrected behavior: the whole-module-text contract compares
    COMPLETE recorded text - the module reports changed with an explicit
    terminal-newline marker row.
    """
    strategy = SourceDiffStrategy()
    left = _material(sources={"mod.a": "x = 1\n"})
    right = _material(sources={"mod.a": "x = 1"})

    result = strategy.diff(left, right)

    assert result["identical"] is False
    assert result["changed_modules"] == ["mod.a"]
    assert any(
        "terminal newline" in row
        for row in result["module_diffs"]["mod.a"]["unified_diff"]
    )
