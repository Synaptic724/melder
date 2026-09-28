# Story: Creator and thread context capture - who built it, where, for whom, on which thread

## Metadata
- Story ID: STORY-2026-09-27-creator-thread-context-capture
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want each creation seen by the probe window to record who made it (the conduit or
SpellSpace door, root or lesser), what it was made for (the consumer root spell and its override key set) and
which thread built it, so that the report can explain a conduit's structure and the levers that depend on
thread and consumer stability have their evidence.

## Value / MRP Alignment
Two families of optimization depend on this data and nothing else provides it: thread-affine registration (one
creator thread per scope) and consumer-specialized plans (a transient only ever built as a child of one root;
a root always melded through one door). The capture rides the probe window, so its cost also ends.

## Ticket Contract
- ENTRY_GATE: owner's pick; the probe story's harvest record exists or lands in the same tranche; patch docs
  before src.
- EXECUTION_BOUNDARY: the probe emission (extra fields), the harvest record schema, the meld door identity
  the plan already holds (`meld._conduit_creations` / `_spellspace_creations`, root spell id, key tuple),
  `threading.get_ident()`, tests.
- DEPENDENCIES: STORY-2026-09-27-probe-creation-context-harvest.
- EXIT_GATE: the harvest record carries per-creation creator, consumer and thread fields aggregated per
  window (distinct threads, distinct doors, consumer histogram); cost measured; default off byte-identical.
- FAILURE_ESCALATION: DECISION_REQUEST if per-creation capture costs more than the count-only bound; then
  aggregate at the site instead of per creation.

## Requirements (Functional)
- Per creation in the window: thread ident, door kind and id (conduit root/lesser or SpellSpace), consumer
  root spell id, override key tuple (or none).
- Aggregation at harvest: distinct creator threads, distinct doors, consumer histogram per spell; value-
  only.
- SpellSpace thread ownership read from the existing thread state, not re-derived.

## Requirements (Non-Functional)
- Capture cost inside the count-only bound (+11%) or aggregated per site.
- No identity of user objects stored; ids and counts only.

## Scope Boundaries
- In scope: the fields, their aggregation, the cost measurement, tests, docs.
- Out of scope: acting on the data (the thread-affine and consumer-specialized stories).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- SpellSpace thread state: src/melder/aether/conduit/spell_space/spell_space_thread_state.py:10-95
- STORY-2026-09-27-probe-creation-context-harvest
- STORY-2026-09-27-thread-affine-creation-stores
- STORY-2026-09-27-consumer-specialized-transients

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK design the fields and the aggregation; measure `get_ident()` and the door reads in the harness;
      patch docs.
- [ ] Task: TASK implement in the probe emission and the harvest; tests on a multi-thread, multi-door shape.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A two-thread, two-door shape reports both threads and both doors with the right counts; the consumer
  histogram names the roots that built each transient.

## Validation / Test Plan
- Unit tests on aggregation; component tests on a lesser + SpellSpace + threads shape; VM cost run.

## UX / API / Data Notes
- Fields in the value-only profile record; surfaced by the report story.

## Risks / Mitigations
- Thread idents are reused after a thread exits -> record distinct counts per window, not a thread registry.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Does the owner want the consumer histogram per transient spell, per (transient, consumer) pair, or both?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Collected from the owner's
  direction (thread context, who made it, what for).

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
  - creator context; thread ident; consumer root; override key set
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: HYPOTHESIS
  CLAIM: The door identity (conduit id or space id), the consumer root spell id and the key tuple are already
    in the plan's namespace at emission; only the thread ident is a new read per creation. Cost UNKNOWN
    until measured.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:119-165
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:10-95
  IMPACT: If the reads are cheap the capture rides the count-only window unchanged.
  NEXT: owner picks; measure the reads in the harness first.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T00:37:47Z
  TYPE: FACT
  CLAIM: What the probe can see, from source. Per shared site the body reads `c_i._creations.get(sid)` and calls
    `_miss_i` when it is None, so a count-only probe records exactly "existed" vs "had to be built" per site and
    how often, and the miss order is the build order of providers this root built itself (the emission order is
    static, providers-first). Scope IS visible: the executor receives `meld`, and the stores it reads carry
    `_owner_conduit_id` and `_id` (`Creations.__init__`), the meld carries `_resolution_conduit_id` and the
    spellspace store when one is active - so the conduit, lesser or SpellSpace that made the object is readable
    without a new reference on the context.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1336-1396
  - src/melder/aether/conduit/creations/creations.py:128-170
  - src/melder/aether/conduit/meld/meld.py:182-202
  - src/melder/aether/conduit/meld/meld.py:278-280
  - tests/experimentation/probe_creation_context_prototype.py:1-136
  IMPACT: The owner's "we can at least tell what existed and what didn't, how often, and the order" is the
    count-only probe as prototyped; the scope fields cost one attribute read each.
  NEXT: owner picks; the investigation task measures the scope reads in the harness.
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
STATE 2026-09-27T23:42:45Z: DRAFT. Collected from the owner's direction; not routed. Opens when the owner
picks it; its first
task is the measurement plan and the patch docs.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
