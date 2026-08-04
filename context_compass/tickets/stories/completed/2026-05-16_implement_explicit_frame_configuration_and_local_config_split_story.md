# Story: Implement Explicit Frame Configuration And Local Config Split
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed as superseded by the final owner-split story and absorbed into the completed frame-posture migration lane.


## Metadata
- Story ID: STORY-2026-05-16-implement-explicit-frame-configuration-and-local-config-split
- Epic: EPIC-2026-05-16-explicit-aetheric-frame-configuration-and-spellbook-local-config
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T08:07:52Z
- Updated: 2026-05-16T15:47:45Z

## User Narrative
As the project owner, I want frame configuration to be explicit and
thread-safe, so that Spellbooks share only the intended frame-global posture
and keep their richer config behavior local.

## Value / MRP Alignment
This story is the core implementation slice for the ownership model. If this
split lands cleanly, later override/compiler work and AR posture work can
assume stable, explicit configuration semantics instead of hidden adoption.

## Ticket Contract
- ENTRY_GATE: the investigation story has logged the concrete consumer
  inventory, race window, and file-level implementation surface.
- EXECUTION_BOUNDARY: config-ownership and explicit-frame-setup runtime code
  only; no unrelated override/compiler optimization in this story.
- DEPENDENCIES:
  - STORY-2026-05-16-investigate-frame-configuration-ownership-and-race-surfaces
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/spellbook/configuration/configuration.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/nexus/nexus.py`
- EXIT_GATE: explicit frame configure behavior exists, full-config adoption is
  removed, frame-global fields are sourced from frame posture, and conjure
  respects the bounded wait/timeout semantics.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the final field split proves
  incompatible with current AR or conduit runtime behavior.

## Requirements (Functional)
- Add explicit `Spellbook.configure_aetheric_frame(...)`.
- Add frame-local configuration state / claim semantics on `AethericFrame`.
- Remove Spellbook adoption of the full config object from Aether.
- Make `conjure()` require configured frame posture and wait only when another
  Spellbook is actively configuring the same frame.
- Move frame-global consumers off the full config object.
- Keep Spellbook-local hooks and local-only flags local.

## Requirements (Non-Functional)
- Thread-safe and deterministic.
- Explicit user/agent-visible lifecycle.
- No hidden fallback to implicit frame configuration during conjure.

## Scope Boundaries
- In scope:
  - frame config state machine/claim path
  - Spellbook explicit frame configure path
  - field ownership split
  - bounded wait/timeout behavior
- Out of scope:
  - new override/compiler optimization behavior
  - broad AR feature redesign
  - unrelated lifecycle cleanup refactors

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the investigation inventory is sufficient and the user
  explicitly chose a bounded first implementation slice around explicit shared
  framewide rich-config mechanics.

## Dependencies / Related Work
- tickets/epics/2026-05-16_explicit_aetheric_frame_configuration_and_spellbook_local_config_epic.md
- tickets/stories/2026-05-16_investigate_frame_configuration_ownership_and_race_surfaces_story.md

## Tasks (Implementation Checklist)
- [ ] Task: implement frame configuration state/claim semantics on `AethericFrame`
- [ ] Task: add explicit `Spellbook.configure_aetheric_frame(...)`
- [ ] Task: remove `_initialize_configuration()` adoption of full frame config
- [ ] Task: reroute frame-global consumers to `AethericFrameConfiguration`
- [ ] Task: keep `Configuration` local and preserve hook localization by `spellbook_id`
- [ ] Enforce Ticket Microcycle across the implementation lane.
- [ ] Require meaningful-finding note updates during implementation.

## Acceptance Criteria
- Spellbook no longer inherits another Spellbookâ€™s full config object from Aether.
- Frame posture is configured explicitly and canonically.
- `conjure()` waits only for active frame configuration and otherwise raises
  clearly when the frame is not configured.
- The agreed local/global field split is reflected in code.

## Validation / Test Plan
- Focused unit/component/integration work deferred to the paired test story.
- Runtime implementation should be validated only through the explicit test
  surfaces named there.

## UX / API / Data Notes
- Likely new public API:
  - `Spellbook.configure_aetheric_frame(...)`
- Likely internal frame state:
  - `UNCONFIGURED`
  - `CONFIGURING`
  - `CONFIGURED`
  - `FAILED`
- Candidate local-vs-global split to preserve:
  - frame-global: `system_state`, `ai_native_enabled`, `rift_enabled`
  - likely local: hooks, disposal, worker/timer tuning,
    `full_ahead_of_time_compilation`, `overrides_enabled`

## Risks / Mitigations
- Risk: moving `overrides_enabled` local breaks current spell transfer/runtime
  assumptions.
  Mitigation: restamp effective spell posture from the new owner path and
  validate in the test story.
- Risk: bounded wait semantics hide failure.
  Mitigation: preserve explicit `FAILED` state and clear timeout errors.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No ownership split applied without investigation-story evidence.

## Open Questions
- Final timeout default (`5s` vs `10s`).
- Whether `FAILED` requires explicit reset or can be re-entered through a new
  configure attempt.
- Exact owner bookkeeping for same-Spellbook re-entry.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-16T08:07:52Z
  TYPE: PLAN
  CLAIM: The intended implementation direction is already sharply defined:
    keep `AethericFrameConfiguration` as the shared canonical posture, make
    frame setup explicit, stop inheriting full config from Aether, and allow
    `conjure()` to wait only when another Spellbook is actively configuring the
    same frame.
  EVIDENCE:
  - user_instruction: "we need a threadsafe way to turn on a gate"
  - user_instruction: "it might make more sense to add a method into spellbook called, configure_aetheric_frame"
  - user_instruction: "we basically need to stop conjure and raise until the aetheric_frame is configured"
  - user_instruction: "if someone is setting up the configuration we can still hit a condition instead of raise right away"
  IMPACT: The implementation can be bounded around explicit frame setup and
    removal of hidden full-config sharing without touching override/compiler
    behavior yet.
  NEXT: wait for the investigation inventory, then patch the frame and
    Spellbook ownership path first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:40:21Z
  TYPE: DECISION
  CLAIM: `debugging` is no longer part of the config shape we are trying to
    preserve. The feature has one current conduit-side consumer, but the user
    explicitly wants it removed because the original monkey-patching idea is
    not a good fit for the repo's slotted runtime objects.
  EVIDENCE:
  - user_instruction: "I think we can remove debugging"
  - user_instruction: "originally I wanted to monkey patch things onto objects but slots stops that"
  - src/melder/spellbook/configuration/configuration.py:87-100
  - src/melder/aether/conduit/conduit.py:969-972
  IMPACT: The implementation story should treat `debugging` as a removal target
    during the ownership cleanup instead of trying to preserve it as a local
    Spellbook feature.
  NEXT: keep `debugging` out of the preserved local/global split and carry the
    removal into the paired test story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:07:52Z
  TYPE: FACT
  CLAIM: The concrete runtime surfaces to modify are already visible from the
    current code paths. The frame ownership/state work belongs in
    `aetheric_frame.py` and `aether.py`; the explicit setup and no-full-config
    adoption work belongs in `spellbook.py` and
    `spellbook_creation_system.py`; the local/global field split touches
    `configuration.py` and `aetheric_frame_configuration.py`; and the runtime
    consumers likely needing reroutes are `conduit.py`, `nexus.py`, and
    `frame_descriptor_manager.py`.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:93-96
  - src/melder/aether/aether.py:734-867
  - src/melder/spellbook/spellbook.py:2887-2908
  - src/melder/spellbook/spellbook_creation_system.py:222-225
  - src/melder/spellbook/configuration/configuration.py:917-944
  - src/melder/aether/conduit/conduit.py:969-972
  - src/melder/aether/nexus/nexus.py:2376-2454
  - src/melder/aether/nexus/frame_descriptor_manager.py:168-178
  IMPACT: The implementation story is bounded enough to proceed later without
    another broad repo scan.
  NEXT: preserve this file list as the allowed implementation surface unless
    the investigation story finds another true consumer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when ownership boundaries, state semantics, or field splits change.
- Reference investigation evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story stages the bounded runtime implementation for explicit frame
configuration and local Spellbook config ownership.

