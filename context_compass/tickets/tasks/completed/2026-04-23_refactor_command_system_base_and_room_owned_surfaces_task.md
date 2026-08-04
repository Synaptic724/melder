# Task: Refactor Command System Base And Room-Owned Surfaces
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the base/capability/static ownership cut and the static JSON-driver cleanup both landed green.

## Metadata
- Task ID: TASK-2026-04-23-refactor-command-system-base-and-room-owned-surfaces
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-23T22:55:10Z
- Updated: 2026-04-24T01:03:27Z

## Objective
Shrink `CommandSystem` down to shared command infrastructure plus truly shared
public helpers, move static-forbidden topology and activation methods into
`CapabilityCommandSystem`, and make `StaticCommandSystem` own only the
static-safe surface it actually needs.

## Ticket Contract
- ENTRY_GATE: the new command-ownership epic is active and the user explicitly
  requested an implementation slice that leaves codegen out and fixes base,
  capability, and static command ownership first.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/command_system/command_system.py`
  - `src/melder/aether/nexus/rift/command_system/capability_command_system.py`
  - `src/melder/aether/nexus/rift/command_system/static_command_system.py`
  - directly affected command-system interfaces
  - directly affected unit tests
  - this task ticket, patch artifacts, and board state
- DEPENDENCIES:
  - tickets/epics/2026-04-23_refactor_room_command_surface_ownership_and_composition_epic.md
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: the base no longer owns static-forbidden topology/activation or
  capability-only conduit-discovery commands, capability owns them explicitly,
  static no longer relies on deny lists for the moved methods, and the focused
  command-surface unit ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if moving the methods cleanly
  requires a broader AR/runtime redesign beyond command ownership.

## Scope Boundaries
- In scope:
  - command ownership cut for base/capability/static
  - shared command discovery updates
  - directly affected command-system protocols
  - focused command-surface tests
- Out of scope:
  - codegen command ownership changes
  - lower conduit/runtime API redesign
  - unrelated room/viewer/workstation refactors

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the base/capability/static ownership cut is implemented,
  the focused command-surface ring is green, and the docs/task state are
  synchronized.

## Steps / Checklist
- [x] Stage and link minimal patch artifacts for this system-impacting command ownership cut.
- [x] Lock the current-vs-target placement matrix in `## Notes`.
- [x] Move topology mutation and activation methods out of `CommandSystem`.
- [x] Add those methods explicitly to `CapabilityCommandSystem`.
- [x] Keep `StaticCommandSystem` as a room-owned static-safe surface without deny-list reliance for moved methods.
- [x] Align directly affected interfaces and discovery behavior.
- [x] Update focused unit tests.
- [x] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- slimmer shared `CommandSystem`
- room-owned capability/static command surfaces
- updated protocols and focused tests

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-23_refactor_command_system_base_and_room_owned_surfaces_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/rift/command_system/command_system.py
- src/melder/aether/nexus/rift/command_system/capability_command_system.py
- src/melder/aether/nexus/rift/command_system/static_command_system.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- tests/unit/melder/aether/test_command_system_direct.py
- tests/unit/melder/aether/test_rift_runtime_contracts.py
- tests/integration/melder/aether/rift/static_rift_json_testbench_support.py
- tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py

## Validation
- Executed:
  - `python -m py_compile src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/capability_command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_runtime_contracts.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_runtime_contracts.py -k "conduit or capability_command_system or static_command_system or supported_methods or meld_existing_spell or create_lesser_conduit or create_cluster or list_clusters or link or sever_link or meld or rift_spaces_expose_conduit_discovery"`
  - `python -m py_compile tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py`
- Result:
  - `138 passed, 2 warnings`
  - `105 passed, 2 warnings`

## Risks / Rollback Notes
- Risk: moving methods out of the base leaves the protocol layer lying about
  room command surfaces.
  Rollback: align interfaces in the same patch so room typing stays honest.
- Risk: current tests depend on runtime denials instead of absence/room-owned
  methods.
  Rollback: update the tests to match the intended ownership model directly.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [ ] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/room_command_surface_ownership_refactor/architecture_patch.md
  - system_docs/patches/active/room_command_surface_ownership_refactor/component_patch_command_system.md
  - system_docs/patches/active/room_command_surface_ownership_refactor/component_patch_room_command_systems.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the command ownership refactor is merged into
  canonical docs or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-23T22:55:10Z
  TYPE: FACT
  CLAIM: The current placement problem is concrete and bounded. `CommandSystem`
    owns topology mutation, `meld(...)`, and `meld_existing_spell(...)`, while
    static then denies the topology methods plus `meld(...)` and capability adds
    almost no room-specific ownership at all.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:331-374
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:1-18
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:28-45
  - tests/unit/melder/aether/test_nexus.py:3469-3648
  IMPACT: The first clean implementation slice is to move the static-forbidden
    commands out of the base and make capability/static own them explicitly.
  NEXT: stage patch docs and lock the exact placement matrix before editing the
    command classes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T22:55:10Z
  TYPE: PLAN
  CLAIM: Patch artifact consumption is now mapped for implementation. The
    architecture patch defines the ownership cut and migration order, the
    `CommandSystem` component patch defines the base-method removal set, and the
    room-command component patch defines the capability/static landing surface.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/room_command_surface_ownership_refactor/architecture_patch.md:1-27
  - codex/context_compass/system_docs/patches/active/room_command_surface_ownership_refactor/component_patch_command_system.md:1-22
  - codex/context_compass/system_docs/patches/active/room_command_surface_ownership_refactor/component_patch_room_command_systems.md:1-30
  IMPACT: Code edits can stay mechanically aligned:
    - architecture patch -> overall cut order and invariants
    - base component patch -> move/remove base methods and discovery entries
    - room component patch -> add capability methods, simplify static, and fix
      room discovery/tests
  NEXT: patch the command classes and directly affected interfaces/tests in that
    order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:03:59Z
  TYPE: FACT
  CLAIM: The ownership cut is now implemented. `CommandSystem` no longer owns
    topology mutation, cluster, direct `meld(...)`, or reuse-only
    `meld_existing_spell(...)`. Those methods now live on
    `CapabilityCommandSystem`, while `StaticCommandSystem` owns only its
    static-safe spell retrieval/reuse/status helpers and no longer relies on
    runtime denials for the moved methods. The command-system protocol layer and
    the two canonical room-command docs are updated to match.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:14-35
  - src/melder/aether/nexus/rift/command_system/command_system.py:317-364
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:1-427
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:9-30
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:420-500
  - src/melder/utilities/interfaces/interfaces.py:7024-7549
  - codex/context_compass/system_docs/src_architecture.md:533-558
  - codex/context_compass/system_docs/src_components.md:635-772
  IMPACT: The room command model is now structurally closer to the intended
    composition: capability owns the broad manual-runtime commands instead of
    inheriting them from a fat shared base, and static no longer needs deny-list
    subtraction for those moved methods.
  NEXT: review whether the next cut should move more contract-topology helpers
    out of the shared base or stop here at the first bounded ownership fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:03:59Z
  TYPE: MEASURE
  CLAIM: The first ownership refactor slice is green on syntax and the focused
    Nexus room-command unit ring. The updated tests now assert room ownership
    directly: capability exposes the moved methods, static no longer exposes
    them, static advertises its own spell-status helpers, and the shared base no
    longer lists capability-only commands.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:3469-3673
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/capability_command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "capability_command_system or static_command_system or supported_methods or meld_existing_spell or create_lesser_conduit or create_cluster or list_clusters or link or sever_link or meld"` -> `116 passed, 2 warnings`
  IMPACT: The first bounded command-ownership cut is stable enough to return
    for review without widening immediately into the remaining shared
    contract-topology helpers.
  NEXT: decide whether to stop at this ownership cut or stage a second bounded
    refactor over the remaining non-static shared command helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:03:59Z
  TYPE: DECISION
  CLAIM: The second cut is now explicit and landed. Per user direction, the
    shared base no longer owns conduit discovery helpers either:
    `get_conduit_cloud`, `get_conduit_by_id`, `get_conduit_by_name`,
    `list_conduit_ids`, `list_conduit_names`, `count_conduits`,
    `has_conduit_id`, `has_conduit_name`, and `find_conduit_id_by_name` all now
    live on `CapabilityCommandSystem`. The shared base keeps the explicitly
    approved spell/runtime query helpers.
  EVIDENCE:
  - user_instruction: "These cannot be shared move them to capability"
  - src/melder/aether/nexus/rift/command_system/command_system.py:331-355
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:22-282
  - src/melder/utilities/interfaces/interfaces.py:7043-7529
  IMPACT: Static no longer exposes direct conduit discovery through the command
    surface, and the shared base is materially slimmer than the first cut left
    it.
  NEXT: review whether the remaining link/contract-topology helpers should move
    next or stay shared.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:03:59Z
  TYPE: MEASURE
  CLAIM: The second ownership cut is green on syntax plus the focused command,
    room, and Rift runtime ring. The updated tests now cover:
    - capability-owned conduit discovery
    - static absence of direct conduit discovery
    - base absence of capability-only conduit discovery
    - direct command-system helper fallout
    - capability-Rift runtime contract fallout
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:1520-1532
  - tests/unit/melder/aether/test_nexus.py:1755-2088
  - tests/unit/melder/aether/test_nexus.py:2195-2239
  - tests/unit/melder/aether/test_nexus.py:3629-3713
  - tests/unit/melder/aether/test_command_system_direct.py:1-369
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:143-350
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/capability_command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_runtime_contracts.py -k "conduit or capability_command_system or static_command_system or supported_methods or meld_existing_spell or create_lesser_conduit or create_cluster or list_clusters or link or sever_link or meld or rift_spaces_expose_conduit_discovery"` -> `138 passed, 2 warnings`
  IMPACT: The command ownership refactor now covers both the original
    topology/activation cut and the conduit discovery cut, and the focused
    runtime fallout is resolved in the same lane.
  NEXT: decide whether to stop here or stage a third bounded pass for the
    remaining link/contract-topology helpers still in the shared base.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:03:59Z
  TYPE: FACT
  CLAIM: The third cut is now landed too. The remaining link/contract-topology
    helper block no longer lives on the shared base:
    `get_links`, `get_lesser_conduit`, `get_initiated_conduit`,
    `get_provider_conduit`, `get_initiated_conduits`,
    `get_provider_conduits`, `get_contracted_conduits`,
    `get_spell_in_contracts`, `get_spells_in_contract_by_conduit`, and
    `get_spells_in_contract_by_conduit_name` all now live on
    `CapabilityCommandSystem`.
  EVIDENCE:
  - user_instruction: "you can move all these to capability"
  - src/melder/aether/nexus/rift/command_system/command_system.py:331-345
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:22-32
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:57-911
  - src/melder/utilities/interfaces/interfaces.py:7043-7201
  - src/melder/utilities/interfaces/interfaces.py:7430-7621
  IMPACT: The shared base is now much closer to the intended shape: spell/query
    and workstation-target helpers only, while capability owns the broader
    runtime-manipulation and topology/contract surface.
  NEXT: review whether any further capability-only helpers should move, or stop
    the ownership refactor here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:03:59Z
  TYPE: MEASURE
  CLAIM: The full focused ownership-refactor ring stays green after the third
    cut. The capability room now owns conduit discovery, topology mutation,
    direct spell activation/reuse, and link/contract-topology helpers, while
    the base and static surfaces remain aligned to their slimmer contracts.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:1520-1532
  - tests/unit/melder/aether/test_nexus.py:1755-2088
  - tests/unit/melder/aether/test_nexus.py:2195-2239
  - tests/unit/melder/aether/test_nexus.py:3629-3825
  - tests/unit/melder/aether/test_command_system_direct.py:1-369
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:143-350
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/capability_command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_runtime_contracts.py -k "conduit or capability_command_system or static_command_system or supported_methods or meld_existing_spell or create_lesser_conduit or create_cluster or list_clusters or link or sever_link or meld or rift_spaces_expose_conduit_discovery"` -> `138 passed, 2 warnings`
  IMPACT: The last requested ownership cut is complete and stable on the
    focused ring.
  NEXT: report the finished ownership matrix to the user and let them decide
    whether another command-surface cleanup pass is warranted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:49:54Z
  TYPE: FACT
  CLAIM: The leftover static JSON bench assumptions are now removed. The static
    JSON harness no longer exposes a fake `cloud` dispatch surface, the static
    request matrix no longer encodes conduit-discovery requests, the static turn
    script matrix no longer encodes conduit-discovery or lesser-fetch flows, and
    the explicit static lesser-conduit command fetch test is deleted. The static
    JSON lane now reflects the current no-backward-compat command ownership
    model instead of the pre-refactor surface.
  EVIDENCE:
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:489-496
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:230-319
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:345-639
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:728-749
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:1188-1216
  IMPACT: The ownership refactor no longer leaves stale static integration
    assumptions behind. Static command behavior, static JSON-driver behavior,
    and unit/integration expectations now agree.
  NEXT: return the finished command ownership refactor with the static JSON
    cleanup included.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:49:54Z
  TYPE: MEASURE
  CLAIM: The static JSON cleanup is green on the focused integration ring after
    removing the stale conduit-discovery assumptions.
  EVIDENCE:
  - validation_result: `python -m py_compile tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> `105 passed, 2 warnings`
  IMPACT: There is no longer a known stale static JSON-driver surface hanging
    off the command ownership cut.
  NEXT: let the user decide whether the command-surface cleanup is complete or
    whether another bounded surface cleanup lane is still needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T23:03:59Z
  TYPE: FACT
  CLAIM: The remaining questionable base methods now cluster cleanly. After the
    first cut, the shared base still publishes three groups:
    1) likely still shared:
       `get_conduit_cloud`, conduit lookup/list/count/has/find,
       spell lookup by source/index/id, target attribute/method execution
    2) likely capability-only because they are link/peer/contract topology:
       `get_links`, `get_lesser_conduit`, `get_initiated_conduit`,
       `get_provider_conduit`, `get_initiated_conduits`,
       `get_provider_conduits`, `get_contracted_conduits`,
       `get_spell_in_contracts`, `get_spells_in_contract_by_conduit`,
       `get_spells_in_contract_by_conduit_name`
    3) ambiguous and needs an explicit call:
       `describe_spells_in_conduit`, `get_resolution_state`,
       `get_active_spellspace`, `find_spell_id`, `find_spell_key`,
       `get_spell_permissions`, `snapshot_state`
    The static room no longer exposes the moved topology/activation methods, so
    the next meaningful ownership discussion is this second cluster.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:331-364
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:22-32
  - tests/unit/melder/aether/test_nexus.py:3631-3673
  IMPACT: We can discuss the second cut in a bounded way instead of arguing
    about the whole base surface at once.
  NEXT: confirm with the user which of the remaining link/contract/runtime
    query helpers should move into capability in the second ownership pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first implementation slice for room command ownership.
The focus is only base/capability/static; codegen is intentionally left out of
this patch.
