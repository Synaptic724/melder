- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The three readers the FACT note named, probed on 0.2.8256 (new probe M4-M7, Python 3.14.7t; the GIL-on
    output equals the GIL-off one apart from the GIL-mode warning). M4: another Book of the frame binds French
    (same class, address and existence, so French's spell_id). Control (a), French parked in English's index: both
    binds refused, "Spell ID collision detected". (b), French alone in the minted index: a conjured Book's
    post-conjure bind is ACCEPTED - two Books of one frame hold French's spell_id - and an unconjured Book's bind is
    accepted too, its conjure then refused ("Conjure refused: 1 spell(s) owned by this ..."). M5: a Book of another
    frame under process-wide spell ids (the default) - the same answers as M4. M6: root 'lender' torn down with
    French parked alone in the minted index - nothing was ever registered for it, so nothing is left behind. M7: a
    transfer by spell_id of French, notched active in the minted index, is refused: ValueError "Spell version <id>
    not found in any conduit.".
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_minted_index_fix_cases.py:1-198
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_fix_cases_0_2_8256_gil0.txt:1-32
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_fix_cases_0_2_8256_gil1.txt:1-36
  IMPACT: The defect is wider than lookups: bind's collision guard (`Aether._check_for_spell`) misses a version in a
    minted index, so its spell_id can be bound again in the frame and in other frames, and an ownership transfer by
    spell_id is refused. The regression tests take M4b, M5b and M7 as acceptance cases.
  NEXT: Record the prototypes of the three edits (MEASURE note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
