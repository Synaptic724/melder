# Story: Creation profile report - the DevOps station view of what a conduit built, for whom, and which version runs

## Metadata
- Story ID: STORY-2026-09-27-creation-profile-report
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a report in the DevOps station that shows, per spell and per conduit, the node
structure the runtime actually built (sites, kinds, hit rates, ns), who built it (threads, doors, consumers)
and which version of its creation context is live with its measured delta, with a describe verb and a reset,
so that optimization is something I can read, not something that happens to me.

## Value / MRP Alignment
The user-visible half of the epic. The DevOps station already holds fact baselines and builds derived views
through information strategies; the report is one more strategy over the harvested profiles, so it costs
nothing on the warm path and reuses an existing surface.

## Ticket Contract
- ENTRY_GATE: owner's pick; the probe story's harvest record schema fixed; patch docs (component: DevOps
  Control Plane, DevOps Information Strategies) before src.
- EXECUTION_BOUNDARY: `devops_information_registry.py` (a profile fact family), a
  `DevopsInformationStrategyBuilder` strategy, a describe verb on Conduit/Spellbook or the station, a reset
  verb, tests.
- DEPENDENCIES: STORY-2026-09-27-probe-creation-context-harvest; the capture story for the creator fields.
- EXIT_GATE: report readable from the station and the describe verb; reset clears profiles and re-arms the
  probe; value-only output; tests green.
- FAILURE_ESCALATION: DECISION_REQUEST on where the describe verb lives (conduit, spellbook, station).

## Requirements (Functional)
- A profile fact family reported by the harvest (`report_fact`), listed and read through the existing
  registry verbs.
- One information strategy that renders per spell: sites and kinds, hit rates, ns per site and per creation,
  creator threads/doors, consumer histogram, live version key and measured delta.
- A describe verb returning the rendered report; a reset verb clearing profiles and re-arming the window.

## Requirements (Non-Functional)
- Zero cost on the warm path; rendering is on demand.
- Output is plain values (dicts, lists, strings, numbers).

## Scope Boundaries
- In scope: the fact family, the strategy, the verbs, tests, docs.
- Out of scope: the probe, the capture, regeneration.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- Registry verbs: src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:385-507
- STORY-2026-09-27-probe-creation-context-harvest
- STORY-2026-09-27-creator-thread-context-capture

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK design the fact family and the strategy output; patch docs.
- [ ] Task: TASK implement the strategy and the verbs; tests over a harvested profile.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `describe` on a conduit that ran a probe window returns the structure, timings, creators and versions of
  every spell it built; reset empties it.

## Validation / Test Plan
- Unit tests on the strategy renderer; component test over a real harvested window.

## UX / API / Data Notes
- Verb placement decided with the owner; value-only output.

## Risks / Mitigations
- Report grows with spell count -> per-conduit slices and a summary view.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Does the report also carry the static ledger view (from the rows) for roots that never ran a window?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Collected from the owner's
  direction (dynamic reporting).

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
  - DevOps report; information strategy; describe; reset
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: FACT
  CLAIM: `DevopsInformationRegistry` holds fact baselines (`report_fact`, `get_fact_record`,
    `list_fact_records`) and derived views are information strategies; the report fits as one strategy
    over profile records.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:385-507
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:41-105
  IMPACT: No new surface is invented for the report.
  NEXT: owner picks; then the design task.
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

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
