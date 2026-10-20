- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8255, re-verified before any change as the owner asked. melder_0's probe, copied
    with its two calls renamed for 0.2.8253 (`find_spell_by_id` -> `find_spell_by_spell_id`; for an active spell_id
    both return the same Spell), ran on Python 3.14.7t: with the GIL off its output equals his 0.2.8252 run with the
    ids masked, and with the GIL on it is the same apart from the GIL-mode warning. D1: `cleanup_spell(English)` is
    refused, nothing changes. D2 (`English.cleanup()`) and D3 (`cleanup_and_remove_spell(english_id)`), French
    parked on English's index: the index is cleaned; French stays parked in the Book, uncleaned, unknown to the
    frame; a notch to it raises AttributeError, `add_to_spell_index` and `cleanup_spell` raise "SpellIndex has
    already been cleaned."; the root's teardown leaves it and `French.cleanup()` then raises "Spellbook has already
    been cleaned."; the borrower keeps an active copy of the cleaned English and a parked copy of French.
  EVIDENCE:
  - context_compass/artifacts/direct_cleanup_refusal_20261018/probes/probe_direct_cleanup_active_member_0_2_8255.py:1-190
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_0_2_8255_gil0.txt:1-49
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_0_2_8255_gil1.txt:1-53
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil0.txt:1-49
  IMPACT: Nothing landed since 0.2.8252 changed the failure; the acceptance criteria stand as written.
  NEXT: The removal path read whole (FACT note), then the patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
