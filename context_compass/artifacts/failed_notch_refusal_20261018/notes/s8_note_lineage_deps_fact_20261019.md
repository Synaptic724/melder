- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The red set on the mirror (0.2.8260 plus the S8 edits) found one more thing the reversal must put back: the
    check's Phase 3 registers the refused version's dependencies and topology on the lineage
    (`update_dependencies`, `register_local_topology`), and the seam run back leaves them. SelfMade depends on
    itself, so after the refusal the lineage read English as depending on SelfMade, and the borrower's first meld of
    `Speaker` - whose catch-up had nothing to refresh, its topology an UNRESOLVED_INPUT socket from before the link -
    was refused by VisibilityGapStrategy: "Spell 'English' depends on spells this Spellbook cannot see (spell id
    3f1c78b54469)" [visibility_gap_dependency_filtered], GIL off and on; the TimedGreeter twin passed, an ambiguous
    socket registering no dependency. `_notch_spell` now records the lineage's direct dependencies and the outgoing
    version's topology before the switch, and the reversal restores both after the seam run back. All 25 S8 tests
    pass with the GIL off and on (14 integration, 11 unit with the four new line-break cases); the probe shows the
    lineage back on no dependencies and the borrower's meld of `Speaker` ok.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1203-1212
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:757-817
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1789-1845
  - src/melder/aether/spellbook/spell_compiler/system/validation/visibility_gap_strategy.py:43-120
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/dbg_refused_notch_lineage_dependencies.py:1-48
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/dbg_refused_notch_lineage_dependencies_fix_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_green_gil0.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_green_gil1.txt:1-10
  IMPACT: The patch's invariant "SpellSystemStates tracks the restored version" widens to its dependency registration;
    the component patch and the architecture invariants say so before the code lands.
  NEXT: Add the dependency restore to the patch docs, then run the seven whole-tree shards with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: HYPOTHESIS
  CLAIM: The same leftover may follow an ordinary notch back, outside S8: a notch back to a version compiled before
    runs no Phase 3 (`_check_notched_version` and the commit validator both skip it), so the lineage keeps the
    dependencies the version notched away registered until the restored version's next structural rerun. If one of
    them is not visible to a borrower, the borrower's consumer melding before the lender could be refused for a
    dependency the restored version does not have. Unprobed; not changed by S8.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4002-4157
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:757-817
  - src/melder/aether/spellbook/spell_compiler/system/validation/visibility_gap_strategy.py:43-120
  IMPACT: A possible defect for EPIC-2026-10-17-correctness_defects (a borrower stuck until its lender melds).
  NEXT: Probe it after S8 lands (a version with a lender-only dependency, a notch away and back, the borrower's
    consumer melding first) and file a story under the epic if it holds.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
