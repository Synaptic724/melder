- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The owner's review (chat 2026-10-19): "The rollback for notch is fine but it should still put the spell in an
    invalid state just incase for revalidation". It does, in Melder's terms: `gated` is the state whose next meld
    re-runs the checks, and `invalid` refuses every meld with no re-run (`Meld._ensure_lineage_resolvable`,
    `Meld._ensure_resolution_resolvable`). Probe on the mirror (S3 as in the worktree, plus S8), the same with the GIL
    off and on apart from the GIL-mode warning: after a notch to TimedGreeter is refused, the index state reads gated
    and tracks English, English's verdict in the world conduit reads gated, and TimedGreeter's reads gated with its
    check result cleared; one meld of English returns "hello" and leaves the index state and English's verdict valid.
    The marks are the seam's own (`register_index`, `mark_dependents_for_revalidation`, the verdicts set gated), from
    its run back toward English and its forward run to TimedGreeter; S8 adds no mark. Shown to the owner.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4002-4157
  - src/melder/aether/conduit/meld/meld.py:944-1021
  - src/melder/aether/conduit/meld/meld.py:1290-1351
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_refused_notch_marks.py:1-77
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_s3s8_mirror_gil0.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_s3s8_mirror_gil1.txt:1-25
  IMPACT: The owner's ask is met by the patch as built; S8's edit set is unchanged.
  NEXT: Act on the owner's answer on the turn-in (DECISION_REQUEST note).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
