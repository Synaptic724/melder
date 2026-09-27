"""Update the tests that pinned the old stop-at-first-failure posture (melder_0, 2026-09-27). Usage: python apply_test_updates.py <repo root>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eol_lines
replace_lines = eol_lines.replace_lines

root = sys.argv[1]
reg = os.path.join(root, "tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py")
unit = os.path.join(root, "tests/unit/melder/aether/conduit/creations/test_creations.py")
edits = [
    (reg, """    The failure posture is pinned in its own test rather than assumed: the first
    failing method currently ends disposal for that entry and surfaces one
    error. That is the accepted current behaviour, not a guarantee - if disposal
    later aggregates per-method failures the way
    `_dispose_disposable_registry` already aggregates per-entry ones, the
    failure test is the one to update.
""", """    The failure posture is pinned in its own test rather than assumed. Until
    2026-09-27 the first failing method ended disposal for that entry and
    surfaced one error; this file pinned that posture so a change would be a
    deliberate edit. The owner then ruled that per-method failures aggregate
    the way `_dispose_disposable_registry` already aggregates per-entry ones,
    so the failure test now asserts that the methods declared after a failing
    one still run. The full failure contract (one chained error per failing
    method, safe error text) is covered by
    `test_creations_disposal_failure_aggregation_regression.py`.
"""),
    (reg, """    Purpose:
        Pin the current failure posture: disposal of one entry stops at the
        first raising method rather than continuing through the remainder.

    Contract:
        - `close()` records the call and then raises.
        - `flush()` records the call; reaching it would prove the posture
          changed.
""", """    Purpose:
        Pin the failure posture: a raising first method does not stop the
        entry's remaining methods (owner decision, 2026-09-27).

    Contract:
        - `close()` records the call and then raises.
        - `flush()` records the call; it must still be reached after `close()`
          fails.
"""),
    (reg, '''def test_first_failing_method_ends_disposal_for_that_entry() -> None:
    """PINS CURRENT POSTURE - not a guarantee.

    Disposal of one entry stops at the first raising method and surfaces one
    error through the aggregated `ExceptionGroup`. If per-method failures are
    later collected the way per-entry failures already are, THIS is the test to
    update - the three above stay valid either way.

    Contract assertions:
        - The failing method ran.
        - The method declared after it did not.
        - Exactly one error reached the caller for this entry.
    """
''', '''def test_first_failing_method_does_not_end_disposal_for_that_entry() -> None:
    """PINS THE FAILURE POSTURE (updated 2026-09-27 on the owner's ruling).

    A raising method no longer ends disposal of its entry: the method declared
    after it still runs, and the one failure reaches the caller through the
    aggregated `ExceptionGroup`. Until 2026-09-27 this test asserted the
    opposite (disposal stopped at the first raising method).

    Contract assertions:
        - The failing method ran.
        - The method declared after it also ran.
        - Exactly one error reached the caller for this entry.
    """
'''),
    (reg, """    assert probe.calls == ["close"], (
        "expected disposal to stop at the first failing method; "
        f"got {probe.calls}"
    )
""", """    assert probe.calls == ["close", "flush"], (
        "expected the method after a failing one to still run; "
        f"got {probe.calls}"
    )
"""),
    (unit, '''def test_attempt_cleanup_missing_method_returns_runtimeerror(
        creations: Creations,
) -> None:
    """
    Verify disposal failures are wrapped when a method cannot be resolved.
    """
    result = creations._attempt_cleanup((object(), ["dispose"]))

    assert isinstance(result, RuntimeError)
    assert "Failed to dispose object" in str(result)
''', '''def test_attempt_cleanup_missing_method_returns_one_chained_runtimeerror(
        creations: Creations,
) -> None:
    """
    Verify a method that cannot be resolved is one wrapped failure.

    Since 2026-09-27 the helper returns every failure as a list, and each
    wrapped error is chained from the exception the method lookup raised.
    """
    result = creations._attempt_cleanup((object(), ["dispose"]))

    assert len(result) == 1
    assert isinstance(result[0], RuntimeError)
    assert "Failed to dispose object" in str(result[0])
    assert isinstance(result[0].__cause__, AttributeError)
'''),
    (unit, '''def test_attempt_cleanup_no_methods_returns_none(creations: Creations) -> None:
    """
    Verify empty disposal method lists are treated as no-op.
    """
    probe = Probe()

    assert creations._attempt_cleanup((probe, [])) is None
''', '''def test_attempt_cleanup_no_methods_returns_no_errors(creations: Creations) -> None:
    """
    Verify empty disposal method lists are treated as no-op (no errors returned).
    """
    probe = Probe()

    assert creations._attempt_cleanup((probe, [])) == []
'''),
]
for path, old, new in edits:
    print(os.path.basename(path), replace_lines(path, old, new))
