- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The HYPOTHESIS of 11:41:48Z, measured at 12:08:58Z and read whole on 0.2.8260, is filed as
    STORY-2026-10-19-notch_back_keeps_outgoing_dependencies (ready, unassigned, p2) under
    EPIC-2026-10-17-correctness_defects: `_apply_notch` never writes the lineage's dependencies and a notch to a
    compiled version runs no Phase 3, so the outgoing version's dependencies stay; a borrower's consumer melding
    first is refused by `VisibilityGapStrategy` and its verdict stays `invalid`. A fourth case joined the probe -
    H4, a notch to French and straight back with no meld between - refused and stuck the same way. The story's
    reproducer is rowed on the artifact board; melder_0, the epic's writer, is told by M1-47.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-19_notch_back_keeps_outgoing_dependencies_story.md:1-212
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt:1-55
  IMPACT: S8's own scope is unchanged (its reversal restores the dependencies for a refused notch only); the plain
    notch-back case waits for the owner's scheduling.
  NEXT: Wait for melder_0's hand-over of spellbook.py and conduit.py after S3, then apply S8 to the repository.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
