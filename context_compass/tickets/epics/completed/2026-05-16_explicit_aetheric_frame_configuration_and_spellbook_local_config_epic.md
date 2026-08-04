# Epic: Explicit Aetheric Frame Configuration And Spellbook Local Config
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed as superseded and absorbed into the final frame-posture owner migration lane.


## Metadata
- Epic ID: EPIC-2026-05-16-explicit-aetheric-frame-configuration-and-spellbook-local-config
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T08:07:52Z
- Updated: 2026-05-16T15:47:45Z
- Target Window: 2026-Q2
- Related Program/Initiative: Runtime configuration ownership and explicit frame bootstrap

## Problem / Opportunity
The current runtime stores both the rich Spellbook `Configuration` object and
the narrow `AethericFrameConfiguration` on the same frame. `Spellbook`
initialization currently pulls the shared full config from `Aether` when one
already exists, while the narrow frame posture is separately bound under
first-writer-wins semantics. That creates an ownership split where:

- the rich local config can become frame-shared implicitly
- the narrow frame posture is treated as canonical for AR/Nexus behavior
- concurrent Spellbooks targeting one frame can race into inconsistent shared
  state

The user wants an explicit AI-native setup model:

- one Spellbook configures the frame posture explicitly
- later Spellbooks inherit only the frame posture, not another Spellbook's
  full rich config
- `conjure()` should stop if the frame is not configured, but may wait a
  short bounded interval when another Spellbook is already configuring the
  frame during bootstrap

## MRP Alignment (Most Reasonable Product)
The MRP is not "rewrite every config surface at once." The MRP is:

- one explicit canonical frame-configuration path
- one clear split between frame-global posture and Spellbook-local behavior
- one thread-safe frame claim/configure lifecycle
- one bounded conjure wait/timeout rule that is understandable to agents

That gives the runtime a stable configuration ownership model before more
override/compiler or AR posture work continues.

## Ticket Contract
- ENTRY_GATE: the user explicitly wants this modeled as its own tracked lane
  and agrees with the direction of explicit frame configuration, local
  Spellbook config, and bounded bootstrap waiting.
- EXECUTION_BOUNDARY: define and route the config-ownership investigation,
  implementation, and test stories for the frame/local split; do not patch the
  runtime yet in this epic.
- DEPENDENCIES:
  - `src/melder/spellbook/configuration/configuration.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aether.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/nexus/nexus.py`
- EXIT_GATE: the epic has one investigation story with explicit change
  inventory, one implementation story with bounded modification surfaces, and
  one test story with the exact test areas to update.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the field split or
  configure/wait semantics prove incompatible with current frame/AR behavior.

## Goals (Outcomes)
- Define the exact ownership split between frame-global posture and
  Spellbook-local config.
- Define an explicit `Spellbook.configure_aetheric_frame(...)` setup path.
- Define the thread-safe frame configuration claim/state model.
- Define the bounded wait semantics for `conjure()` when frame setup is in
  progress.
- Stage implementation and test work with concrete file-level scope.

## Non-Goals (Explicit Exclusions)
- Direct runtime implementation in this epic.
- Broad override/compiler optimization implementation in this epic.
- Reworking unrelated Nexus/descriptor features.
- Changing completed ticket history.

## Scope Boundaries
- In scope:
  - frame config ownership model
  - Spellbook local config ownership model
  - explicit frame configure API direction
  - wait/timeout semantics for in-progress frame setup
  - file/test inventory for the follow-on change
- Out of scope:
  - landing the runtime refactor now
  - broad policy changes outside config ownership
  - reopening unrelated mutation or crystallizer work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved starting with one epic plus
  investigation/implementation/test stories before runtime edits.

## Success Metrics
- The current race/ownership problem is documented with direct source evidence.
- The frame-global vs local field split is explicit.
- The implementation story names the concrete runtime surfaces to modify.
- The test story names the exact test suites and concurrency cases to update.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify all current consumers of full `Configuration`
  - identify all current consumers of `AethericFrameConfiguration`
  - define the explicit frame-configuration lifecycle
  - define the bounded wait/timeout behavior for `conjure()`
  - define the proposed field split
- Non-functional:
  - evidence-backed only
  - preserve thread-safety and deterministic ownership
  - keep agent-visible behavior explicit rather than hidden

## Constraints / Assumptions
- Most users will target the `"default"` frame, but the model still needs to
  work for any named frame.
- Hooks are already localized by `spellbook_id` even under a shared config
  object and should remain local.
- `overrides_enabled` is likely Spellbook-local, not frame-global, but this
  must be preserved explicitly in the implementation story.

## Dependencies / External References
- `codex/context_compass/tickets/epics/2026-05-11_add_overrides_enabled_configuration_and_spell_gate_epic.md`
- `codex/context_compass/tickets/epics/2026-05-11_investigate_aot_creation_context_override_disable_and_no_overrides_compiler_path_epic.md`

## Milestones (Track Progress)
- [ ] Milestone 1: map current ownership and race surfaces precisely
- [ ] Milestone 2: define the explicit frame configure lifecycle and field split
- [ ] Milestone 3: stage bounded implementation and test stories

## Stories (Required to Complete)
- [ ] Story: STORY-2026-05-16-investigate-frame-configuration-ownership-and-race-surfaces - map current ownership, races, and exact modification surfaces
- [ ] Story: STORY-2026-05-16-implement-explicit-frame-configuration-and-local-config-split - implement the explicit frame configure path and ownership split
- [ ] Story: STORY-2026-05-16-update-frame-configuration-and-local-config-tests - update and expand tests for the new lifecycle and concurrency rules

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: complete the investigation story before runtime edits
- [ ] Task: keep the implementation story bounded to frame/spellbook/conduit/Nexus config surfaces
- [ ] Task: keep the test story bounded to config ownership, explicit setup, and bounded wait semantics
- [ ] Task: verify Ticket Microcycle enforcement across active config-ownership work

## Acceptance Criteria (Epic Done)
- The investigation story captures the current state with direct evidence.
- The implementation story names the exact files/behaviors to change.
- The test story names the exact tests and new race/timeout cases to cover.
- The board routes cleanly to this lane for future execution.

## Risks / Mitigations
- Risk: we move too many fields out of `Configuration` without proving their
  actual consumers.
  Mitigation: inventory consumers first and keep the split evidence-backed.
- Risk: bounded wait semantics hide configuration failures.
  Mitigation: treat `FAILED` as explicit state and raise clear timeout/failure
  errors after the wait path.
- Risk: implementation drifts into override/compiler work immediately.
  Mitigation: keep that work as a dependent lane, not part of this epic.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No ownership-split claims without direct source evidence.

## Validation / Test Approach
- Investigation/design only in this epic.
- Validation is coherence of the ownership model and readiness for the
  implementation/test stories.

## Rollout / Adoption Plan
- First map the current state and exact change surfaces.
- Then execute the implementation story.
- Then update/expand the test surfaces for explicit frame configure behavior.

## Open Questions
- Final frame-state enum names and timeout policy.
- Whether `overrides_enabled` should remain entirely local or ever appear in
  derived frame posture again.
- Whether `FAILED` should require an explicit retry/reset API or allow direct
  re-entry by a later Spellbook.

## Decision Log
- 2026-05-16T08:07:52Z: Opened to track the explicit frame-configuration and
  Spellbook-local config direction before runtime edits begin.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-16T08:07:52Z
  TYPE: FACT
  CLAIM: The current runtime stores both the full shared Spellbook
    `Configuration` and the narrow `AethericFrameConfiguration` on each frame.
    `Spellbook` initialization currently adopts the full config from Aether
    when one is already bound, while the narrow frame posture is separately
    bound under first-writer-wins semantics. Hooks are the one clear localized
    exception because they are already keyed by `spellbook_id`.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:93-96
  - src/melder/spellbook/spellbook.py:2887-2908
  - src/melder/aether/aether.py:734-745
  - src/melder/aether/aether.py:806-809
  - src/melder/aether/aether.py:848-867
  - src/melder/spellbook/configuration/configuration.py:482-509
  - src/melder/spellbook/configuration/configuration.py:603-634
  IMPACT: The frame/local boundary is conceptually present but only partially
    realized, and the current mixed sharing model is the root of the
    ownership/race confusion.
  NEXT: create the investigation, implementation, and test stories with exact
    change surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when ownership boundaries, lifecycle states, or field-split
  decisions change.
- Reference story evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the explicit frame-configuration and Spellbook-local config
direction before runtime edits begin.

