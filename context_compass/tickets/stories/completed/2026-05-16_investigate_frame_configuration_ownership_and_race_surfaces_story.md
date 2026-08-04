# Story: Investigate Frame Configuration Ownership And Race Surfaces
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed after the investigation baseline was absorbed into the completed frame-posture migration lane.


## Metadata
- Story ID: STORY-2026-05-16-investigate-frame-configuration-ownership-and-race-surfaces
- Epic: EPIC-2026-05-16-explicit-aetheric-frame-configuration-and-spellbook-local-config
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T08:07:52Z
- Updated: 2026-05-16T15:47:45Z

## User Narrative
As the project owner, I want the current frame/local configuration ownership
and race surfaces mapped precisely, so that the implementation change does not
guess about what is shared today and what must become explicit.

## Value / MRP Alignment
This story protects the core ownership boundary. If we move fields or add
frame-state gating without proving current consumers first, we will likely
rebuild the wrong config shape and reintroduce hidden coupling elsewhere.

## Ticket Contract
- ENTRY_GATE: the new epic is active and the user explicitly wants the current
  state investigated in detail before runtime edits.
- EXECUTION_BOUNDARY: investigation and inventory only; no runtime code edits
  in this story.
- DEPENDENCIES:
  - `src/melder/spellbook/configuration/configuration.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aether.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/frame_descriptor_manager.py`
- EXIT_GATE: the story records the current ownership split, race surface, and
  exact implementation/test modification targets.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the consumer inventory shows
  the field split is materially different from the current design direction.

## Requirements (Functional)
- Inventory all current consumers of full `Configuration`.
- Inventory all current consumers of `AethericFrameConfiguration`.
- Identify the current race window across Spellbook init/freeze/bind/conjure.
- Identify which fields should become frame-global vs Spellbook-local.
- Record the concrete runtime and test files the implementation story will
  need to touch.

## Requirements (Non-Functional)
- Evidence-backed only.
- No hidden assumptions about default-frame-only behavior.
- Preserve the current hook-localization distinction explicitly.

## Scope Boundaries
- In scope:
  - ownership inventory
  - race inventory
  - field-split inventory
  - implementation/test surface inventory
- Out of scope:
  - applying the refactor
  - modifying tests
  - altering ticket state outside this lane

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user asked to start by logging the detailed
  investigation and exact change surfaces before implementation.

## Dependencies / Related Work
- tickets/epics/2026-05-16_explicit_aetheric_frame_configuration_and_spellbook_local_config_epic.md
- tickets/epics/2026-05-11_add_overrides_enabled_configuration_and_spell_gate_epic.md
- tickets/epics/2026-05-11_investigate_aot_creation_context_override_disable_and_no_overrides_compiler_path_epic.md

## Tasks (Implementation Checklist)
- [ ] Task: inventory current `Configuration` consumers and categorize them as frame-global or local-only
- [ ] Task: inventory current `AethericFrameConfiguration` consumers and note where it is canonical already
- [ ] Task: map the Spellbook init -> freeze -> bind -> conjure race window in detail
- [ ] Task: record exact implementation and test files to modify in the later stories
- [ ] Enforce Ticket Microcycle across the active investigation lane.
- [ ] Require meaningful-finding note updates during discovery.

## Acceptance Criteria
- The story states what the frame currently stores.
- The story states what `Spellbook` currently adopts from Aether.
- The story states which fields should be frame-global vs local.
- The story states the exact runtime files and tests that the later stories
  will modify.

## Validation / Test Plan
- Investigation only.
- Validation is source-backed coherence across the inventory and change plan.

## UX / API / Data Notes
- Likely public API addition:
  - `Spellbook.configure_aetheric_frame(...)`
- Likely internal frame state:
  - `UNCONFIGURED`
  - `CONFIGURING`
  - `CONFIGURED`
  - `FAILED`

## Risks / Mitigations
- Risk: overstate how isolated the frame posture already is.
  Mitigation: treat all consumers as UNKNOWN until directly inventoried.
- Risk: implementation surfaces widen beyond the config path.
  Mitigation: log exact file-level change targets before coding.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-surface ownership claims without direct source evidence.

## Open Questions
- Whether `overrides_enabled` should remain strictly local.
- Whether the frame configure API should allow explicit compatible re-entry.
- Whether the timeout belongs on `conjure()` only or on configure paths too.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-16T08:07:52Z
  TYPE: FACT
  CLAIM: The current ownership/race problem is already narrow enough to map
    cleanly. The frame stores both `_configuration` and `_frame_configuration`;
    `Spellbook` initialization adopts the full config from Aether when one is
    bound; the narrow frame posture is separately first-writer-wins; and
    hooks are already localized through `spellbook_id` inside the shared config
    object.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:93-96
  - src/melder/spellbook/spellbook.py:2887-2908
  - src/melder/aether/aether.py:734-745
  - src/melder/aether/aether.py:806-809
  - src/melder/aether/aether.py:848-867
  - src/melder/spellbook/configuration/configuration.py:482-509
  - src/melder/spellbook/configuration/configuration.py:603-634
  IMPACT: The later implementation can be bounded around removing full-config
    frame sharing while preserving the already-local hook behavior.
  NEXT: enumerate all full-config and frame-posture consumers, then log the
    exact files for implementation and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:07:52Z
  TYPE: FACT
  CLAIM: The current consumer split is already concrete enough to stage the
    later stories. Full `Configuration` is directly consumed by Spellbook and
    Conduit runtime paths for `system_state`, `debugging`, disposal metadata,
    and other build/runtime knobs, while `AethericFrameConfiguration` is
    already the canonical posture object for Nexus target-frame validation and
    descriptor publishability. The likely field split is therefore:
    frame-global = `system_state`, `ai_native_enabled`, `rift_enabled`;
    Spellbook-local = hooks, debugging, disposal settings, scheduler tuning,
    `full_ahead_of_time_compilation`, and likely `overrides_enabled`.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:2376-2454
  - src/melder/aether/nexus/frame_descriptor_manager.py:168-178
  - src/melder/aether/nexus/frame_descriptor_manager.py:213-219
  - src/melder/aether/conduit/conduit.py:969-972
  - src/melder/spellbook/spellbook_creation_system.py:398-408
  - src/melder/spellbook/spellbook_creation_system.py:446-455
  - src/melder/spellbook/spellbook.py:2058-2071
  - src/melder/spellbook/configuration/configuration.py:482-509
  - src/melder/spellbook/configuration/configuration.py:603-634
  IMPACT: The implementation story can now be bounded around removing full
    config adoption from Aether while rerouting frame-global consumers to the
    narrow posture object.
  NEXT: list the concrete runtime files and test files to touch in the later
    implementation and test stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when ownership boundaries, race surfaces, or file inventories change.
- Reference source evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the detailed source-backed inventory for the frame/local config
split and the exact surfaces the later implementation and test stories should touch.

