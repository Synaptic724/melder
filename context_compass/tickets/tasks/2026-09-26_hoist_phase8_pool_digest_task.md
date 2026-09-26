# Task: Hoist the phase-8 pool digest into the pass cache and test the analysis slot first

## Metadata
- Task ID: TASK-2026-09-26-hoist-phase8-pool-digest
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: ready
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T09:05:00Z

## Objective
In `SpellOccurrenceGraphAnalyzerStrategy.analyze`: test `artifact._occurrence_graph_analysis is None`
before any key work; hash the pass-invariant rows (spell rows, topology rows, contracted rows, system
state) once per pass into `analysis_pass_cache["phase8_pool_digest"]`; build the root rows once and
combine them with the digest for both the fast key and the input signature, so per-root work is
proportional to the root's own blueprint (C-A).

## Ticket Contract
- ENTRY_GATE: Task 2 in review (single serializer) or the owner confirms C-A may land first; patch docs
  linked; the owner confirmed the Propose -> Confirm message; active board row routes here.
- EXECUTION_BOUNDARY: `spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
  (`analyze`, `_build_occurrence_graph_fast_key`, `_build_occurrence_graph_input_signature`, one new
  helper `_get_pool_digest`) and its tests. No other file.
- DEPENDENCIES: task 1 patch docs; the pass-cache lifetime contract (dies with the pass units); the
  key semantics: `id(path_registry)` stays a per-root process-local part.
- EXIT_GATE: the pool-wide rows are hashed once per pass; root rows built once per root; the None
  check precedes key work; unit tests for digest reuse, None-first skip and key equality across roots;
  breakdown harness before/after recorded (owner-run); status review.
- FAILURE_ESCALATION: CONFLICT if updater_1 or melder_0 edit the strategy file concurrently; RISK if
  the JIT path shows a memo hit that the new key shape would miss (none expected: hash of hash).

## Scope Boundaries
- In scope: the key/signature path of the strategy and its tests.
- Out of scope: the occurrence graph build, contract-defaults reading (C-K), phases 9-11, emitters.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Created with the story; opens after task 2 (or on owner direction) and the
  confirmed proposal.

## Steps / Checklist
- [ ] H1: Propose -> Confirm (file, symbols, the digest cache key, the None-first rule) and owner
      confirmation.
- [ ] H2: implement `_get_pool_digest` (pass-cache memo, benign last-writer-wins like the two existing
      slots), single `_build_root_blueprint_rows` call, key = (root rows..., pool digest), signature =
      hash(root rows..., pool digest); None-first skip of the compare.
- [ ] H3: tests - digest built once per pass over N roots; analysis None -> no compare, keys still
      stored; identical key/signature for the same root across two passes with equal inputs; different
      digest when a topology row changes.
- [ ] H4: docstring ritual; notes; task -> review with "Not run." and the harness command.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The strategy change; tests; before/after breakdown harness rows (owner-run) recorded here.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py
- tests (unit tests for the strategy's key path)

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/spellbook/spell_crafter`
  - `BENCH_BREAKDOWN_WORKERS=1 python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`

## Risks / Rollback Notes
- Rollback: restore the two key builders (pure functions) and drop the helper.
- Phase 8 is inside updater_1's review-stage proposals: the change is confined to ~40 lines of the key
  path and rebases trivially; NOTICE sent at story open.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No edit under `src/` before the owner confirms the file/symbol proposal.

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
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/
  - artifacts/codegen_signature_determinism_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: phase-8 key path; pass cache; pool digest.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T09:05:00Z
  TYPE: PLAN
  CLAIM: The digest is a hash of the same rows the key carried, so the signature remains a function of
    the same inputs; the None-first check only removes a compare that cannot succeed on the conjure
    path. Root rows are built once and shared by key and signature.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:118-372
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:182-216
  IMPACT: Removes the cold path's O(spells^2) step without changing what invalidates the analysis.
  NEXT: Wait for the confirmed proposal (H1).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T09:05:00Z: ready; opens after task 2 is in review (or on owner direction) and H1 is confirmed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
