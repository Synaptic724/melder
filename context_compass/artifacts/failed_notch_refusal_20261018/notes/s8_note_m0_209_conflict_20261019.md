- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: M0-209 from melder_0 (2026-10-19T10:50:30Z), consumed after the re-onboarding: the owner gave S3
    (STORY-2026-10-17-parked_cleanup_leaves_borrower_copies) its go in melder_0's chat and melder_0 takes it -
    `Conduit.cleanup_spell` removes a version from every contract that holds it before the Book disposes it, and
    the direct `Spellbook.cleanup_spell` takes the same path; melder_0 writes conduit.py, spellbook.py and, if the
    patch needs it, conduit_ward.py, notches above 0.2.8260 at landing, and asks to be told before they are
    edited. That crosses the order the owner gave melder_1 (DECISION note of 2026-10-19T10:34:26Z: S1, S3, S2, S8,
    S5, all with melder_1) and M1-45's line "S3 comes to melder_1 too". S3 is in progress with melder_0, so
    melder_1 does not take it: after S8 it goes on with S1, S2 and S5, and asks the owner about S3 only if
    melder_0 hands it back.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:329-350
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:456-475
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:561-581
  IMPACT: S8's files stay with melder_0 until it answers M1-45 or lands S3; S8 lands after S3 and notches above it.
  NEXT: Add the shared-key refinement and the preface's line-break refusal to the patch docs, then build the
    rollback in the mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
