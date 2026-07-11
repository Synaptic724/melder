import ast

import pytest

from melder.mutation_research.synthesis.structural_synthesizer import (
    StructuralSynthesizer,
)

BASE = (
    "import os\n"
    "\n"
    "def cast():\n"
    "    return 1\n"
    "\n"
    "def helper():\n"
    "    return 'base'\n"
    "\n"
    "class Widget:\n"
    "    size = 1\n"
)

DONOR = (
    "def cast():\n"
    "    return 2\n"
    "\n"
    "@staticmethod\n"
    "def fresh():\n"
    "    return 'donor'\n"
    "\n"
    "class Widget:\n"
    "    size = 2\n"
    "\n"
    "class Gadget:\n"
    "    pass\n"
)


def test_synthesize_replaces_same_named_function() -> None:
    """
    Verify a same-named donor function replaces the base body in place and
    the rest of the base survives untouched.
    """
    synthesizer = StructuralSynthesizer()

    verdict = synthesizer.synthesize(BASE, DONOR, take_functions=["cast"])

    composed = verdict["composed_source"]
    assert verdict["parse_error"] is None
    assert verdict["selections"] == [
        {"name": "cast", "kind": "function", "action": "replaced"},
    ]
    assert "return 2" in composed
    assert "return 1" not in composed
    assert "def helper():" in composed
    assert "import os" in composed
    ast.parse(composed)
    synthesizer.cleanup()


def test_synthesize_adds_new_parts_with_decorators() -> None:
    """
    Verify a donor part absent from the base appends at the tail WITH its
    decorators, and class selections work alongside function selections.
    """
    synthesizer = StructuralSynthesizer()

    verdict = synthesizer.synthesize(
        BASE,
        DONOR,
        take_functions=["fresh"],
        take_classes=["Widget", "Gadget"],
    )

    composed = verdict["composed_source"]
    actions = {
        (row["name"], row["kind"]): row["action"]
        for row in verdict["selections"]
    }
    assert actions[("fresh", "function")] == "added"
    assert actions[("Widget", "class")] == "replaced"
    assert actions[("Gadget", "class")] == "added"
    assert "@staticmethod" in composed
    assert "size = 2" in composed
    assert "size = 1" not in composed
    assert "class Gadget:" in composed
    ast.parse(composed)
    synthesizer.cleanup()


def test_synthesize_unknown_selection_refuses_loudly() -> None:
    """
    Verify an unknown donor selection raises teach-grade, naming what the
    donor actually carries.
    """
    synthesizer = StructuralSynthesizer()

    with pytest.raises(ValueError, match="no top-level function 'missing'"):
        synthesizer.synthesize(BASE, DONOR, take_functions=["missing"])
    with pytest.raises(ValueError, match="Gadget"):
        synthesizer.synthesize(BASE, DONOR, take_classes=["Missing"])
    synthesizer.cleanup()


def test_synthesize_validates_inputs() -> None:
    """
    Verify empty sources and empty selections refuse before any parsing.
    """
    synthesizer = StructuralSynthesizer()

    with pytest.raises(ValueError, match="base_source"):
        synthesizer.synthesize("", DONOR, take_functions=["cast"])
    with pytest.raises(ValueError, match="donor_source"):
        synthesizer.synthesize(BASE, "", take_functions=["cast"])
    with pytest.raises(ValueError, match="at least one selection"):
        synthesizer.synthesize(BASE, DONOR)
    synthesizer.cleanup()


def test_synthesize_parse_errors_answer_honestly() -> None:
    """
    Verify unparseable text on either side answers a parse_error row that
    names the side - never raises, never composes.
    """
    synthesizer = StructuralSynthesizer()
    broken = "def broken(:\n"

    base_bad = synthesizer.synthesize(
        broken, DONOR, take_functions=["cast"],
    )
    assert base_bad["parse_error"]["side"] == "base"
    assert base_bad["composed_source"] is None

    donor_bad = synthesizer.synthesize(
        BASE, broken, take_functions=["cast"],
    )
    assert donor_bad["parse_error"]["side"] == "donor"
    assert donor_bad["composed_source"] is None
    synthesizer.cleanup()


def test_synthesize_cleanup_guards_dispatch() -> None:
    """
    Verify the cleaned synthesizer refuses further work (Cleanable law).
    """
    synthesizer = StructuralSynthesizer()
    synthesizer.cleanup()
    synthesizer.cleanup()

    with pytest.raises(RuntimeError):
        synthesizer.synthesize(BASE, DONOR, take_functions=["cast"])
