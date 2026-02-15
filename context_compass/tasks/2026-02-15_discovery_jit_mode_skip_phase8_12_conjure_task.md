# Task: Discovery - JIT Mode Should Skip Conjure Phases 8-12

## Metadata
- Task ID: TASK-2026-02-15-discovery-jit-skip-conjure-phases-8-12
- Story: none
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Run focused discovery to verify and document why JIT mode currently executes conjure phase work that should be deferred, and identify the exact change points needed so conjure skips phases 8-12 when JIT is enabled.

## Scope Boundaries
- In scope:
  - Conjure orchestration path in `SpellbookCreationSystem`.
  - Conduit resolution phase registration (5-11) and Phase 12 compile trigger.
  - `full_ahead_of_time_compilation` propagation points that influence deferred runtime resolution.
- Out of scope:
  - Implementing behavior changes.
  - Benchmark/test rewrites beyond discovery evidence.
  - Non-conjure runtime policy redesign.

## Steps / Checklist
- [ ] Trace conjure pipeline and confirm whether phases 8-11 run unconditionally in JIT mode.
- [ ] Confirm where Phase 12 compile is triggered during conjure.
- [ ] Map where `full_ahead_of_time_compilation` currently affects runtime gate flags.
- [ ] Propose concrete insertion points/guard strategy for skipping 8-12 during conjure in JIT mode.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed discovery notes describing current behavior and gap.
- Candidate implementation plan (file/symbol-level) to enforce JIT conjure skip for phases 8-12.

## Files / Paths Impacted
- `context_compass/tasks/2026-02-15_discovery_jit_mode_skip_phase8_12_conjure_task.md`
- `context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py -k jit`

## Risks / Rollback Notes
- Skipping plan/compile phases during conjure can shift work to first meld and may affect first-call latency/error timing.
- Discovery must separate intended JIT semantics from current implementation semantics before any code change.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Conjure currently runs conduit resolution phases via `run_resolution_phases_for_conduit`, and the registered conduit phase set includes `occurrence_plan`, `injection_plan`, `patch_maps`, and `execution_plan` (8-11) without a JIT-mode guard.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:249-254, src/melder/spellbook/spellbook_creation_system.py:1008-1030
  IMPACT: JIT mode does not currently prevent phase 8-11 work during conjure.
  NEXT: Confirm whether Phase 12 compile is also triggered from this conjure path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Phase 11 execution-plan build triggers `_compile_phase12_no_overrides_executor_from_plan(...)`, so Phase 12 compile can be reached from the conjure resolution pipeline.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:4341-4456
  IMPACT: Conjure can perform compile work that should be deferred if JIT mode intends runtime-first resolution.
  NEXT: Map where `full_ahead_of_time_compilation` is consumed to determine current policy boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: `full_ahead_of_time_compilation` currently propagates primarily to spell runtime flags (`resolution_required`, `resolution_complete`) and meld-time deferred resolution behavior.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:475-511, src/melder/aether/conduit/meld/meld.py:339-340, src/melder/aether/conduit/meld/meld.py:463-510
  IMPACT: The AOT/JIT flag is currently wired to runtime gate behavior more than conjure-phase scheduling.
  NEXT: Produce a discovery plan for where to add JIT gating in conjure phase registration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Discovery task created to analyze and document the JIT-mode conjure gap (phases 8-12 not skipped). Initial evidence shows conjure still schedules phase 8-11 and reaches Phase 12 compile; next step is to produce a concrete guard-insertion plan before implementation.
