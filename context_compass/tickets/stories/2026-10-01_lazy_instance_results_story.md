# Story: Lazy instance_results - a dict-mode root builds its dict only inside a miss (S8)

## Metadata
- Story ID: STORY-2026-10-01-lazy-instance-results
- Epic: EPIC-2026-10-01-static-codegen-and-door-strategies
- Status: ready
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-01T00:55:51Z
- Updated: 2026-10-01T00:55:51Z

## User Narrative
As the Melder owner, I want a root whose plan runs in dict mode (any generic step - an existing object, a
contract payload, a positional override, a collection parameter) to stop building `instance_results = {}` and
storing every step into it on every warm creation, so that the plan pays for the dict only on the miss that
reads it.

## Value / MRP Alignment
Measured by the certification harness at -18..-24% of the plan on ContextRoot and wide8 over existing objects,
with no store change and no guard: the warm path never reads the dict (only a miss's
`_construct_spell_instance` does), so building it inside the misses is a pure emitter change that returns the
same objects. It is the cheapest certified lever after S1.

## Ticket Contract
- ENTRY_GATE: S1 landed or parked; patch docs (component: SpellCompiler codegen, site-plan lowering; code
  description: the miss path's dict construction) written and linked before any src edit.
- EXECUTION_BOUNDARY: `site_plan_lowering.py` (`_emit_context`, `_emit_miss`, the generic step emission that
  stores into `instance_results`), the generalized hydrator where the miss closure receives the dict,
  `caching_system.py` generation bump, tests.
- DEPENDENCIES: the certification table; S1's landing (the registration line in the same emitter).
- EXIT_GATE: differential test (plain vs lazy on the same dict-mode roots: same objects, same errors on a
  failing miss), suites green, the harness re-run showing the plan delta, owner-run gauntlet.
- FAILURE_ESCALATION: DECISION_REQUEST if a miss needs a value the warm path no longer holds in a local.

## Requirements (Functional)
- A dict-mode plan allocates no `instance_results` on the path where every shared site hits.
- A miss builds the dict from the locals the plan already holds (the sites read before it) and hands it to
  `_construct_spell_instance` exactly as today.
- Direct-mode plans are byte-identical.

## Requirements (Non-Functional)
- >= 15% off the plan of a dict-mode root on the VM; generation bump retires the old executors.

## Scope Boundaries
- In scope: the emitter's context/miss emission for dict mode, the hydrator seam, tests, docs, generation bump.
- Out of scope: making generic steps direct (a different lever); the store; the doors.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Drafted from the harness finding of 2026-09-30 and the owner's split
  (2026-10-01T00:55:51Z); opens after S1.

## Dependencies / Related Work
- tickets/tasks/2026-09-30_build_codegen_strategy_certification_harness_task.md (the S8 FACT and MEASURE notes)
- artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md
- tickets/stories/2026-09-27_many_registration_trim_story.md (S1; same emitter)

## Tasks (Implementation Checklist)
- [ ] Task: read `_emit_context`, `_emit_miss`, `_is_direct` and the generic step emission whole; write the
      patch docs; map patch sections to edits and tests.
- [ ] Task: implement the lazy dict, differential tests, generation bump; re-run the harness.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Same objects and errors as the plain body on every dict-mode shape of the harness; the measured plan delta
  recorded; owner-run gauntlet numbers recorded.

## Validation / Test Plan
- Unit tests on the emitter output (dict absent on the warm path, present in the miss); component test through
  a real conjure of a root with an existing-object step; the harness re-run; owner-run gauntlet.

## UX / API / Data Notes
- No public API change; cache generation bump.

## Risks / Mitigations
- A miss that references a site not yet read -> the miss closure receives only the sites the plan read before
  it, in plan order, which is the order the rows already fix.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Does any generic step read `instance_results` on the warm path for an override of a stored instance? To
  verify in the emitter before the patch docs.

## Decision Log
- 2026-10-01T00:55:51Z (owner): non-PGO strategies first, as their own epic. fable_0: S8 is second after S1
  (same emitter, no store change).

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
  - dict-mode plans; miss closures; instance_results
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-10-01T00:55:51Z
  TYPE: MEASURE
  CLAIM: S8 alone: -18..-24% of the plan on the two dict-mode shapes (ContextRoot, wide8 over existing objects);
    nothing on direct-mode roots, which build no dict.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md:1-60
  - tickets/tasks/2026-09-30_build_codegen_strategy_certification_harness_task.md:150-222
  IMPACT: Sets the acceptance bar (>= 15% on dict-mode roots).
  NEXT: opens after S1 lands.
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
STATE 2026-10-01T00:55:51Z: READY. Drafted under the static epic; opens after S1 lands. Not routed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
