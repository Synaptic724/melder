# Task: Discovery - JIT Mode Should Skip Conjure Phases 8-12



Completed: 2026-02-15
Summary: Closed after user acceptance; implementation and validation artifacts are recorded in this ticket.


## Metadata
- Task ID: TASK-2026-02-15-discovery-jit-skip-conjure-phases-8-12
- Story: none
- Status: done
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
- [x] Trace conjure pipeline and confirm whether phases 8-11 run unconditionally in JIT mode.
- [x] Confirm where Phase 12 compile is triggered during conjure.
- [x] Map where `full_ahead_of_time_compilation` currently affects runtime gate flags.
- [x] Propose concrete insertion points/guard strategy for skipping 8-12 during conjure in JIT mode.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed discovery notes describing current behavior and gap.
- Candidate implementation plan (file/symbol-level) to enforce JIT conjure skip for phases 8-12.

## Files / Paths Impacted
- `context_compass/tasks/2026-02-15_discovery_jit_mode_skip_phase8_12_conjure_task.md`
- `context_compass/attention_board.md`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py`
    - Result: `3 passed` (warnings: Python/GIL runtime warning from `src/melder/__init__.py`, pytest cache permission warning).
- Recommended follow-up:
  - `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py -k jit`

## Risks / Rollback Notes
- Skipping plan/compile phases during conjure can shift work to first meld and may affect first-call latency/error timing.
- Discovery must separate intended JIT semantics from current implementation semantics before any code change.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
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

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Conjure uses a single 5-11 scheduler path that only skips 8-11 for foundational resolution errors, while dedicated foundational-only (5-7) and deferred target-local plan (8-11) paths already exist and can be composed for JIT behavior.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:230-255, src/melder/spellbook/spellbook_creation_system.py:742-786, src/melder/spellbook/spellbook_creation_system.py:998-1031, src/melder/spellbook/spellbook_creation_system.py:1241-1340, src/melder/spellbook/spellbook_creation_system.py:879-947, src/melder/aether/conduit/meld/meld.py:463-510
  IMPACT: A low-risk JIT fix can likely be implemented at conjure orchestration level by choosing foundational-only 5-7 during conjure when AOT is disabled, while preserving existing first-meld deferred 8-11 behavior.
  NEXT: Validate exact symbol-level change set and draft implementation patch plan (including docstring contract updates) before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Implement JIT conjure skip by branching in `run_resolution_phases_for_conduit`: always run foundational phases (5-7), then run plan phases (8-11) only when configuration indicates full AOT compilation and foundational phases reported no resolution errors.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:742-786, src/melder/spellbook/spellbook_creation_system.py:1241-1340, src/melder/spellbook/spellbook_creation_system.py:475-511, src/melder/spellbook/spellbook_creation_system.py:879-947
  IMPACT: JIT mode will defer 8-11/phase12 compile work to runtime target-local deferred resolution, while AOT mode retains current eager behavior.
  NEXT: Request approval for code edits in `src/melder/spellbook/spellbook_creation_system.py` and targeted tests; then implement with docstring updates and validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The JIT conjure skip plan is now present in runtime code: conduit resolution reads `full_ahead_of_time_compilation`, forces plan-phase skip when disabled, and removes plan-phase outputs; targeted fastpath tests assert plan factories remain at zero in JIT mode and pass.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:773-820, src/melder/spellbook/spellbook_creation_system.py:996-1053, tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:406-483
  IMPACT: This discovery ticket's identified behavior gap is now closed at source + unit-test level.
  NEXT: Review with user for acceptance, then either close this discovery ticket or route to the next AOT/JIT active task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Current runtime contract treats `resolution_required=True` as "deferred runtime phases still needed" and `resolution_complete=True` as "deferred runtime phases complete"; meld success flips to `(required=False, complete=True)` and failure preserves `(required=True, complete=False)`.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:463-510, tests/unit/melder/aether/conduit/meld/test_meld.py:1720-1773, tests/unit/melder/aether/conduit/meld/test_meld.py:1776-1806
  IMPACT: Inverting this polarity (for example setting `resolution_required=True` on completion) would conflict with the active meld gate and regress deferred-resolution semantics.
  NEXT: Align user-facing design discussion on preserving current flag polarity while deciding whether any additional invalidation hooks should set `(required=True, complete=False)` when plan artifacts are invalidated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Discovery ticket confirmed and documented the original gap, then validated that current source now applies the guard strategy in `run_resolution_phases_for_conduit` and that targeted JIT fastpath tests pass (`3 passed`). Ticket is ready for user acceptance and routing to the next AOT/JIT lane.


