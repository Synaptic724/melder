# Task: fix spell system validation strategy blueprint contract cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-spell-system-validation-strategy-blueprint-contract-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T11:57:58Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current Phase 6 system-validation strategy mypy cluster by aligning the
strategy `run(...)` signatures to the existing `IRootResolutionBlueprint`
public contract and cleaning the one remaining local `DagNode | None`
narrowing.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded Phase 6 strategy mypy cluster under
  `spell_crafter/system/validation`.
- EXECUTION_BOUNDARY:
  - directly implicated strategy files only:
    - `src/melder/spellbook/spell_crafter/system/validation/visibility_gap_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/socket_ref_sanity_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/scope_ordering_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/root_viability_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/root_scale_limit_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/root_reachability_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/root_lineage_conflict_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/root_coverage_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/ownership_consistency_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/missing_phase4_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/lineage_version_conflict_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/lineage_alignment_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/index_dependency_sanity_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/index_coverage_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/identity_mixing_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/graph_consistency_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/dependency_type_sanity_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/cycle_detection_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/contract_graph_cycle_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/contracted_version_drift_strategy.py`
    - `src/melder/spellbook/spell_crafter/system/validation/broken_spell_in_dag_strategy.py`
  - support contract only if truth requires it:
    - `src/melder/utilities/interfaces/irootresolutionblueprint.py`
    - `src/melder/spellbook/spell_crafter/system/validation/strategy_base.py`
- DEPENDENCIES:
  - existing `SpellSystemValidationStrategy.run(...)` base signature
  - current `IRootResolutionBlueprint` public contract
  - no casts, no shims, no fake local protocols
- EXIT_GATE:
  - the targeted strategy signature cluster is gone
  - the one local `DagNode | None` narrowing is corrected
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any strategy actually needs a
  concrete root-blueprint contract that `IRootResolutionBlueprint` does not
  truthfully expose

## Scope Boundaries
- In scope:
  - strategy `run(...)` signature alignment to `IRootResolutionBlueprint`
  - one local `DagNode | None` narrowing in `root_scale_limit_strategy.py`
- Out of scope:
  - unrelated system-validation mypy debt
  - broader root-blueprint interface redesign beyond directly implicated needs

## Steps / Checklist
- [ ] confirm `IRootResolutionBlueprint` already exposes everything the affected strategies use
- [ ] patch the strategy signatures to the interface contract
- [ ] patch the one local `DagNode | None` narrowing
- [ ] rerun targeted mypy on the bounded strategy set
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded Phase 6 strategy interface-alignment fix

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/system/validation/*.py` for the
  directly implicated strategy files only
- only if required by truthful fix:
  - `src/melder/utilities/interfaces/irootresolutionblueprint.py`
  - `src/melder/spellbook/spell_crafter/system/validation/strategy_base.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spell_crafter\system\validation`

## Risks / Rollback Notes
- Low risk. This looks like one interface/base-signature drift seam plus a
  single local narrowing.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T11:57:58Z
  TYPE: FACT
  CLAIM: The Phase 6 system-validation cluster is centered on one truthful
    interface seam: `SpellSystemValidationStrategy.run(...)` already declares
    `blueprints: dict[str, IRootResolutionBlueprint]`, but a large set of
    concrete strategies still use `dict[str, RootResolutionBlueprint]` in their
    overrides. One extra local residual remains in
    `root_scale_limit_strategy.py`, where `dag.get_node(...)` is not narrowed
    before use.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/system/validation/strategy_base.py:36-50
  - src/melder/utilities/interfaces/irootresolutionblueprint.py:1-33
  - src/melder/spellbook/spell_crafter/system/validation/visibility_gap_strategy.py:31-41
  - src/melder/spellbook/spell_crafter/system/validation/socket_ref_sanity_strategy.py:34-44
  - src/melder/spellbook/spell_crafter/system/validation/root_scale_limit_strategy.py:64-73
  - user_error_report: `root_scale_limit_strategy.py:191`
  IMPACT: This should be a straightforward interface-alignment lane, not a
    broader blueprint redesign.
  NEXT: patch the affected strategies to `IRootResolutionBlueprint`, then fix
    the local `DagNode | None` narrowing and rerun targeted mypy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:57:58Z
  TYPE: FACT
  CLAIM: The cluster stayed exactly where it first looked: concrete strategies
    were overspecifying `RootResolutionBlueprint` even though they only consume
    the published blueprint interface contract, and one local variable in
    `root_scale_limit_strategy.py` was reusing a name in a way that forced an
    unnecessary `DagNode | None` assignment error.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/system/validation/strategy_base.py:36-50
  - src/melder/utilities/interfaces/irootresolutionblueprint.py:1-33
  - src/melder/spellbook/spell_crafter/system/validation/root_scale_limit_strategy.py:176-196
  IMPACT: The correct fix was interface alignment plus one tiny local rename,
    not a broader root-blueprint redesign.
  NEXT: record the bounded validation result and move the lane to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:57:58Z
  TYPE: MEASURE
  CLAIM: The targeted Phase 6 strategy cluster is green. The affected system
    validation files show no file-local mypy output after switching the
    concrete strategy signatures to `IRootResolutionBlueprint`, and the full
    system-validation unit ring passes.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/system/validation/visibility_gap_strategy.py:1-108
  - src/melder/spellbook/spell_crafter/system/validation/socket_ref_sanity_strategy.py:1-175
  - src/melder/spellbook/spell_crafter/system/validation/root_scale_limit_strategy.py:1-216
  - src/melder/spellbook/spell_crafter/system/validation/strategy_base.py:1-67
  - src/melder/utilities/interfaces/irootresolutionblueprint.py:1-33
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spell_crafter\system\validation 2>&1 | Select-String 'src\\melder\\spellbook\\spell_crafter\\system\\validation\\'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_crafter\system\validation` -> `149 passed, 1 warning`
  IMPACT: The user-supplied Phase 6 strategy cluster is fixed without casts or
    interface churn beyond the already-canonical blueprint contract.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active Phase 6 system-validation strategy lane. Current evidence says the main
work is aligning concrete strategy overrides to the already-canonical
`IRootResolutionBlueprint` contract.
