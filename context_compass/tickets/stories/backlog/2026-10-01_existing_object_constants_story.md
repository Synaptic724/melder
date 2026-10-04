# Story: Existing-object constants - existing-object sites bound at hydration, not read per creation (S2a)

## Metadata
- Story ID: STORY-2026-10-01-existing-object-constants
- Epic: EPIC-2026-10-01-static-codegen-and-door-strategies
- Status: ready (parked)
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-01T00:55:51Z
- Updated: 2026-10-03T21:31:58Z

## User Narrative
As the Melder owner, I want a plan step that injects an existing object (a spell with
`spell_is_existing_creation`) to receive that object as a namespace constant bound when the plan is hydrated,
instead of reading its owner store and checking for None on every creation, so that consumers of configured
instances pay nothing for them.

## Value / MRP Alignment
Measured by the certification harness at -11..-17% of the plan on roots with existing-object sites (commandops'
ContextRoot has four). In an automatic world the object cannot change (bind after conjure is refused), so the
constant needs no guard; in a dynamic world a notch can replace the selected spell, so the site keeps an
epoch-guarded read (the S2b shape, -8 ns, measured). The rows already say which sites qualify.

## Ticket Contract
- ENTRY_GATE: S8 landed or parked; patch docs (component: SpellCompiler codegen, site-plan lowering and the
  generalized hydrator) written and linked before any src edit.
- EXECUTION_BOUNDARY: `site_plan_lowering.py` (shared-site emission for existing-object steps), the generalized
  hydrator (namespace constants), the posture read that selects constant vs guarded, `caching_system.py`
  generation bump, tests.
- DEPENDENCIES: the certification table; S8's landing (same emitter).
- EXIT_GATE: differential test (plain vs constant on the same roots; a dynamic notch test proving the guarded
  shape follows the new object), suites green, harness re-run, owner-run gauntlet.
- FAILURE_ESCALATION: DECISION_REQUEST if any path in an automatic world can replace an existing object's
  registration after hydration (to verify in source first).

## Requirements (Functional)
- Automatic posture: an existing-object site is a constant in the plan namespace; no store read, no None check.
- Dynamic posture: the site compares the spell's door epoch and falls back to the store read on mismatch.
- Every other site is unchanged.

## Requirements (Non-Functional)
- >= 10% off the plan of a root with existing-object sites on the VM; generation bump retires the old
  executors.

## Scope Boundaries
- In scope: existing-object sites in the normal plan and the key-set plans; the hydrator seam; tests; docs.
- Out of scope: constructed singleton captures (S2b, PGO epic); the doors.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Drafted from the certification table and the owner's split (2026-10-01T00:55:51Z); opens after S8.

## Dependencies / Related Work
- tickets/epics/backlog/2026-09-27_adaptive_creation_contexts_epic.md (Concrete Strategies: S2a, S2b)
- artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md
- tickets/stories/backlog/2026-09-27_probe_selected_codegen_styles_story.md (S2b, the guarded shape)

## Tasks (Implementation Checklist)
- [ ] Task: verify in source that no automatic-world path replaces an existing object's registration after
      hydration (bind refusal, transfer, notch gating); write the patch docs.
- [ ] Task: implement the constant/guarded emission and the hydrator binding; differential and notch tests;
      generation bump; harness re-run.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Same objects as the plain body on every shape; a dynamic notch of an existing-object spell is followed by
  the guarded shape; measured plan delta and owner-run numbers recorded.

## Validation / Test Plan
- Unit tests on the emitter output per posture; component tests through real conjures in both postures; the
  harness re-run; owner-run gauntlet.

## UX / API / Data Notes
- No public API change; cache generation bump.

## Risks / Mitigations
- An existing object retired by purge in an automatic world -> verify whether purge can target an existing
  object's registration; if it can, the constant shape is refused for that spell and the guarded shape used.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Can `purge` retire an existing-object registration in an automatic world? If so the site keeps the guard.

## Decision Log
- 2026-10-01T00:55:51Z (owner): non-PGO strategies first, as their own epic. fable_0: S2a is third, after S8.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (the certification table; the re-run after landing)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - existing-object sites; hydration constants; posture-dependent guards
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-10-01T00:55:51Z
  TYPE: MEASURE
  CLAIM: S2a alone: -11..-17% of the plan on roots with existing-object sites; S2b (the guarded unique capture)
    -1..-18%, worth it combined; the guarded shape is the dynamic-posture fallback for S2a.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md:1-60
  - tickets/tasks/2026-09-30_build_codegen_strategy_certification_harness_task.md:150-222
  IMPACT: Sets the acceptance bar (>= 10% on roots with existing-object sites).
  NEXT: opens after S8 lands.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-03T21:31:58Z
  TYPE: DECISION
  CLAIM: Parked by the owner's remark (2026-10-03: existing objects are very rare); the general parts of the
    emitter pass (S9, S11) ship through tickets/stories/2026-10-03_flat_warm_body_constants_story.md. Reopen
    on explicit request; the open question (purge of an existing-object registration) stays open.
  EVIDENCE:
  - tickets/stories/2026-10-03_flat_warm_body_constants_story.md:1-40
  IMPACT: No lane; not routed.
  NEXT: none unless reopened.
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
STATE 2026-10-01T00:55:51Z: READY. Drafted under the static epic; opens after S8 lands. Not routed.

STATE 2026-10-03T21:31:58Z: READY (parked). Existing objects are rare (owner); S9/S11 ship separately. Not routed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
