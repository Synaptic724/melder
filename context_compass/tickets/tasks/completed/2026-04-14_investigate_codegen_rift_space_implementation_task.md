# Task: Investigate Codegen RiftSpace Implementation
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after the codegen-room boundary was established and later
  internal codegen-system work superseded the investigation lane.

## Metadata
- Task ID: TASK-2026-04-14-investigate-codegen-rift-space-implementation
- Epic: EPIC-2026-04-13-investigate-april-11-12-aethericrift-history-and-next-steps
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-14T11:22:04Z
- Updated: 2026-04-26T11:39:24Z

## Objective
Investigate how to turn `CodegenRiftSpace` into the real post-capability room:
everything capability already has, plus the later codegen option, without
duplicating lower-object behavior on the command surface.

## Ticket Contract
- ENTRY_GATE: the AR room rename to `codegen` is landed and the user explicitly
  asked for an implementation investigation before building the codegen layer.
- EXECUTION_BOUNDARY: investigation and planning only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/command_system/codegen_command_system.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - codex/context_compass/tickets/tasks/2026-03-15_rift_dynamic_local_construction_task.md
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md
- EXIT_GATE: the ticket records what `CodegenRiftSpace` should inherit from
  capability now, what should stay room/viewer/command/workstation work, and
  what should be deferred to the later actual codegen-execution slice.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current room/viewer/
  workstation model is still too incomplete to define a clean pre-codegen
  implementation boundary.

## Scope Boundaries
- In scope:
  - current codegen room/runtime shape
  - capability parity requirements
  - viewer/command/workstation implications
  - codegen-later boundary
- Out of scope:
  - implementing codegen execution itself
  - lower Melder runtime refactors
  - unrelated ticket cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an investigation of how to
  implement `CodegenRiftSpace` now, with actual codegen deferred.

## Steps / Checklist
- [ ] Read current codegen/capability room and command surfaces.
- [ ] Read current viewer/workstation room contracts.
- [ ] Read the older dynamic-local-construction design lane and retained AR artifacts.
- [ ] Record what parity with capability means in current code.
- [ ] Record what belongs to the later actual codegen slice.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed implementation direction for `CodegenRiftSpace`
- explicit split between "capability parity now" and "codegen later"

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-14_investigate_codegen_rift_space_implementation_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: investigation drifts into implementing codegen or re-expanding command
  wrappers instead of preserving the "use bound objects their own way" design.
  Rollback: keep the analysis bounded to capability parity, room semantics, and
  deferred codegen boundary only.

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
- DATETIME: 2026-04-19T11:09:19Z
  TYPE: DECISION
  CLAIM: The target model is not a separate registered codeblock workflow and
    not a `CodegenCommandSystem` subclass over the existing command lineage.
    The user clarified that codegen should work over workstation-bound objects,
    create local objects/helpers from that context, bind those outputs back into
    the room, and then let the capability-style command surface consume those
    results in combination with later codegen. That means the clean shape is:
    - one direct/runtime command lineage for capability-style imperative work
    - one separate codegen lineage for governed local construction/execution
    - workstation bindings as the bridge between them
  EVIDENCE:
  - user_instruction: "CodegenCommandSystem cannot be a subclass of the CommandSystem"
  - user_instruction: "the same capability style command system should exist and then we should have our own codegen command system"
  - user_instruction: "the codegen would create objects that are consumed by the capability command system in combination with codegen"
  IMPACT: The strategy should pivot away from a codeblock registry API and
    toward a room-local `CodegenSystem` that executes over governed workspace
    bindings and exports local artifacts back into the workstation.
  NEXT: describe the dual-lineage room model, the workstation bridge, and the
    ACL/proxy strategy needed so codegen cannot bypass capability policy by
    touching raw runtime objects directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T11:09:19Z
  TYPE: FACT
  CLAIM: The live codegen ACL/profile layer and the retained codegen pipeline
    artifact already line up on the right conceptual split. The ACL side is
    operation-oriented (`query`, `resolve_existing`, `bind_existing`,
    `local_create`, `invoke_method`, `read_attribute`, `write_attribute`,
    `dynamic_access`, `mutation`, `contract_override`,
    `unsafe_reflection`, `dunder_access`) while the artifact defines the later
    AST/runtime pipeline (`parse -> structural validation -> symbol resolution
    -> lane classification -> governed execution -> audit`). That means the
    implementation strategy should be:
    1) compile a per-frame/per-room capability manifest from
       `CodegenProjection.compiled_access_surface` plus the typed codegen ACL
       config/profile/rulesets,
    2) run AST/lane validation against that manifest,
    3) execute through a room-local codegen system that mirrors the command
       system's ownership/gate/result-binding pattern.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:11-129
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/safe_profile.py:1-61
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/precision.py:1-53
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile.py:1-223
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:1-80
  - src/melder/aether/nexus/rift/command_system/command_system.py:14-35
  - src/melder/aether/nexus/rift/command_system/command_system.py:2161-2188
  - src/melder/aether/nexus/rift/command_system/command_system.py:2677-2721
  IMPACT: We do not need to guess at the codegen system boundary anymore. The
    missing object should be designed as a room-local consumer over compiled
    codegen ACL answers, with AST/lane governance above it and workstation
    result-binding below it.
  NEXT: summarize the concrete runtime object model and the phased strategy to
    the user, including where hooks should live.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T11:09:19Z
  TYPE: FACT
  CLAIM: The current repo already has the codegen substrate shells we would
    build on, but not the actual runtime consumer. `CodegenRiftSpace` exists,
    `CodegenCommandSystem` exists as a thin subclass, `CodegenProjection`
    exists as the codegen-shaped projection shell, and the ACL side already has
    typed codegen config/profile/ruleset objects. What does not exist yet is
    the real `codegen_system` object graph that consumes those projections and
    ACL answers to do intake, AST validation, lane classification, governed
    execution, hooks, and audit.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:1-87
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:1-20
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:1-80
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py:1-224
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile.py:1-223
  - src/melder\aether\nexus\acl\configurations\profiles\rules\frame_acl_ruleset.py:1-224
  - src/melder/aether/nexus/rift/codegen_system/__init__.py:1-1
  IMPACT: The strategy should not start by inventing ACL or projection storage.
    It should start by defining the missing `CodegenSystem` runtime object that
    composes the already-existing shells the same way `CommandSystem` composes
    `CommandProjection`.
  NEXT: inspect the command-system template and the retained codegen pipeline
    artifact to define the concrete missing runtime objects and seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T11:22:04Z
  TYPE: PLAN
  CLAIM: The next useful lane is not codegen execution yet. It is defining the
    pre-codegen implementation boundary for `CodegenRiftSpace`: what it should
    already inherit from capability, what room/viewer/workstation behavior it
    should have before codegen exists, and what must stay deferred to the later
    real codegen pipeline.
  EVIDENCE:
  - user_instruction: "remember it should have everything capability has and with the option of codegen"
  - user_instruction: "we'll build the codegen part last"
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:13-29
  - src/melder/aether/nexus/rift/rift_space/command_system/codegen_command_system.py:6-20
  IMPACT: We need one bounded implementation-investigation pass before new
    coding starts.
  NEXT: read the current codegen/capability room code, viewer/workstation
    surfaces, and the older dynamic-local-construction design notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T11:22:04Z
  TYPE: FACT
  CLAIM: `CodegenRiftSpace` already has capability parity at the current
    room/command layer. Both rooms are thin wrappers over `RiftSpace`, both use
    the generic viewer posture, and both compose a room-specific command class
    that currently preserves the same shared broad manual-runtime surface.
    So there is no separate "implement the capability command/viewer features
    for codegen room" tranche left in current code. That parity already exists.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:13-85
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:16-98
  - src/melder/aether/nexus/rift/rift_space/command_system/codegen_command_system.py:6-20
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:6-43
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:28-64
  IMPACT: The next implementation work should not be framed as "copy capability
    features into codegen room." The current room shell already does that.
  NEXT: isolate what the old dynamic/codegen design expected beyond this shared
    parity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T11:22:04Z
  TYPE: FACT
  CLAIM: The missing `CodegenRiftSpace` work is the old dynamic-local-
    construction slice, not more wrapper parity. The retained task/artifacts
    consistently expected the final room to:
    - surface the backing/root conduit as a workspace-facing tool
    - allow local helper/object/materialization against that substrate
    - bind resulting local outputs back into room targets
    - keep local construction distinct from canonical MutationResearch
    - later host the governed codegen pipeline over the workspace
    Current `CodegenRiftSpace` does none of that yet. It does not expose a
    `RiftConduit`, does not add local-construction APIs, and does not add a
    codegen validation/execution surface. It is just the renamed thin room
    wrapper today.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-03-15_rift_dynamic_local_construction_task.md:12-33
  - codex/context_compass/tickets/tasks/2026-03-15_rift_dynamic_local_construction_task.md:55-64
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:159-185
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:294-305
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:338-375
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:41-68
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:161-209
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:15-28
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:175-183
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:13-85
  IMPACT: The real pre-codegen implementation question is "how do we add room-
    local construction and workspace-side conduit exposure without jumping into
    the full codegen pipeline yet?"
  NEXT: inspect the existing workstation/viewer/command surfaces for where that
    local-construction and binding behavior could slot in without duplicating
    lower-object APIs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T11:22:04Z
  TYPE: FACT
  CLAIM: The existing generic room surfaces already give most of the non-
    codegen scaffolding needed for the eventual codegen room. `RiftSpace`
    already owns:
    - attached viewer
    - selected-target state
    - workstation
    - command system
    - event queue/config
    `Workstation` already supports strong/weak bindings, active target
    selection, and rebinding call results. The viewer already projects ACL-
    filtered frame/conduit/spell targets. The command system already resolves
    selected targets, runtime objects, and optional result binding. That means
    the likely missing pre-codegen slice is not a new viewer or workstation.
    It is a way for the codegen room to deliberately expose one local
    construction tool/surface over the backing conduit and bind the resulting
    outputs into the already-existing workstation/target model.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:28-64
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:137-160
  - src/melder/aether/nexus/rift/rift_space/workstation.py:15-40
  - src/melder/aether/nexus/rift/rift_space/workstation.py:343-372
  - src/melder/aether/nexus/rift/rift_space/workstation.py:501-578
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3270-3280
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1528-1647
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1676-1730
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1897-1905
  IMPACT: The next codegen-room implementation slice can stay narrow:
    add room-specific local construction/conduit exposure over the existing
    viewer/workstation/command scaffolding, and defer actual codegen execution.
  NEXT: summarize that narrow implementation direction so we can decide whether
    to stage it as the next task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T23:25:55Z
  TYPE: FACT
  CLAIM: The recent artifact stack now makes the lane split explicit. The
    April 12 capability artifact settles capability as the broad manual
    non-codegen room over either automatic or dynamic frames, while the older
    retained AR/codegen artifacts still define the next room's unique job:
    expose the backing conduit as a workspace-local construction substrate,
    bind local outputs back into `RiftSpace`, and only later add the governed
    Python codegen pipeline (`CapabilityManifest` + `ExecutionContext` +
    AST/lane validation) on top.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md:30-61
  - codex/context_compass/tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md:83-92
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:68-79
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:333-359
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:50-59
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:262-291
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:15-28
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:101-112
  IMPACT: The next work should not reopen the settled capability semantics or
    jump straight into `exec()` governance. The clean next slice is the
    pre-codegen workspace/conduit construction layer for the codegen room.
  NEXT: summarize that current artifact-backed direction to the user and decide
    whether to stage the pre-codegen construction slice as the next task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-15T01:08:33Z
  TYPE: FACT
  CLAIM: The base command layer confirms the ownership split directly.
    `CommandSystem` is room-local and explicitly says it is owned by one
    `RiftSpace`, while it only borrows the workstation reference and must not
    cleanup the room or workstation itself. `RiftSpace` creates the workstation
    first, passes it into the command system, and later cleans both children.
    So the workstation does not live inside the command system in the ownership
    sense; the command system is only one consumer of the room-owned
    workstation.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:12-33
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:45-90
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:150-157
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:162-202
  - src/melder/aether/nexus/rift/rift_space/workstation.py:12-44
  IMPACT: Codegen should layer over the room-owned workstation namespace, but
    the workstation itself should not be re-owned by the command system or
    collapsed into it.
  NEXT: explain that ownership split clearly to the user and use it as the
    baseline for the next codegen-room design step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-15T01:17:18Z
  TYPE: FACT
  CLAIM: The current filesystem/layout is mid-transition, not finished. A new
    `rift/codegen_system/` package exists, but it is still empty except for
    `__init__.py`. The live room classes and base room still import the
    command layer from `rift/command_system`, and the room extension seam is
    still `_create_command_system()` plus optional viewer wrapping through
    `attach_frame_viewer(...)`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:9-12
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:157-157
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:325-343
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:7-10
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:81-108
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:3-6
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:88-94
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:3-6
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:75-81
  - src/melder/aether/nexus/rift/codegen_system/__init__.py:1-1
  IMPACT: The next design step should not pretend a codegen-system stack
    already exists. We need to define that object model first, then wire
    `CodegenRiftSpace` to compose it intentionally.
  NEXT: propose the `CodegenSystem` object model and how `CodegenRiftSpace`
    should own it beside the existing workstation/command/viewer composition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-16T23:00:05Z
  TYPE: FACT
  CLAIM: Rift is currently sync-biased end to end. There are no `await` or
    `asyncio` paths under `src/melder/aether/nexus/rift`, and the room-facing
    execution seams call methods/targets directly. If an async method leaks
    into the current command/workstation/viewer surface, Rift will not await
    it; it will just return the coroutine object, and any bind-back path would
    bind that coroutine object as-is. The only explicit async-aware utility in
    current Melder is `Package`, which documents coroutine-function support but
    also says it does not auto-await.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:1510-1577
  - src/melder/aether/nexus/rift/rift_space/workstation.py:473-521
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2669-2690
  - src/melder/utilities/helpers/package.py:16-33
  - src/melder/utilities/helpers/package.py:471-494
  IMPACT: Async-capable underlying objects are a real future integration issue,
    but there is no hidden async execution model in Rift today. Any async
    support will require an explicit boundary/design cut instead of assuming
    current room execution paths already handle it.
  NEXT: explain the current sync-only Rift contract to the user and decide
    whether async-capable methods should be blocked, wrapped, or explicitly
    handed off outside Rift later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-16T23:34:57Z
  TYPE: FACT
  CLAIM: The Rift layer currently mixes two command/access strata. `Rift`
    itself still exposes a thin set of direct conduit/runtime convenience
    methods (`get_conduit_cloud`, `list_conduit_ids`, `get_conduit_by_id`,
    etc.) and also owns frame-targeting/viewer attachment responsibilities,
    while `RiftSpace` owns the actual room-local command/viewer/workstation
    composition model. So commands ended up "in Rift" historically because
    `Rift` still acts as a session-level facade over targeted frame/conduit
    access, but the newer room model has already moved the richer mediated
    surface down into `RiftSpace`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:433-611
  - src/melder/aether/nexus/rift/rift.py:614-895
  - src/melder/aether/nexus/rift/rift.py:1027-1126
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:19-61
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:133-157
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:18-30
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:16-30
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:14-25
  IMPACT: The layering is not purely clean yet. The strategic direction is
    room-owned command/viewer/workstation behavior, but `Rift` still carries an
    older convenience-facade layer for direct targeted runtime access.
  NEXT: explain that mixed layering plainly to the user and use it to decide
    whether more command/runtime convenience should stay on `Rift` or continue
    moving downward into `RiftSpace` and its room-owned systems.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the implementation investigation for `CodegenRiftSpace` before
the later actual codegen-execution slice.
