# Task: Author the structural-snapshot patch docs (architecture, SpellCompiler component, hydrator control flow)

## Metadata
- Task ID: TASK-2026-09-26-author-structural-snapshot-patch-docs
- Story: STORY-2026-09-26-structural-snapshot
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T15:03:58Z
- Updated: 2026-09-26T15:44:18Z

## Objective
Write the patch-framework entry-gate artifacts for I-1 under
`system_docs/patches/active/structural_snapshot_2026_09_26/`: `architecture_patch.md` (two-tier key, placement,
capture-on-valid rule, refusal rule, no raw index ULIDs, generation coordination), `component_patch_spell_compiler.md`
(row schemas per phase from the D2 table and the dormant phase 2-5 export; hydrate = registry replay + blueprint
rebuild + one revalidator registration + Spell flags; before/after of the conjure cache path) and
`code_description_patch_structural_hydrator.md` (control flow, edge/error semantics, idempotency, non-goals),
after re-reading the S3b cache path so the docs describe the tree as it is.

## Ticket Contract
- ENTRY_GATE: The four rulings (a)-(d) recorded in the story's Decision Log; the active board row routes here.
- EXECUTION_BOUNDARY: the three patch docs and this ticket; reads of `caching_system.py`,
  `spellbook_creation_system.py` (cache classification, `_stage_spell_payloads_at_conjure_end`, the full-hit
  branch), `SpellSystemStates` write helpers, `compiler_phase_5.py` attach seams and `shared_compiler_executions.py`
  `capture_phase2_5_codegen_ir`. No edit under `src/`.
- DEPENDENCIES: summary.md D1-D6 and the records it cites; melder_0's S3b state of the cache path.
- EXIT_GATE: three patch docs present, linked from the story and this task, artifact-board row added; consumption
  mapping (patch section -> implementation task -> validation) recorded here; owner reviews before task 2 opens.
- FAILURE_ESCALATION: DECISION_REQUEST if a D2 write cannot be expressed as rows; CONFLICT if the cache path is
  under concurrent edit by melder_0 at authoring time (the docs then describe their landed shape).

## Scope Boundaries
- In scope: the three patch docs; the consumption mapping; UNKNOWN resolution by reading the named files.
- Out of scope: any `src/` or test edit; the generation bump itself.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Story opened (2026-09-26T15:03:58Z); waiting on the owner's rulings (a)-(d) before authoring.
- from_state: ready
- to_state: in_progress
- transition_reason: Design shape settled with the owner (story DECISION 2026-09-26T15:37:00Z): 1-4 only, per-spell rows, no
  refusal, normal regeneration for non-replayable spells; authoring starts at A1.

## Steps / Checklist
- [ ] A1: rulings recorded (story DECISION 2026-09-26T15:37:00Z); re-read the S3b cache path (caching_system.py, the creation system's
      classification/staging/full-hit branch) and the phase-5 attach seams; note the deltas since the survey.
- [ ] A2: architecture_patch.md (objective/non-goals, changed components, key tiers, placement, invariants,
      migration order, rollback, coverage matrix).
- [ ] A3: component_patch_spell_compiler.md (row schemas per phase; before/after of the conjure cache path;
      interface deltas; validation expectations).
- [ ] A4: code_description_patch_structural_hydrator.md (control flow in D2 order; edge/error semantics; idempotency;
      explicit non-goals); consumption mapping note; artifact-board row; task -> review.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The three patch docs under `system_docs/patches/active/structural_snapshot_2026_09_26/`.

## Files / Paths Impacted
- system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md
- system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md
- system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md

## Validation
- Not run (documentation task). Read-order and mapping per `patch_artifact_consumption.md` recorded before task 2.

## Risks / Rollback Notes
- The S3b tree may still be moving (melder_0 in progress): the docs cite the landed shape and name the seam
  melder_0 owns; rollback is deleting the folder.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behaviour claim in a patch doc without a `path:start-end` read behind it.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/structural_snapshot_2026_09_26/ (to be created)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: structural snapshot patch docs.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T15:03:58Z
  TYPE: PLAN
  CLAIM: Authoring order A1-A4 after the rulings. Inputs: summary.md D1-D6 (row sources per phase, hydrate order,
    key tiers, envelope mechanics, invalidation surface, full-hit reads), candidates.md C-G, and a fresh read of
    the S3b cache path (generation 14 `override_site_plan_lanes` is the current envelope generation; the legacy
    codec is deleted and `_emit_spell_cache` stages manifest creations only, per melder_0's M0-28). The docs
    must name the rows a hydrate replays through `SpellSystemStates` helpers (never raw dict writes), the
    blueprint/index rebuild from rows including the path registry's sequential assignment (D6), and the
    refusal predicate.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/summary.md:46-61
  - artifacts/ir_phase_survey_20260925/summary.md:95-101
  - src/melder/utilities/caching_system/caching_system.py:151-167
  IMPACT: No src edit in this task; the patch gate is satisfied when the three docs exist and are linked.
  NEXT: Wait for rulings (a)-(d); then A1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T15:44:18Z
  TYPE: FACT
  CLAIM: Mailbox M2-3 (melder_2, 15:16:27Z) consumed: a new agent melder_2 (claude, synaptic_python_developer)
    is checked in on stand-by with no lane, no board rows and no production files; the owner assigns its work.
    File ownership for this lane is unchanged (melder_0 holds the cache path / creation system in S3; melder_2
    holds nothing). Owner go for this task received ("go ahead and begin do the right thing").
  EVIDENCE:
  - mailbox_board.md:93-93
  IMPACT: No collision; a stand-by peer exists if the owner wants parallel work on the snapshot tasks later.
  NEXT: A1 - read the S3b cache path (caching_system.py, creation-system cache branch, _emit_spell_cache).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE 2026-09-26T15:03:58Z: READY. Waiting on the owner's rulings (a)-(d); then A1 (re-read the S3b cache path) and
the three patch docs.
STATE 2026-09-26T15:37:00Z: IN_PROGRESS. Shape settled (1-4 per spell; no refusal; normal regeneration). Next: A1 re-read of the S3b
cache path and the phase-4 strategy reads, then A2-A4.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
