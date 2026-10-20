- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8255, the current tree, re-verified before any change as the owner asked. melder_0's
    probe, copied with its one call renamed for 0.2.8253 (`find_spell_by_id` -> `find_spell_by_spell_id`; for an
    active spell_id both return the same Spell), ran on Python 3.14.7t with the GIL off and on; the output is
    byte-equal to his 0.2.8252 run apart from the GIL-mode warning. N1 (French, sound): owner and borrower follow. N2
    (SelfMade, SELF_DEPENDENCY): `notch_spell` raises SpellbookValidationError "Broken spells: SelfMade.", yet the
    lender's index selects SelfMade with English parked, the borrower keeps English active, the lender's meld by
    address raises that error and `meld(spell_id=English)` KeyError. N3: a notch back to English restores both sides.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_failed_notch_commit_0_2_8255.py:1-175
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_gil0.txt:1-34
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_gil1.txt:1-38
  IMPACT: Nothing landed since 0.2.8252 changed the failure; the acceptance criteria stand as written.
  NEXT: Choose the mechanism from the commit path as read on 0.2.8255 (FACT note), then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
