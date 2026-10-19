- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The half-switch is not about recursion; proven on 0.2.8260 with the GIL off and on. A version broken for
    an ordinary reason - TimedGreeter, whose `clock: Clock` parameter has two registered providers (UtcClock,
    LocalClock) - is staged without error; `notch_spell` to it raises SpellbookValidationError
    [AMBIGUOUS_PROVIDER], and afterwards the lender's index selects TimedGreeter, `meld(spell_id=English)` raises
    KeyError, a meld by the greeter address raises KeyError (TimedGreeter staged at its own address) and the
    borrower's consumer `Speaker` is refused (SpellbookValidationError naming Speaker) - the state SelfMade
    leaves. Side by side, Melder gives each version its real reason at the notch and at every meld: SelfMade
    "depends on itself ... [SELF_DEPENDENCY]", TimedGreeter "... 2 registered spells provide it ...
    [AMBIGUOUS_PROVIDER]". The checks are right; the switch they follow is never undone. The owner asked for
    this proof (chat 2026-10-19: "make a test for this and prove this can happen because this looks like
    recursion"; "so your claiming melder doesn't catch a recursion loop in its checks?") and was shown it.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_failed_switch_plain.py:1-100
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_0_2_8260_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_0_2_8260_gil1.txt:1-17
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_failed_notch_two_reasons.py:1-91
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_two_reasons_0_2_8260.txt:1-76
  IMPACT: The defect is the notch's order - switch, then check, no undo - whatever the check finds, so the fix in
    the patch docs (an undo inside the window) must and does cover any failing check, not only a self-dependency.
  NEXT: Add symptom-named regression tests with TimedGreeter to the S8 integration file (red today) and run them
    with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
