# Task: Add Command-Level Meld Helpers
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the command-level meld-helper slice after shared activation helpers and the final static policy correction both landed and validated.

## Metadata
- Task ID: TASK-2026-04-12-add-command-level-meld-helpers
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T21:19:28Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Add shared command-level spell activation helpers over `Conduit.meld(...)` and
`Conduit.meld_existing_spell(...)`, while denying the create-path helper in
static rooms.

## Ticket Contract
- ENTRY_GATE: capability room/runtime and shared command-surface slices are
  landed and green, and the user explicitly asked to keep building capability.
- EXECUTION_BOUNDARY: base/static command system methods, shared command
  protocol surface, focused tests, patch docs, and board/artifact sync only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/conduit/conduit.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: shared command-level meld helpers exist, static denies the
  create-path helper, and the focused test ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if command-level meld needs a
  broader command/runtime redesign or if the helper contract is ambiguous.

## Scope Boundaries
- In scope:
  - shared command helpers for `meld(...)` and `meld_existing_spell(...)`
  - static denial for the create-path helper
  - protocol/introspection updates
  - focused unit/runtime tests
- Out of scope:
  - codegen helpers
  - capability integration harness expansion
  - viewer redesign
  - broader runtime API reshaping

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next missing broad-manual capability seam is explicit
  command-level spell activation instead of more topology-only surface area.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Add shared `meld(...)` and `meld_existing_spell(...)` to `CommandSystem`.
- [x] Deny `meld(...)` in `StaticCommandSystem`.
- [x] Update shared command protocol/introspection surface.
- [x] Add focused tests for capability allow and static deny behavior.
- [x] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- shared command-level meld helpers
- explicit static deny behavior for create-path spell activation
- focused test coverage for the new command contract

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
- src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`
  - `python -m pytest -q tests/integration/melder/aether/rift`

## Risks / Rollback Notes
- Risk: command-level spell activation duplicates or muddies the existing spell
  getter contract.
  Rollback: keep the current spell-object getters unchanged and use explicit
  helper names for activation.
- Risk: static behavior becomes uneven if create-path activation is not denied.
  Rollback: keep a room-owned deny override and test it directly.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
  - system_docs/patches/active/command_level_meld_helpers/architecture_patch.md
  - system_docs/patches/active/command_level_meld_helpers/component_patch_command_system.md
  - system_docs/patches/active/command_level_meld_helpers/component_patch_static_command_system.md
  - system_docs/patches/active/command_level_meld_helpers/component_patch_interfaces.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the command-level meld helper behavior is merged
  into canonical docs or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T21:19:28Z
  TYPE: PLAN
  CLAIM: The next missing capability seam is explicit spell activation through
    the shared command surface. The room can already fetch spell metadata
    objects and perform topology operations, but there is no direct
    command-level helper for "create/reuse this spell" or "reuse only if it is
    already live". The lower runtime seam already exists on `Conduit` via
    `meld(...)` and `meld_existing_spell(...)`, so the clean move is a shared
    command helper over that seam with an explicit static deny on the
    create-path helper.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2441-2577
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:573-707
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md:107-149
  IMPACT: Capability can get a more complete manual runtime room without
    changing the meaning of the existing spell-object getters.
  NEXT: stage patch docs and route the task, then add the new shared helper
    methods and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:25:38Z
  TYPE: FACT
  CLAIM: The command-surface parity audit shows three real drift points.
    First, the staged task/patch docs were using `meld_spell(...)` instead of
    the real lower API name `meld(...)`; that doc drift is now fixed. Second,
    the current shared command surface already drifts from lower owner naming
    in `link_conduits(...)`, which wraps `Conduit.link(...)`, and
    `get_spell_object_by_*`, which wraps `Conduit.get_spell_by_*` but adds the
    `object` suffix. Third, some shared command names match lower owners but
    not their semantics exactly: command conduit list/count/id-name helpers are
    ACL/publication-filtered, and `CommandSystem.get_conduit_by_id(...)`
    includes lesser-conduit fallback while `Rift`/`Aether` root lookups do not.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:339-393
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:635-707
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:735-1076
  - src/melder/aether/conduit/conduit.py:1421-1421
  - src/melder/aether/conduit/conduit.py:1593-1639
  - src/melder/aether/conduit/conduit.py:2303-2341
  - src/melder/aether/conduit/conduit.py:2440-2557
  - src/melder/aether/conduit/conduit.py:2794-2977
  - src/melder/aether/nexus/rift/rift.py:408-568
  IMPACT: If we continue the next helper slice, we should mirror Melder names
    where the command layer is directly wrapping a lower runtime seam, and we
    should be explicit when a command method is intentionally a filtered or
    room-mediated variant instead of a parity facade.
  NEXT: align the next spell-activation helper slice to the real lower names
    `meld(...)` and `meld_existing_spell(...)`, and decide whether
    `link_conduits(...)` should be renamed to `link(...)` for parity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:36:35Z
  TYPE: FACT
  CLAIM: The shared command-level activation helpers are now landed on the
    corrected names. Base `CommandSystem` now exposes `meld(...)` and
    `meld_existing_spell(...)` as direct wrappers over the existing conduit
    runtime seam, and `StaticCommandSystem` denies both helpers so static rooms
    cannot bypass the published live-only spell surface through raw conduit
    activation.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1067-1164
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1262-1278
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:63-86
  - src/melder/utilities/interfaces/interfaces.py:7057-7088
  IMPACT: Capability/dynamic now have a more complete manual runtime surface
    on the same names as the lower Melder API, while static stays closed to
    direct activation.
  NEXT: record the green validation result and then wire these helpers into the
    capability integration harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:36:35Z
  TYPE: MEASURE
  CLAIM: The command-level meld-helper slice is green on both the focused
    unit/runtime ring and the full shared `rift/` integration folder.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 123 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 180 passed
  IMPACT: The helper slice is stable enough to return for review and then move
    the same semantics into the capability integration harness.
  NEXT: extend the capability JSON harness to cover `meld(...)` and
    `meld_existing_spell(...)`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T22:49:00Z
  TYPE: FACT
  CLAIM: Two policy drifts remain in the static command surface relative to the
    intended room story. First, static still exposes `list_clusters(...)` even
    though the room should not surface cluster topology. Second, static denies
    `meld_existing_spell(...)` even though that is the non-creating spell
    activation path it actually wants to allow. The correct policy is:
    - deny `list_clusters(...)`
    - deny `meld(...)`
    - allow `meld_existing_spell(...)`
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:39-78
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:492-509
  - user_direction: "static does not need access to list_clusters"
  - user_direction: "why would you block meld_existing_spell when it should be enabled"
  IMPACT: This is a targeted policy correction to the existing helper slice, not
    a new capability feature lane.
  NEXT: patch the static command policy and the focused tests, then rerun the
    unit/runtime ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T22:49:55Z
  TYPE: MEASURE
  CLAIM: The static command-policy correction is green on both the focused
    unit/runtime ring and the shared `rift/` integration folder. Static now:
    - denies `list_clusters(...)`
    - denies `meld(...)`
    - allows `meld_existing_spell(...)`
    and `list_supported_command_methods()` matches that policy.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:39-86
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:492-509
  - tests/unit/melder/aether/test_nexus.py:3046-3128
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 128 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 220 passed
  IMPACT: The static vs capability split now matches the intended room story
    on those two command seams instead of drifting under the shared surface.
  NEXT: return to the next genuinely new capability/runtime seam instead of
    more static policy cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the next capability-command expansion: explicit command-level
spell activation helpers over the existing conduit meld seams. The helper
slice is now landed and green.
