# Story: Many registration trim - one append per creation, disposal methods recorded once per key

## Metadata
- Story ID: STORY-2026-09-27-many-registration-trim
- Epic: EPIC-2026-10-01-static-codegen-and-door-strategies (moved from EPIC-2026-09-27-adaptive-creation-contexts
  on the owner's split, 2026-10-01)
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-10-01T00:56:50Z

## User Narrative
As the Melder owner, I want a `many` creation with disposal methods to register with one append into one
bucket while the disposal side reads the spell's method list recorded once per key, so that the 400-690 ns a
real application pays per transient creation drops to a fraction without touching what disposal does.

## Value / MRP Alignment
The only lever the commandops proof measured at 10% or more: 25-45% of a disposal-bearing `many` meld. It
changes a registry shape, not a contract: the same objects are disposed in the same order with the same
errors. It ships before any probe because it needs no data to be right.

## Ticket Contract
- ENTRY_GATE: owner's pick; patch docs (component: Creations and SpellSpace; code description: registration
  and cleanup race) written and linked before any src edit.
- EXECUTION_BOUNDARY: `conduit/creations/creations.py` (add_many_creations, _append_many_locked, cleanup,
  clear_all, purge, extract/restore of many buckets), the one emitted line in `site_plan_lowering.py` and
  its hydrator-side constants, `caching_system.py` generation bump, tests.
- DEPENDENCIES: the registration split measurement; melder_0's scope-exit lane holds no file here.
- EXIT_GATE: differential test (same disposal order, same ExceptionGroup shape), suites green, VM
  before/after on the commandops shapes, owner-run gauntlet; cache generation bumped so old executors are
  retired.
- FAILURE_ESCALATION: DECISION_REQUEST on trimmed A (lock kept) vs B (lock-free append) once the cleaned-
  store race is written down; BLOCKER if the refusal contract cannot be kept for B.

## Requirements (Functional)
- Per-key disposal methods recorded once at first use; entries hold the object only.
- One `list.append` per creation on the live bucket; the disposable mirror derived from it, not maintained
  per entry.
- Cleanup, clear_all and purge dispose the same objects in the same (newest-first) order with the same error
  aggregation.
- A build finishing after `cleanup()` is still refused and its object disposed (the 2026-09-25 contract).

## Requirements (Non-Functional)
- Warm meld of a `many` root with disposal: >= 25% faster on the VM; no change for roots without disposal.
- Default path byte-identical for every other existence.
- Overlay rules; rich docstrings on every touched method; `Optional`/`Union`.

## Scope Boundaries
- In scope: the registry shape, the emitted registration line, extract/restore of many buckets, tests, docs,
  generation bump.
- Out of scope: unique/per-conduit registration; disposal semantics; the doors.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's split (2026-10-01T00:56:50Z): non-PGO first, S1 is the largest
  certified lever; the implementation task is routed on the board.

## Dependencies / Related Work
- Proof: artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
- Live shapes: artifacts/pgo_strategies_20260927/vm_commandops_shapes_gil0_20260927.md
- tickets/tasks/backlog/2026-09-27_probe_creation_context_design_task.md (MEASURE notes of 2026-09-27T23:32:15Z)

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK-2026-10-01-implement-many-registration-trim - read the store and the emitter whole, patch docs
      (trimmed A, the cleaned-store race argument), implement, differential + deopt tests, generation bump.
      tickets/tasks/2026-10-01_implement_many_registration_trim_task.md
- [ ] Task: TASK measure on the VM and hand the gauntlet to the owner; decide whether B is worth its race redesign.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Same disposal behaviour under cleanup, clear_all, purge and the refused late publish, proven by tests.
- Worker-shaped meld drops by >= 25% on the VM; owner-run gauntlet shows the delta at threads > 1.

## Validation / Test Plan
- Unit tests on the registry; component tests on the plan's emitted line; the differential matrix; VM runs
  of `commandops_shape_probe.py` before/after; owner-run gauntlet.

## UX / API / Data Notes
- No public API change; `Creations` internals and one emitted call change; cache generation bump.

## Risks / Mitigations
- Lock-free append strands a late publish -> ship A first; B only with a written and tested refusal path.
- Restore/extract of many buckets reads the old tuple shape -> migrate both readers in the same change.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Is the disposable mirror kept at all, or is the live bucket plus the per-key method list the whole record?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Ranked first: measured,
  data-independent, contract-preserving.
- 2026-10-01T00:56:50Z (owner): split into non-PGO and PGO epics, non-PGO first. fable_0: this story moves to
  the static epic and opens now; the certification table (2026-09-30) measured S1 alone at -11..-49% of the
  plan and ALL at -40..-67%, so the >= 25% bar on a disposal-bearing many meld stands.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (proof and runs shared by the epic; new runs land here)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Creations registration; disposal order; cleaned-store refusal
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: MEASURE
  CLAIM: Today 305-384 ns per disposal-bearing many registration, 151-185 without disposal; trimmed A 103-120,
    trimmed B 62-63; in situ the registration is 400-690 ns of a 650-1220 ns meld.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/vm_commandops_shapes_gil0_20260927.md
  - src/melder/aether/conduit/creations/creations.py:597-711
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1313-1329
  IMPACT: Sets the acceptance bar (>= 25% on those melds).
  NEXT: owner picks; then the design task with patch docs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-27T23:42:45Z: DRAFT. Collected from the owner's direction; not routed. Opens when the owner
picks it; its first
task is the measurement plan and the patch docs.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

STATE 2026-10-01T00:56:50Z: IN_PROGRESS. Moved to tickets/stories/ under the static epic; the implementation task is the
active lane. Resume from its latest STATE line.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
