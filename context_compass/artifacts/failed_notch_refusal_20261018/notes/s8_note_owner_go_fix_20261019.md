- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's go for the fix, now (chat 2026-10-19). Asked "are you saying notch doesn't roll back?" and told
    that today it does not - its check fails after the switch and nothing in src/melder registers a rollback or an
    abort hook for it - he answered "yes go ahead and fix this ... it should roll back properly", and asked that
    the code be explained properly. So S8 is fixed now, ahead of S1, S3, S2 and S5 (his order for those stands),
    as the patch docs give it: the check inside the notch window and, when it fails, an undo of everything the seam
    did - English active, selected, claimed and routed again, the refused version parked and unchecked, borrowers
    untouched, nothing journaled or published for the refused version - with the shared-address refinement (FACT
    note of 2026-10-18T13:11:11Z), which a proper rollback needs on today's tree; the patch docs take it first.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:242-242
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:534-560
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:445-526
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-62
  IMPACT: S8's hold is lifted; the four files go to melder_1 for S8 by message (M1-45); S1 follows S8.
  NEXT: Send M1-45; add the refinement to the patch docs; implement and test in the mirror while melder_0 answers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
