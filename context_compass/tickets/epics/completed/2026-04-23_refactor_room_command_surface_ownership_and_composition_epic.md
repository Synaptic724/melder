# Epic: Refactor Room Command Surface Ownership And Composition
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the room-command ownership cut landed and the remaining live work narrowed to codegen-specific implementation.

## Metadata
- Epic ID: EPIC-2026-04-23-refactor-room-command-surface-ownership-and-composition
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-23T22:43:44Z
- Updated: 2026-04-24T01:03:27Z
- Target Window: 2026-Q2
- Related Program/Initiative: AR room command-system cleanup and codegen foundation alignment

## Problem / Opportunity
The current room-command shape is too base-heavy. `CommandSystem` owns the full
manual-runtime command vocabulary, `CapabilityCommandSystem` is effectively a
nominal shell, and `StaticCommandSystem` narrows the base by denying inherited
commands and overriding a few spell behaviors.

That works mechanically, but it is the wrong ownership model:
- the base class owns commands that do not belong to every room
- capability does not earn its own command type with real behavior
- static has to subtract inherited behavior instead of owning its actual
  command surface
- codegen is now at risk of inheriting the same wrong shape instead of staying
  intentionally slim

The opportunity is to refactor room command composition so the base class owns
only true shared infrastructure and each room command system owns the public
commands that actually belong to that room.

## MRP Alignment (Most Reasonable Product)
The MRP is not another round of deny-list patching.

The MRP is an honest room-command model:
- `CommandSystem` contains only shared command infrastructure and truly shared
  public helpers
- `CapabilityCommandSystem` owns the broad manual-runtime command surface
- `StaticCommandSystem` owns static-safe read/live-status behavior
- `CodegenCommandSystem` stays slim and codegen-biased instead of inheriting a
  capability-grade surface by accident

That is the smallest trustworthy foundation for future room behavior. Anything
weaker leaves the command model structurally misleading and keeps pushing room
policy into inheritance subtraction instead of real composition.

## Ticket Contract
- ENTRY_GATE: the user explicitly rejected the current fat-base command design
  and requested a new epic to investigate and then refactor the room command
  systems properly.
- EXECUTION_BOUNDARY: command-system ownership analysis, room-command matrix,
  refactor planning, and later room-command implementation/test follow-on work.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py
  - src/melder/aether/nexus/rift/command_system/static_command_system.py
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py
  - tests/unit/melder/aether/test_nexus.py
  - tickets/epics/2026-04-22_investigate_codegen_foundation_acl_and_validation_strategy_epic.md
- EXIT_GATE: the room-command ownership matrix is explicit, the refactor plan
  is staged, and follow-on stories/tasks can move through implementation
  without re-litigating the command-model architecture.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refactor implies a wider
  AR/runtime redesign than room command ownership and composition.

## Goals (Outcomes)
- Reconstruct the current command ownership model from source.
- Define the target room-command ownership matrix.
- Slim the base `CommandSystem` to shared infrastructure and truly shared
  commands only.
- Define what should move into capability, static, and codegen specifically.
- Stage the refactor and test updates in bounded implementation slices.

## Non-Goals (Explicit Exclusions)
- Rewriting lower Melder runtime semantics.
- Changing unrelated viewer/workstation ownership.
- Implementing the full codegen engine in this epic.
- Broad AR redesign outside the room-command composition boundary.

## Scope Boundaries
- In scope:
  - current room-command ownership and enforcement model
  - shared/base command extraction
  - capability/static/codegen command-surface decomposition
  - directly affected tests and command discovery surfaces
- Out of scope:
  - lower conduit/spell runtime API redesign
  - unrelated ACL/viewer architecture changes
  - non-command room behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new epic and wants the
  ownership matrix worked out before the refactor starts.

## Success Metrics
- One epic owns the room-command decomposition lane.
- The current and target command ownership models are explicit from source.
- The implementation order is clear enough to refactor without more structural
  guessing.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify which commands are truly shared
  - identify which commands belong to capability only
  - identify which commands belong to static only
  - identify which commands belong to codegen only
  - define room-by-room discovery and enforcement behavior
  - define test updates needed for the ownership cut
- Non-functional:
  - no handwaving
  - no fake “similar enough” inheritance claims
  - keep room ownership honest and reviewable

## Constraints / Assumptions
- Static currently proves the deny/override mechanism is real, but that does
  not make the ownership model good.
- Capability is currently mostly a semantic shell.
- Codegen should stay slimmer than capability and should bias the agent toward
  generated Python over a broad manual command surface.
- `meld_existing_spell(...)` needs explicit treatment because current source
  uses it in both capability and static.

## Dependencies / External References
- src/melder/aether/nexus/rift/command_system/command_system.py
- src/melder/aether/nexus/rift/command_system/capability_command_system.py
- src/melder/aether/nexus/rift/command_system/static_command_system.py
- src/melder/aether/nexus/rift/command_system/codegen_command_system.py
- tests/unit/melder/aether/test_nexus.py

## Milestones (Track Progress)
- [ ] Milestone 1: Audit current command ownership and publish the room-command matrix.
      Success means the current and target surfaces are explicit enough to stage the cut.
- [ ] Milestone 2: Refactor shared/base vs room-specific command ownership.
      Success means the base class no longer owns room-only commands.
- [ ] Milestone 3: Align codegen command ownership to the new slim-room model.
      Success means codegen no longer depends on the old fat-base shape.

## Stories (Required to Complete)
- [ ] Story: audit current command ownership and define the target room-command matrix
- [ ] Story: refactor shared infrastructure vs capability/static command ownership
- [ ] Story: align codegen command surface and tests to the new ownership model

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: investigate `CommandSystem`, `CapabilityCommandSystem`, and `StaticCommandSystem`
- [ ] Task: produce an explicit current-vs-target command placement matrix
- [ ] Task: define enforcement strategy after the base is slimmed down
- [ ] Task: update tests for room-specific command ownership and discovery
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The current fat-base command ownership problem is documented with source evidence.
- The target command placement matrix is explicit.
- The refactor is decomposed into bounded implementation slices.
- The resulting room-command model no longer relies on broad subtraction where
  room ownership should be explicit.

## Risks / Mitigations
- Risk: we move methods without preserving real behavior contracts.
  Mitigation: derive the target matrix from live source and tests before moving
  any method.
- Risk: codegen inherits another accidental capability-shaped surface.
  Mitigation: treat codegen as a separately owned slim room command surface.
- Risk: the base class still keeps too much “just in case.”
  Mitigation: force every surviving base public method to justify why it belongs
  to every room.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Investigation first.
- Refactor slices should be validated with focused command-surface and room
  behavior tests.
- Discovery/listing behavior and runtime denial/allow behavior both need test
  coverage after the ownership cut.

## Rollout / Adoption Plan
- First, lock the matrix:
  - shared base
  - capability-owned
  - static-owned
  - codegen-owned
- Then refactor `CommandSystem` down to shared infrastructure plus truly shared
  public methods.
- Then move capability-only commands into `CapabilityCommandSystem`.
- Then keep static as a room-owned read/live-status surface instead of a
  subtraction-heavy child of a fat base.
- Then align `CodegenCommandSystem` to the new slim-room model.
- Finish with targeted tests and room discovery updates.

## Open Questions
- Which public methods are truly shared by all rooms after we strip topology
  mutation and broad activation out of the base?
- Does `meld_existing_spell(...)` belong in capability and static only, or is
  there still a case for keeping it shared?
- Should codegen keep any direct conduit/spell runtime fetches beyond minimal
  bootstrap/discovery helpers?

## Decision Log
- 2026-04-23T22:43:44Z: user requested a new epic because the current command
  model is too base-heavy and room ownership is structurally wrong.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-23T22:43:44Z
  TYPE: FACT
  CLAIM: The current room-command ownership model is fat-base plus subtraction.
    `CommandSystem` publishes the full broad command vocabulary, capability is a
    near-empty semantic shell over that base, and static narrows behavior by
    deny sets plus selected overrides.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:317-374
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:1-18
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:28-45
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:531-558
  IMPACT: The current enforcement works, but room command ownership is not
    honest and codegen risks inheriting the same bad shape.
  NEXT: publish the current-vs-target command placement matrix and decide which
    public methods truly belong in the shared base.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T22:43:44Z
  TYPE: FACT
  CLAIM: Static already proves which commands do not belong in every room.
    Topology mutation and direct `meld(...)` are denied there, while static also
    adds room-specific live-only spell access and spell-status helpers.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:28-45
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:47-135
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:168-460
  - tests/unit/melder/aether/test_nexus.py:3528-3641
  IMPACT: Those denied base methods are the first candidates to move out of the
    shared base and into room-owned command classes.
  NEXT: define the target matrix for shared, capability-only, static-only, and
    codegen-only public commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T22:43:44Z
  TYPE: DECISION
  CLAIM: The target direction is a slim shared base plus room-owned public
    command surfaces. Capability should own the broad manual-runtime commands,
    static should own static-safe read/live-status commands, and codegen should
    stay slimmer than capability so generated Python carries more of the work.
  EVIDENCE:
  - user_instruction: "the base class shouldn't own everything"
  - user_instruction: "the capability command system should own methods that do not exist in static"
  - user_instruction: "codegen doesn't need link adn create conduit and all that stuff"
  IMPACT: Follow-on work should be a real command-ownership refactor, not more
    deny-list patching on top of the current base class.
  NEXT: discuss and lock the room-command placement matrix with the user before
    staging the first implementation story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the command-surface ownership cleanup for room command systems.
The current design works through fat-base inheritance plus room-specific
subtraction, but the target is a slim shared base with explicit room-owned
public command surfaces for capability, static, and codegen.
