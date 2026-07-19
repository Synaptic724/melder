# Task: Inventory Frame Local Configuration Consumers And Race Window
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed after the source-backed inventory was absorbed into the completed frame-posture migration lane.


## Metadata
- Task ID: TASK-2026-05-16-inventory-frame-local-configuration-consumers-and-race-window
- Story: STORY-2026-05-16-investigate-frame-configuration-ownership-and-race-surfaces
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T08:30:02Z
- Updated: 2026-05-16T15:47:45Z

## Objective
Produce the concrete source-backed inventory for the frame/local configuration
split: current consumers of the full `Configuration`, current consumers of
`AethericFrameConfiguration`, the exact Spellbook init/freeze/bind/conjure race
window, and the exact runtime/test files the later stories must modify.

## Ticket Contract
- ENTRY_GATE: the explicit frame/local config epic and investigation story are
  active, and the user explicitly asked to investigate this further before
  runtime edits begin.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/configuration/configuration.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aether.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/frame_descriptor_manager.py`
  - directly relevant tests under `tests/unit/melder/**` and
    `tests/integration/melder/**` when needed as evidence
- DEPENDENCIES:
  - `codex/context_compass/tickets/epics/2026-05-16_explicit_aetheric_frame_configuration_and_spellbook_local_config_epic.md`
  - `codex/context_compass/tickets/stories/2026-05-16_investigate_frame_configuration_ownership_and_race_surfaces_story.md`
- EXIT_GATE: the current ownership model, race window, field split, and exact
  implementation/test modification surfaces are logged with evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the current consumers
  prove a materially different split than the current direction expects.

## Scope Boundaries
- In scope:
  - current consumer inventory
  - current race inventory
  - field split inventory
  - implementation and test surface inventory
- Out of scope:
  - runtime refactor
  - test modification
  - ticket cleanup outside this lane

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to continue the investigation,
  and the lane now has enough direction to justify a concrete task-level
  inventory pass.

## Steps / Checklist
- [ ] Inventory all current consumers of full `Configuration`.
- [ ] Inventory all current consumers of `AethericFrameConfiguration`.
- [ ] Map the current Spellbook init -> freeze -> bind -> conjure race window precisely.
- [ ] Record the likely frame-global vs Spellbook-local field split.
- [ ] Record the exact runtime files to modify in the implementation story.
- [ ] Record the exact test files and new test cases to modify in the test story.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed ownership and race inventory
- exact runtime file modification list
- exact test file and case inventory

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-16_inventory_frame_local_configuration_consumers_and_race_window_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/tickets/stories/2026-05-16_investigate_frame_configuration_ownership_and_race_surfaces_story.md

## Validation
- Not run.
- Investigation only.

## Risks / Rollback Notes
- Risk: we conclude the split too early and miss a hidden consumer.
  Rollback: keep unverified surfaces `UNKNOWN` and extend the inventory before
  implementation begins.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-16T08:30:02Z
  TYPE: FACT
  CLAIM: The current consumer split is already concrete enough to support a
    bounded task-level inventory. The frame stores both the full shared
    `Configuration` and the narrow `AethericFrameConfiguration`; Spellbook init
    adopts the full config from Aether when present; frame posture is separately
    first-writer-wins; Nexus and descriptor publication already prefer the
    narrow frame posture; and hooks remain localized by `spellbook_id` even
    under the shared full config object.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:93-96
  - src/melder/spellbook/spellbook.py:2887-2908
  - src/melder/aether/aether.py:734-745
  - src/melder/aether/aether.py:806-809
  - src/melder/aether/aether.py:848-867
  - src/melder/aether/nexus/nexus.py:2421-2454
  - src/melder/aether/nexus/frame_descriptor_manager.py:168-178
  - src/melder/spellbook/configuration/configuration.py:482-509
  - src/melder/spellbook/configuration/configuration.py:603-634
  IMPACT: The implementation can likely remove full-config frame sharing
    without destabilizing Nexus, because the published frame contract already
    prefers the narrow posture object.
  NEXT: finish the inventory by listing all remaining full-config consumers and
    the exact race window across Spellbook init/freeze/bind/conjure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:30:02Z
  TYPE: FACT
  CLAIM: The current runtime consumers divide cleanly into two groups. The
    narrow `AethericFrameConfiguration` is already the canonical frame posture
    for Nexus target-frame validation and descriptor publication, while the
    full `Configuration` still drives Spellbook/Conduit runtime behavior such
    as dynamic-mode policy checks, debugger mode, disposal metadata, and other
    build/runtime knobs. This confirms the likely split:
    frame-global = `system_state`, `ai_native_enabled`, `rift_enabled`;
    local-only = hooks, debugging, disposal/disposal-method names, scheduler
    tuning, `full_ahead_of_time_compilation`, and likely `overrides_enabled`.
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
  IMPACT: The implementation story can stay narrow: remove full-config frame
    sharing, keep frame-global posture in `AethericFrameConfiguration`, and
    reroute only the true frame-global consumers.
  NEXT: log the exact race window and the test files that currently codify the
    shared-config behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:30:02Z
  TYPE: FACT
  CLAIM: The current tests explicitly encode the shared-full-config behavior,
    so the test story will need to rewrite those expectations. The clearest
    examples are component and integration Spellbook tests that expect a
    Spellbook on an already-configured frame to adopt Aether's full
    `Configuration` object, and Aether unit tests that still treat
    `_bind_configuration` / `_get_configuration` as first-class frame APIs.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_configuration.py:58-68
  - tests/component/melder/spellbook/test_spellbook_component_configuration.py:84-93
  - tests/component/melder/spellbook/test_spellbook_component_configuration.py:109-117
  - tests/integration/melder/spellbook/test_spellbook_integration_core.py:255-290
  - tests/unit/melder/aether/test_aether.py:689-720
  - tests/unit/melder/aether/test_aether.py:731-743
  - tests/unit/melder/aether/test_aether.py:804-832
  IMPACT: The test story must cover not only the new explicit frame configure
    path, but also the removal or rewrite of existing tests that assert full
    config sharing through Aether.
  NEXT: record the exact runtime files to patch so the implementation and test
    stories can proceed without another broad scan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:30:02Z
  TYPE: FACT
  CLAIM: The concrete runtime patch surface is now explicit. The ownership
    change starts in `aetheric_frame.py` and `aether.py` for frame-owned
    posture state and claim/wait behavior; `spellbook.py` and
    `spellbook_creation_system.py` for explicit frame configure and removal of
    hidden full-config adoption; `configuration.py` and
    `aetheric_frame_configuration.py` for the field split; and `conduit.py`,
    `nexus.py`, and `frame_descriptor_manager.py` for rerouting consumers to
    the right config layer.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:93-96
  - src/melder/aether/aether.py:734-867
  - src/melder/spellbook/spellbook.py:2887-2908
  - src/melder/spellbook/spellbook.py:3071-3131
  - src/melder/spellbook/spellbook.py:3140-3178
  - src/melder/spellbook/spellbook_creation_system.py:222-225
  - src/melder/spellbook/configuration/configuration.py:917-944
  - src/melder/aether/conduit/conduit.py:969-972
  - src/melder/aether/nexus/nexus.py:2376-2454
  - src/melder/aether/nexus/frame_descriptor_manager.py:168-178
  IMPACT: The implementation story no longer needs another broad source
    discovery pass before code work can be scoped.
  NEXT: synthesize the final race-window description and convert the story/task
    states to reflect that the investigation is implementation-ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:40:21Z
  TYPE: DECISION
  CLAIM: `debugging` should be removed from the surviving configuration model
    rather than preserved as a local Spellbook feature. The current direct
    consumer is only the conduit-side `__debugger_mode__` flag, and the user
    explicitly no longer wants the feature because the original monkey-patching
    idea is not compatible with the repo's slotted object model.
  EVIDENCE:
  - user_instruction: "I think we can remove debugging, I don't see a use for it"
  - user_instruction: "originally I wanted to monkey patch things onto objects but slots stops that"
  - src/melder/spellbook/configuration/configuration.py:87-100
  - src/melder/aether/conduit/conduit.py:969-972
  IMPACT: The implementation story should stop treating `debugging` as a local
    config field to preserve and instead treat it as a removal candidate in the
    same ownership cleanup.
  NEXT: update the staged implementation/test expectations to reflect debugging
    removal before runtime edits begin.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T11:04:03Z
  TYPE: FACT
  CLAIM: There is a low-churn implementation path for optional frame-shared
    rich Spellbook config if we make it an explicit permanent frame-posture
    boolean instead of the current hidden Aether behavior. The current runtime
    already has all three anchor points needed for that shape:
    `AethericFrame` still stores both `_configuration` and
    `_frame_configuration`, `Spellbook._initialize_configuration()` already
    knows how to adopt or create a `SpellbookConfiguration`, and Aether already
    treats the narrow frame posture as first-writer-wins. So a new permanent
    frame field like `shared_framewide_spellbook_configuration` could decide
    whether first conjure locks both the frame posture and the rich
    SpellbookConfiguration into the frame, or only locks the frame posture
    while later Spellbooks keep local rich config objects.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:93-96
  - src/melder/spellbook/spellbook.py:2887-2927
  - src/melder/aether/aether.py:734-792
  - src/melder/aether/aether.py:794-867
  - src/melder/spellbook/spellbook.py:3186-3239
  IMPACT: We do not have to invent a second ownership mechanism for the rich
    Spellbook config if the user wants optional frame-wide sharing. We can keep
    the frame `_configuration` slot, but make its use explicit and permanent
    through the frame posture instead of unconditional hidden adoption.
  NEXT: decide the default value and then map the exact runtime changes:
    `AethericFrameConfiguration` adds the boolean and default creation path;
    `Spellbook._initialize_configuration()` adopts frame-wide rich config only
    when the canonical frame posture says to; and first conjure binds the rich
    config into Aether only when that boolean is true.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the detailed inventory for the explicit frame-configuration and
local Spellbook-config split before implementation begins.

