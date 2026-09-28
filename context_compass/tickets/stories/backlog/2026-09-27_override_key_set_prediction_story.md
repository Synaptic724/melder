# Story: Override key-set prediction - precompile the key sets the profile saw, report their frequency

## Metadata
- Story ID: STORY-2026-09-27-override-key-set-prediction
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p3
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want the override key sets a spell was melded with during the window to be compiled at
harvest rather than on first use in a later process or scope, with their frequency in the report and pre-sized
operand tuples, so that the first override meld of a known shape never pays a compile on the warm path.

## Value / MRP Alignment
Override plans already compile once per key set under the runtime's compile lock and are read lock-free after;
the profile turns 'first use' into 'known shape', and the report shows which override shapes an application
really uses. Small, but it is the one place a warm meld still compiles.

## Ticket Contract
- ENTRY_GATE: owner's pick; the probe story; patch docs before src.
- EXECUTION_BOUNDARY: `site_plan_override_runtime.py` (precompile from a key-set list), the harvest record
  (key-set histogram), the report, tests.
- DEPENDENCIES: STORY-2026-09-27-probe-creation-context-harvest; STORY-2026-09-27-creation-profile-report.
- EXIT_GATE: key sets from the profile compiled at harvest; frequency in the report; a first override meld
  of a known key set measured without the compile; default off unchanged.
- FAILURE_ESCALATION: DECISION_REQUEST if the compile cost is negligible on the owner's shapes (park).

## Requirements (Functional)
- Harvest records the key-set histogram per spell.
- Regenerate precompiles the observed key sets through the existing runtime.
- The report shows the histogram.

## Requirements (Non-Functional)
- No change to key errors or their caching rule (a failed key set is not cached).

## Scope Boundaries
- In scope: the histogram, the precompile, the report line, tests.
- Out of scope: persistence of the histogram across processes (the persisted-profiles story).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtim
  e.py:119-165
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtim
  e.py:369-405

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK measure the first-use compile cost per key set in the harness.
- [ ] Task: TASK implement the histogram and the precompile; tests.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A known key set's first override meld after harvest runs the stored plan; the report lists the key sets
  and counts.

## Validation / Test Plan
- Unit tests on the histogram; component test on precompile; harness measurement.

## UX / API / Data Notes
- No public API change.

## Risks / Mitigations
- Precompiling unused key sets wastes conjure time -> only sets the window saw.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Is the first-use compile cost worth anything outside cold start?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Collected from the
  superseded epic's axes.

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
  - override key sets; precompile; histogram
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: FACT
  CLAIM: Override plans compile once per key set under the compile lock on first use and are read lock-free
    after; the manifest's rows are what the plan is emitted from.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:119-165
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:369-405
  IMPACT: The story is a cold-start lever unless the owner's apps meld overrides constantly.
  NEXT: owner picks; measure the compile cost first.
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
