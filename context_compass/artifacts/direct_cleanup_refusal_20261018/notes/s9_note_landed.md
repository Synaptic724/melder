- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Landed and turned in at 0.2.8256 on the owner's word (DECISION note of 2026-10-18T16:02:48Z: "... notch
    0.2.8256, closure and rebuild"). `__version__` still read 0.2.8255 (no one notched meanwhile, no new message)
    and is notched to 0.2.8256. The running release note's header reads "# Melder 0.2.8256", and a new section, "A
    cleanup of an index's active version is refused while parked versions remain" (the Breaking change, the three
    remedies, `cleanup_spell`'s reworded message, what stays the same), comes before Packaging, which gains the
    system-documents line and the rebuild line for 0.2.8256; its example runs as written with the GIL off and on
    (probe_release_note_s9.py, cases E1-E4: the refusal, each remedy, `cleanup_spell`'s message). Acceptance: the
    criteria hold (MEASURE note); no independent review was asked for - the closure is on the owner's word. Turn-in:
    Completed and Summary at the top, Status done, the move to completed/, the board's row and detail out with a
    closed anchor and the notch notice, the artifact rows cleared (the lane folder and the probe retained as
    reference, the patch promoted and archived under system_docs/patches/completed/), M1-38, the rebuild last.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:903-959
  - release_docs/next_version_release.md:1060-1063
  - context_compass/artifacts/direct_cleanup_refusal_20261018/probes/probe_release_note_s9.py:1-65
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_release_note_s9_gil0_gil1.txt:1-15
  IMPACT: S9 is done; spellbook.py and spell.py go back to melder_0 for S1 (M1-38), which notches above 0.2.8256.
  NEXT: M1-38 and the rebuild; then S4, re-verified on the current tree before any change.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
