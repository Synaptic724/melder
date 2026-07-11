import pytest

from melder.mutation_research.diff.strategies.part_diff_strategy import (
    PartDiffStrategy,
)

LEFT = (
    "import os\n"
    "LIMIT = 1\n"
    "\n"
    "def cast():\n"
    "    return 1\n"
    "\n"
    "def gone():\n"
    "    return 'left-only'\n"
    "\n"
    "class Widget:\n"
    "    size = 1\n"
)

RIGHT = (
    "import os\n"
    "LIMIT = 2\n"
    "\n"
    "def cast():\n"
    "    return 2\n"
    "\n"
    "class Widget:\n"
    "    size = 1\n"
    "\n"
    "@staticmethod\n"
    "def fresh():\n"
    "    return 'right-only'\n"
)


def _material(text: str, spell_id: str) -> dict:
    """
    Build one single-module material payload.

    Args:
        text:
            Module source text.
        spell_id:
            Material identity stamp.

    Returns:
        dict: Resolver-shaped material.
    """
    return {
        "spell_id": spell_id,
        "sources": {"mod.a": text},
        "fingerprints": {},
    }


def test_parts_strategy_shows_everything_at_class_grain() -> None:
    """
    Verify the owner's grain choice: added/removed parts arrive WITH their
    full code, changed parts arrive as unified diffs, identical parts by
    name, and the module body residue (imports/constants) is compared as
    its own region so nothing escapes.
    """
    strategy = PartDiffStrategy()

    result = strategy.diff(
        _material(LEFT, "sha-l"), _material(RIGHT, "sha-r"),
    )

    assert result["identical"] is False
    assert result["changed_modules"] == ["mod.a"]
    report = result["module_reports"]["mod.a"]

    added = {row["name"]: row for row in report["added_parts"]}
    assert "fresh" in added
    assert added["fresh"]["text"].startswith("@staticmethod")

    removed = {row["name"]: row for row in report["removed_parts"]}
    assert "gone" in removed
    assert "left-only" in removed["gone"]["text"]

    changed = {row["name"]: row for row in report["changed_parts"]}
    assert "cast" in changed
    assert any("return 2" in line for line in changed["cast"]["unified_diff"])
    # LIMIT changed inside the module body residue region.
    assert "<module_body>" in changed
    assert "Widget" in report["identical_parts"]
    strategy.cleanup()


def test_parts_strategy_identical_and_honest_arms() -> None:
    """
    Verify identical texts report clean, fingerprint-only modules ride
    text_unavailable_modules, and unparseable source reports per-module
    naming the failing side.
    """
    strategy = PartDiffStrategy()

    same = strategy.diff(
        _material(LEFT, "sha-1"), _material(LEFT, "sha-2"),
    )
    assert same["identical"] is True
    assert same["module_reports"] == {}

    unavailable = strategy.diff(
        {"spell_id": "a", "sources": {}, "fingerprints": {"mod.x": "p1"}},
        {"spell_id": "b", "sources": {}, "fingerprints": {"mod.x": "p2"}},
    )
    assert unavailable["text_unavailable_modules"] == ["mod.x"]

    broken = strategy.diff(
        _material("def broken(:\n", "sha-bad"), _material(RIGHT, "sha-r"),
    )
    assert "left" in broken["module_reports"]["mod.a"]["parse_error"]
    strategy.cleanup()


def test_parts_strategy_cleanup_guards_dispatch() -> None:
    """
    Verify the cleaned strategy refuses further work (Cleanable law).
    """
    strategy = PartDiffStrategy()
    strategy.cleanup()
    strategy.cleanup()

    with pytest.raises(RuntimeError):
        strategy.diff(_material(LEFT, "a"), _material(RIGHT, "b"))
