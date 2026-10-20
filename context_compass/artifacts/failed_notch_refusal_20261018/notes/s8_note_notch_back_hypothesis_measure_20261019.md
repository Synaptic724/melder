- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The HYPOTHESIS of 11:41:48Z holds for an ordinary notch back, outside S8, on 0.2.8260 (the git index's
    src, exported), the same with the GIL off and on. English (no dependencies) active; French, which needs Accent,
    staged; Accent bound only in the lender's Book; a borrower links, contracts the index and binds
    Speaker(greeter: Greeter). The lender notches to French and melds it (the lineage reads deps [Accent]), then
    notches back to English: the lineage still reads deps [Accent], gated. H3 - the borrower's Speaker never melded
    before: its first meld is refused, "Spell 'English' depends on spells this Spellbook cannot see (spell id
    6e9578a406c6 [Accent]) ... [visibility_gap_dependency_filtered]"; the lender's meld of English then clears the
    lineage to deps [], yet every later meld of Speaker is refused, "Broken spells: Speaker ... No validation error
    was recorded for this spell; its validity is invalid, gated or disabled.": the borrower is stuck. H1 - the
    borrower melded Speaker before the notches: its meld after the notch back is "hello" (its recorded topology
    names English, so the meld's catch-up refreshes the gated lineage first). H2 - the lender melds English first:
    "hello". Not yet read whole: why the catch-up skips English in H3 and why nothing re-gates Speaker's verdict.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_notch_back_lineage_dependencies.py:1-105
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt:1-42
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil1.txt:1-54
  IMPACT: A defect for EPIC-2026-10-17-correctness_defects, independent of S8 (S8's reversal restores the
    dependencies for a refused notch only): a notch back can leave a borrower's consumer refused for good.
  NEXT: Read the paths whole (the notch's lineage re-registration, the meld gate and its catch-up, the visibility
    strategy, the verdict that stays invalid), then file a story under the epic and tell melder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
