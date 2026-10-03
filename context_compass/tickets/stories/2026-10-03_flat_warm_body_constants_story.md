# Story: Flat warm body - site and store constants (S9) and key identity (S11) on every shared site

## Metadata
- Story ID: STORY-2026-10-03-flat-warm-body-constants
- Epic: EPIC-2026-10-01-static-codegen-and-door-strategies
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-03T21:31:58Z
- Updated: 2026-10-03T21:31:58Z

## User Narrative
As the Melder owner, I want every shared site of a site plan (a unique or per-conduit provider read by a
consumer's plan) to stop paying a tuple index and an attribute read per creation for things that are fixed when
the plan is hydrated - the site's Spell object and, in an automatic world, its owner store - and to look its
instance up by a key object that is identical to the store's key, so that the warm path of every root over
shared providers gets cheaper without a store change, a guard or a posture-dependent branch in the body.

## Value / MRP Alignment
Owner (2026-10-03): existing objects are rare, so S2a alone helps little; take the parts that help "everything in
general". S9 and S11 apply to every shared site of every dict-mode and direct-mode plan: S9 removes
`spells[i]` and `._owner_creations` from the body (HYPOTHESIS -8..-12 ns per shared site, from the epic's
catalogue), S11 makes the store lookup hit the dict's identity fast path for cache-restored plans (MEASURED micro
-1.5..-2 ns per lookup). Both are certified in the harness before any src edit (owner: "test it first").

## Ticket Contract
- ENTRY_GATE: the owner's word (2026-10-03: "go ahead and implement the next steps ... just make sure you test
  it first"); the harness certifies S9 and S11 on the five shapes BEFORE the patch docs; patch docs (component:
  SpellCompiler codegen, site-plan lowering and the hydrators) written and linked before any src edit.
- EXECUTION_BOUNDARY: `tests/experimentation/codegen_strategy_certification.py` (S9/S11 transforms),
  `site_plan_lowering.py` (shared-site emission and the plan namespace), the hydrators that bind the plan
  namespace (generalized, many_only; the cache-restored path), `caching_system.py` (generation), tests, docs.
- DEPENDENCIES: S8 landed (0.2.8217); the certification table; the posture read at hydration (transfer repoints
  the owner store in dynamic posture only).
- EXIT_GATE: the harness table with S9/S11 columns; differential tests (same objects, same errors; a dynamic
  transfer test proving the store read survives in dynamic posture); suites green; harness re-run; owner-run
  gauntlet.
- FAILURE_ESCALATION: DECISION_REQUEST if the harness shows S9 within noise on every shape (then S11 alone, or
  nothing, ships); BLOCKER if a hydrator cannot bind the live key objects without a manifest format change.

## Requirements (Functional)
- A shared site reads `cI._creations.get(sidI)` with `cI` bound at hydration in automatic posture (the owner
  store cannot move) and `sI._owner_creations` read per creation in dynamic posture (transfer repoints it).
- `sidI` is the live Spell's `spell_id` object in every plan namespace, including cache-restored plans.
- Every other line of every plan is unchanged; the same objects and errors as today.

## Requirements (Non-Functional)
- Measured on the VM first; a strategy ships only when the harness shows a win above noise on the shapes it
  applies to; generation bump retires the old executors.

## Scope Boundaries
- In scope: S9 and S11 in the normal plan and the key-set plans; the harness transforms; tests; docs.
- Out of scope: S2a existing-object constants (parked by the owner's remark - rare; its own backlog story);
  S10 subscript hits (low value); S12 direct emission of generic steps; the doors (next story).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's word (2026-10-03T21:31:58Z); the certification task is routed on the board.

## Dependencies / Related Work
- tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md (Non-PGO Strategy Catalogue: S9, S11)
- tickets/stories/backlog/2026-10-01_existing_object_constants_story.md (S2a, parked)
- artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-10-03-certify-and-implement-site-store-constants - harness S9/S11 columns, then the
      emitter and hydrator edits with tests. tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Harness table recorded before the edit; same objects on every shape after it; the dynamic transfer test green;
  measured plan delta recorded; owner-run numbers recorded.

## Validation / Test Plan
- Harness (before and after); unit tests on the emitter output per posture; component tests through real
  conjures in both postures including a transfer in dynamic posture and a cache full hit; the suites sharded.

## UX / API / Data Notes
- No public API change; cache generation bump when the emitted body changes.

## Risks / Mitigations
- A dynamic transfer repoints the owner store after hydration -> the constant is automatic-only; the dynamic
  body keeps the read; a test proves it.
- The harness measures a transform of the captured body, not the shipped emitter -> the shipped body is
  re-measured by the same harness after landing.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.
- [ ] No src edit before the harness verdict, the patch docs and the mapping note.

## Open Questions
- Does any automatic-world path repoint a spell's owner store after conjure (upgrade? cluster?) - to verify in
  source before the constant is emitted.

## Decision Log
- 2026-10-03T21:31:58Z (owner): existing objects are rare; implement what helps in general, test first, ignore the PGO
  epic. fable_0: S9 + S11 as this story, S2a parked, the door lane next.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/flat_warm_body_20261003/ (harness runs, apply scripts, logs)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - shared-site emission; plan namespace; hydration constants; key identity
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-10-03T21:31:58Z
  TYPE: PLAN
  CLAIM: Opened on the owner's word. Order: read the shared-site emission and the plan namespace (lowering),
    then the hydrators' namespace binding (live and cache-restored); add S9/S11 transforms to the harness and
    measure; patch docs; implement; tests; land. S2a parked in the backlog with the owner's remark.
  EVIDENCE:
  - tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md:190-215
  - tests/experimentation/codegen_strategy_certification.py:183-245
  IMPACT: One emitter pass over every shared site; the doors follow.
  NEXT: the task's investigation read.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
STATE 2026-10-03T21:31:58Z: IN_PROGRESS. The certification/implementation task is the active lane. Resume from its
latest STATE line.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
