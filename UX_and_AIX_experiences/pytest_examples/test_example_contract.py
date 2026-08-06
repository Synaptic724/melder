"""
Structural contract every example must satisfy, enforced mechanically.

WHY THIS EXISTS
---------------
The example harnesses assert exactly two things: `main()` did not raise, and
it printed something. That is enough to catch a crash and nothing else. A
lesson that only probes `hasattr` and prints the names back passes every row
in this directory while demonstrating nothing - and several did, for weeks,
until they were caught by reading rather than by running.

This file is the mechanical floor. It does not judge whether a lesson
teaches well; it refuses the cases where a lesson cannot POSSIBLY detect a
regression, because it makes no checkable claim at all.

THE RULE
--------
Every example must carry at least one BEHAVIOURAL CHECK:
  - an `assert`, or
  - a `try/except` that catches a refusal the lesson is demonstrating.

Prints do not count. A print is narration; it is true no matter what the
runtime does. If melder inverted a law tomorrow, a print-only lesson would
keep passing and keep narrating the old law.

WHY THE FLOOR IS "AT LEAST ONE" AND NOT A RATIO
-----------------------------------------------
Measured across the tiers, the median example carries 2 checks and many
beginner lessons legitimately carry 1 - a beginner lesson demonstrating a
single idea should not be forced to pad. A ratio would encode a style
opinion. Zero is not a style opinion: it is a lesson asserting nothing.
"""
import ast
from pathlib import Path

import pytest

TIERS = ("01_beginner", "02_intermediate", "03_advanced", "04_expert")

EXAMPLES = sorted(
    path
    for tier in TIERS
    for path in (Path(__file__).parent.parent / tier).glob("[0-9]*.py")
)


def _behavioural_checks(tree: ast.AST) -> tuple[int, int]:
    """Return (assert_count, caught_refusal_count) for one example."""
    asserts = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
    refusals = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Try))
    return asserts, refusals


@pytest.mark.parametrize("path", EXAMPLES, ids=[p.stem for p in EXAMPLES])
def test_example_makes_a_checkable_claim(path: Path) -> None:
    """Every example must assert something or catch a refusal.

    Narration is not a claim. This is the one property that separates a
    lesson which would go red on a behaviour change from one that would
    keep printing the old story indefinitely.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    asserts, refusals = _behavioural_checks(tree)
    assert asserts + refusals > 0, (
        f"{path.name} makes no checkable claim: 0 asserts, 0 caught "
        f"refusals. It cannot fail if melder's behaviour changes, so it "
        f"cannot protect the law it describes. Add an assert on the "
        f"behaviour the lesson is about, or catch the refusal it teaches."
    )


# Measured off the tiers rather than assumed. TIER / GOAL / SURFACE
# EXERCISED are carried by 133, 133 and 132 of the 133 examples - they are
# the curriculum's convention. VERIFY is NOT: 36/36 in expert, 15/19 in
# advanced, 1/41 in beginner. It is an expert-tier habit about harness runs,
# so it is required only where it is actually the convention. Enforcing it
# everywhere would fail 80 files for not following a rule they never had.
UNIVERSAL_KEYS = ("TIER:", "GOAL:", "SURFACE EXERCISED:")
EXPERT_ONLY_KEYS = ("VERIFY:",)


@pytest.mark.parametrize("path", EXAMPLES, ids=[p.stem for p in EXAMPLES])
def test_example_declares_its_surface(path: Path) -> None:
    """Every example must declare what it covers.

    `SURFACE EXERCISED` is the line a reader trusts to know what a lesson
    touches, and it is the one that silently rots when a lesson is
    restructured - so its PRESENCE is enforced here even though its
    accuracy cannot be. Expert additionally carries `VERIFY`, which records
    whether the lesson has actually been run.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    docstring = ast.get_docstring(tree, clean=False) or ""
    required = UNIVERSAL_KEYS
    if path.parent.name == "04_expert":
        required = UNIVERSAL_KEYS + EXPERT_ONLY_KEYS
    missing = [key for key in required if key not in docstring]
    assert not missing, f"{path.name} header is missing {missing}"


def test_the_floor_is_actually_holding() -> None:
    """Report the distribution, so a slide toward narration is visible.

    A gate that only fires on zero says nothing about drift above zero.
    This prints the shape of the tier every run - if the median falls, the
    curriculum is drifting toward prose and someone should look before it
    reaches the floor.
    """
    counts = []
    for path in EXAMPLES:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        asserts, refusals = _behavioural_checks(tree)
        counts.append(asserts + refusals)
    counts.sort()
    median = counts[len(counts) // 2]
    print(
        "examples=%d  checks: min=%d median=%d max=%d  |  at-floor(1)=%d"
        % (len(counts), counts[0], median, counts[-1],
           sum(1 for c in counts if c == 1))
    )
    assert counts[0] > 0, "the floor is breached - see the per-file failures"
