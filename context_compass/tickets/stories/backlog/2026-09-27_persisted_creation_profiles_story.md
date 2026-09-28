# Story: Persisted creation profiles - carry the profile and the chosen version in the .melc manifest

## Metadata
- Story ID: STORY-2026-09-27-persisted-creation-profiles
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p3
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want the harvested profile and the version key a spell settled on to ride its `.melc`
manifest, so that the next process starts with the specialized version instead of re-probing from plain -
optimistic PGO across processes, guarded exactly like the in-process swap.

## Value / MRP Alignment
The cache already re-emits every plan from its rows at hydration; a profile and a version key beside those
rows are a natural extension, and the generation bump retires older bundles as every cache change has. It is
worth doing only after a version has earned its win in-process, which is why it is last.

## Ticket Contract
- ENTRY_GATE: owner's pick; the versioning story shipped with a measured win; patch docs before src.
- EXECUTION_BOUNDARY: `caching_system.py` (generation bump), the spell payload manifest (profile + version
  key), the hydrators (start from the persisted version, guarded), tests.
- DEPENDENCIES: STORY-2026-09-27-creation-context-versioning; STORY-2026-09-27-probe-selected-codegen-
  styles.
- EXIT_GATE: a warm conjure hydrates the persisted version and its guard; a mismatch (different shape)
  deopts to plain and re-probes; cache generation bumped; default off unchanged.
- FAILURE_ESCALATION: DECISION_REQUEST if the persisted version's guard cannot be checked cheaply at
  hydration.

## Requirements (Functional)
- Manifest carries the profile record and the version key per spell (value-only).
- Manifest also carries the PGO attempt count and the best measured ns (owner, 2026-09-28), so hydration
  restores the "budget spent, leave it alone" state and a new process does not re-run the tournament.
- Hydration publishes the persisted version behind its guard; a guard failure at first use deopts and re-
  arms the probe.
- Cache generation bump; older bundles cold-reset as today.

## Requirements (Non-Functional)
- No change for bundles without a profile; nothing persisted with profiling off.

## Scope Boundaries
- In scope: the manifest fields, the hydration path, the generation bump, tests.
- Out of scope: cross-machine profiles; anything in the Crystallizer.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- src/melder/utilities/caching_system/caching_system.py:57-115
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtim
  e.py:369-405

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK design the manifest fields and the hydration guard; patch docs.
- [ ] Task: TASK implement and test a warm conjure that starts specialized and one that deopts.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A second process over the same bundle runs the specialized version from its first meld and the report
  shows it; a changed shape falls back to plain.

## Validation / Test Plan
- Unit tests on the manifest; component test across two conjures with caching on.

## UX / API / Data Notes
- No public API change; cache generation bump.

## Risks / Mitigations
- A persisted version that no longer fits -> guard at hydration, deopt at first use.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Does a persisted profile expire (age, generation), or does the next harvest replace it?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Collected from the
  superseded epic's open question on persistence; ranked last.

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
  - manifest; generation bump; persisted version
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: FACT
  CLAIM: The creation cache is one marshal bundle per conduit with a manifest per spell payload; plans are re-
    emitted from the manifest's rows at hydration; admission is exact release + generation + Python tag.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:57-115
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:369-405
  IMPACT: Persisting a profile is a manifest extension, not a new file.
  NEXT: owner picks after a version has a measured in-process win.
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
