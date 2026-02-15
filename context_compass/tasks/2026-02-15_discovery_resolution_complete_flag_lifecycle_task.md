# Task: Discovery - Resolution Complete Flag Lifecycle and Defaults

## Metadata
- Task ID: TASK-2026-02-15-discovery-resolution-complete-flag-lifecycle
- Story: none
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Investigate and document whether `Spell.resolution_complete` default initialization and lifecycle transitions are semantically correct, with specific focus on the claim that completion should only be true after phase-12 compile work is complete.

## Scope Boundaries
- In scope:
  - `Spell` constructor defaults for `resolution_required` and `resolution_complete`.
  - Conjure ownership stamping logic that sets runtime resolution flags.
  - Meld deferred-resolution readiness path that mutates these flags.
- Out of scope:
  - Implementing behavior changes.
  - Broad phase-pipeline redesign.
  - Benchmark changes.

## Steps / Checklist
- [ ] Trace every assignment/read of `resolution_required` and `resolution_complete`.
- [ ] Validate whether `resolution_complete=True` at `Spell` init can leak incorrect state before/after conjure.
- [ ] Define intended lifecycle contract for both AOT and JIT modes.
- [ ] Propose exact change points if defaults/transitions are inconsistent with intended contract.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed lifecycle map for `resolution_required` / `resolution_complete`.
- Concrete recommendation on whether constructor defaults should change.

## Files / Paths Impacted
- `context_compass/tasks/2026-02-15_discovery_resolution_complete_flag_lifecycle_task.md`
- `context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py -k \"resolution_required or resolution_complete or jit\"`

## Risks / Rollback Notes
- Changing default flags can alter first-meld behavior and error timing in both JIT and AOT paths.
- Discovery must separate "pre-conduit placeholder defaults" from "runtime-ready state."

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
  CLAIM: `Spell` currently initializes `resolution_required=False` and `resolution_complete=True` in the constructor.
  EVIDENCE: src/melder/spellbook/spell.py:322-324
  IMPACT: New spells start in a completed state before conduit ownership stamping mutates flags.
  NEXT: Confirm where and when conjure/bind paths overwrite these flags.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Conjure ownership stamping sets flags from `full_ahead_of_time_compilation` (`required=not AOT`, `complete=AOT`).
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:497-511
  IMPACT: Runtime flag semantics are mode-driven at conduit stamp time, not solely from Spell constructor defaults.
  NEXT: Validate whether conjure phase scheduling itself aligns with these flags under JIT.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Meld deferred-resolution readiness mutates flags (`complete=True/required=False` on success; inverse on failure) when runtime resolution is required.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:463-510
  IMPACT: Post-conjure runtime transitions can override initial/default values; lifecycle correctness depends on entering meld with truthful starting state.
  NEXT: Define desired pre-meld truth contract for constructor and conduit-stamp defaults.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Ticket created to isolate discovery on `resolution_complete` default and lifecycle semantics, including whether constructor defaults should be conservative until phase readiness is actually achieved.
