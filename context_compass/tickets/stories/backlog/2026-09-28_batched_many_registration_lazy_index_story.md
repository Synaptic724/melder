# Story: Batched many registration with a lazy per-key index - one scope list when the profile shows no targeted purge

## Metadata
- Story ID: STORY-2026-09-28-batched-many-registration-lazy-index
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-28T00:57:27Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a `many` creation in a scope whose profile shows no targeted purge to register by
appending `(spell id, object)` to one scope-level list with no per-key bucket, with the first purge building
the per-key index once and switching the scope back, so that the registration costs one list append and
cleanup still disposes everything newest-first.

## Value / MRP Alignment
The step beyond the registration trim (S5): after S1 the remaining cost is the per-key bucket lookup and
first-use branch (103-120 ns); one append into one list measured 39 ns. The purge verb is the only reader that
needs per-key structure, and it can pay once to build it - so the warm path carries no guard at all.

## Ticket Contract
- ENTRY_GATE: owner's word to reopen; the registration trim shipped; patch docs (component: Creations and
  SpellSpace; code description: lazy index and cleanup order) before src.
- EXECUTION_BOUNDARY: `creations.py` (scope list, lazy index build in purge, cleanup/clear_all order), the
  emitted registration line, tests.
- DEPENDENCIES: STORY-2026-09-27-many-registration-trim; the profile's purge count (harvester story) or a
  configuration switch.
- EXIT_GATE: cleanup and clear_all dispose the same objects in the same order; a purge on a batched scope
  builds the index once and behaves as today; measured saving on the VM; owner-run gauntlet.
- FAILURE_ESCALATION: BLOCKER if newest-first order across spells cannot be reconstructed from one list (it
  can: the list is already in registration order).

## Requirements (Functional)
- Batched mode per scope: one list of (sid, object) in registration order; disposal methods per key from the
  rows.
- Purge on a batched scope: build the per-key index once (O(n)), retire the target, switch the scope to
  keyed mode.
- Cleanup/clear_all: walk the one list newest-first; per-key methods looked up; same ExceptionGroup
  contract.

## Requirements (Non-Functional)
- No guard on the warm path; the purge verb is the switch point.
- Default off unless the profile (or a switch) says so; PGO off identical to S1.

## Scope Boundaries
- In scope: the batched store mode, the lazy index, the emitted line, tests, docs.
- Out of scope: S1 itself; disposal semantics.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's direction (2026-09-28T00:57:27Z); parked with the epic.

## Dependencies / Related Work
- artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
- src/melder/aether/conduit/creations/creations.py:186-244
- STORY-2026-09-27-many-registration-trim

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note.
- [ ] Task: TASK design the batched mode and the lazy index; the purge switch; patch docs.
- [ ] Task: TASK implement behind the profile precondition; differential tests on cleanup order and purge; VM
      measurement.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A batched scope registers in ~one append; cleanup order and errors match keyed mode; the first purge
  behaves as today after building the index.

## Validation / Test Plan
- Unit tests on both modes; component tests on cleanup/purge; the differential matrix; VM run; owner-run
  gauntlet.

## UX / API / Data Notes
- No public API change.

## Risks / Mitigations
- A purge storm after batching -> the index is built once and the scope stays keyed.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Is the precondition the profile's purge count, a configuration switch, or both?

## Decision Log
- 2026-09-28T00:57:27Z (owner): trim specific things like disposal registration for specific objects, safely
  - the rows already carry the disposal data.

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
  - batched registration; lazy per-key index; purge switch
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-28T00:57:27Z
  TYPE: MEASURE
  CLAIM: Registration prices (VM): today 305-384 with disposal; trimmed A 103-120; trimmed B 62-63; one
    `list.append` 39 - the batched shape targets the last gap.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
  - src/melder/aether/conduit/creations/creations.py:597-711
  IMPACT: -40..-60 ns beyond the trim on every disposal-bearing many creation in scopes that never purge.
  NEXT: parked with the epic; reopen on the owner's word.
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
STATE 2026-09-28T00:57:27Z: DRAFT, PARKED. Collected from the owner's direction and shelved with the epic; not routed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
