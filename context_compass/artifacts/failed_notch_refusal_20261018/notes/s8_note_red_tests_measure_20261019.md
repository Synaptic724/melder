- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Two symptom-named regression tests with the no-recursion version join the S8 integration file -
    test_a_notch_refused_for_an_ambiguous_provider_leaves_the_old_version_active and
    test_a_notch_refused_for_an_ambiguous_provider_leaves_borrowers_on_the_lenders_version (Clock, UtcClock,
    LocalClock and TimedGreeter; `_world(clocks=True)` binds the two clocks), and the file's docstring names both
    broken versions. On 0.2.8260 the S8 red set is 20 failed, 1 passed, the same list with the GIL off and on:
    13 integration and 7 unit failures, each for the defect's reason (the index selects the broken version, the
    borrower's Speaker is refused, English is unclaimed and does not meld, `preface` does not exist yet); the
    pass is the standing-notch journal control. The two new tests fail where the SelfMade ones do: at the index
    selection (TimedGreeter selected) and at the borrower's Speaker meld.
  EVIDENCE:
  - tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py:93-134
  - tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py:249-295
  - tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py:422-459
  - context_compass/artifacts/failed_notch_refusal_20261018/scripts/add_ambiguous_provider_tests.py:1-206
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_red_0_2_8260_gil0.txt:1-100
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_red_0_2_8260_gil1.txt:1-108
  IMPACT: The fix's acceptance now proves the refusal for any failing check, not only a self-dependency; the red
    set is the patch mapping's validation step on today's tree.
  NEXT: Re-check the patch against 0.2.8260, after the identity landings (FACT note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
