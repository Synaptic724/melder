- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8259, re-verified before any change as the owner asked. melder_0's probe, copied
    with the 0.2.8253 rename (`find_spell_by_id` -> `find_spell_by_spell_id`) and T5's parked version made its own
    class (one object is one spell since 0.2.8257), ran on Python 3.14.7t; with the GIL on the output equals the
    GIL-off run apart from the GIL-mode warning. T2: after the root's teardown English and the shared index are
    cleaned, French (parked on it) is not, and `French.cleanup()` raises "Spellbook has already been cleaned.". T3:
    French alone in the index `remove_from_spell_index` minted - neither French nor that index is cleaned. T1
    (active only) and T5 (both managed versions' pools unregistered) are right; T4 belongs to the notch-signature
    story and is unchanged. S4's teardown edit (0.2.8259) changed none of it.
  EVIDENCE:
  - context_compass/artifacts/book_teardown_parked_20261019/probes/probe_book_teardown_parked_0_2_8259.py:1-242
  - context_compass/artifacts/book_teardown_parked_20261019/runs/probe_book_teardown_parked_0_2_8259_gil0.txt:1-30
  - context_compass/artifacts/book_teardown_parked_20261019/runs/probe_book_teardown_parked_0_2_8259_gil1.txt:1-34
  IMPACT: The acceptance criteria stand as written.
  NEXT: Read the Book teardown whole (FACT note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
