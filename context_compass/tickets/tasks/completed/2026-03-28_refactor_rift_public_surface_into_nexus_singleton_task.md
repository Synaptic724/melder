# Task: Refactor Rift Public Surface Into Nexus Singleton

## Metadata
- Task ID: TASK-2026-03-28-refactor-rift-public-surface-into-nexus-singleton
- Story: STORY-2026-03-16-aethericrift-system-bootstrap
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-28T22:47:05Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Replace the current public ARS-facing model with a public `Nexus` singleton
that owns Rift registry/config/lifecycle state, hides `Aether` from normal
Rift usage, and removes the now-unnecessary separate `AethericRiftState`
concept from the public runtime design.

## Ticket Contract
- ENTRY_GATE: the ARS governance surface is locked well enough that the next
  slice can move downward into the public-root/runtime-object model, and the
  user has explicitly approved the `Nexus` singleton direction.
- EXECUTION_BOUNDARY: Nexus/Rift public-surface refactor only across the AR
  runtime subtree, touched interfaces/tests, and the active AR patch docs.
- DEPENDENCIES:
  - TASK-2026-03-22-implement-aethericrift-system-configuration-governance
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/
  - src/melder/aether/aether.py
  - src/melder/aether/aetheric_rift_system/
- EXIT_GATE: `Nexus` exists as the public singleton root, `Aether` no longer
  facades Rift operations publicly, Rift ownership/lifecycle are coherent, and
  the active docs/tests match the new model.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refactor forces
  workstation/workspace semantics or persistent state-record machinery that the
  user has not approved.

## Scope Boundaries
- In scope:
  - introduce `Nexus` / `NexusConfiguration` naming and singleton behavior
  - keep `Aether` as hidden substrate host for the hosted Nexus instance
  - remove the need for a separate public `RiftState` object
  - simplify `Rift` so it owns its own runtime/config/frame-assignment state
  - update the AR patch docs and focused tests to the new public model
- Out of scope:
  - workstation/workspace implementation beyond owned-field wiring
  - broad non-AR renames across unrelated Melder code
  - MutationResearch or CommandOps changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the `nexus_frame_*` terminology pass is now implemented
  and syntax-clean, so the Nexus slice is back in review.

## Steps / Checklist
- [x] Add patch artifacts describing the Nexus singleton/public-surface model.
- [x] Update story/task routing so this refactor is the active AR lane.
- [x] Refactor AR naming/public entrypoint from hosted ARS facade to `Nexus`.
- [x] Remove the separate public `AethericRiftState` model and fold required
      live state into `Rift`.
- [x] Keep `Aether` as the hidden substrate host that privately creates the
      inert Nexus singleton at boot.
- [x] Update interfaces, focused tests, and touched docs/docstrings.
- [x] Run syntax validation on touched files.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Public `Nexus` singleton root
- Simplified public `Rift` model without separate public state object
- Updated AR patch docs and focused tests

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/aether/aetheric_rift_system/
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_aether.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/system_docs/patches/active/nexus_singleton_public_surface/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md
- codex/context_compass/tickets/stories/2026-03-16_aethericrift_system_bootstrap_story.md

## Validation
- Not run.
- Planned validation:
  - syntax compile of touched AR/Nexus files and tests
  - targeted pytest for focused AR/Nexus tests if `pytest` is available

## Risks / Rollback Notes
- Risk: public renaming leaves behind a split model where both `Aether` facade
  methods and `Nexus` public methods remain active.
  Rollback: keep one public root only and push all substrate access back behind
  `Nexus`.
- Risk: removing `RiftState` forces hidden persistence requirements we do not
  actually need yet.
  Rollback: keep only the live `Rift` state and reintroduce a private record
  object later if true persistence/rehydration appears.

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
  - system_docs/patches/active/nexus_singleton_public_surface/architecture_patch.md
  - system_docs/patches/active/nexus_singleton_public_surface/component_patch_nexus.md
  - system_docs/patches/active/nexus_singleton_public_surface/component_patch_rift.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain while the Nexus singleton/public-surface refactor is
  active or until merged into canonical AR docs

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-31T00:06:59Z
  TYPE: FACT
  CLAIM: The AR target-frame eligibility policy is now implemented in `Nexus`
    and validated in the focused Nexus unit surface. `Nexus` now treats AR as a
    Melder-frame attachment policy instead of just a target-frame name policy.
    For any AR attachment, the target frame must have a bound Melder
    `Configuration` and `rift_enabled=True`. Dynamic AR additionally
    requires `ai_native_enabled=True` and `system_state == dynamic`. Static AR
    remains allowed against an automatic frame when AI profiles are enabled. A
    TODO note was also added in `Rift` documenting that future Rift-owned
    Melder frames for local conduit hosting should default to the most
    permissive AR posture (`rift_enabled=True`,
    `ai_native_enabled=True`, `system_state=dynamic`).
  EVIDENCE:
  - src/melder\aether\nexus\nexus.py:941-1112
  - src/melder\aether\nexus\rift\rift.py:18-41
  - tests\unit\melder\aether\test_nexus.py:17-53
  - tests\unit\melder\aether\test_nexus.py:391-515
  - command:python -m pytest -q tests\unit\melder\aether\test_nexus.py
  IMPACT: AR frame attachment now respects Melder runtime capability posture
    instead of blindly attaching to any named frame. This gives static vs
    dynamic AR a real substrate eligibility rule and prevents dynamic AR from
    attaching to frames that cannot actually support the richer mode.
  NEXT: keep the Nexus task in review and use this policy as the baseline when
    we define the top-side workspace/context contract next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-31T00:06:59Z
  TYPE: FACT
  CLAIM: The first AR frame-eligibility test run exposed one immediate drift in
    the focused Nexus unit surface. The new policy correctly requires a bound
    Melder `Configuration` on the target frame, but the existing `test_nexus.py`
    fixtures still treated target frames like bare names with no attached frame
    configuration. That means the current failures are a test-fixture contract
    mismatch, not evidence that the runtime should allow unconfigured frames
    back in.
  EVIDENCE:
  - src/melder\aether\nexus\nexus.py:941-1073
  - tests\unit\melder\aether\test_nexus.py:17-34
  - command:python -m pytest -q tests\unit\melder\aether\test_nexus.py
  IMPACT: The focused Nexus tests need to bind eligible default/ops frame
    configurations explicitly before Rift creation, otherwise they are asserting
    a pre-policy target-frame model that no longer exists.
  NEXT: patch the test fixtures/helpers to bind default target-frame
    configurations up front, then rerun the focused Nexus test file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-31T00:06:59Z
  TYPE: FACT
  CLAIM: The lower-level object flow is now clear enough to identify the real
    missing top-side contract. The bind pipeline already creates a
    `SpellBindingProfile`, fingerprints it, and attaches it onto each `Spell`
    as `spell.profile`. The `Spell` object also accumulates later phase-owned
    runtime artifacts such as `resolution_profile`, `dependency_graph`,
    execution-plan metrics, mutation overlay state, and a back-reference to the
    owning `Spellbook`. `Conduit` then provides the live runtime surface that
    can resolve local and contracted spells through Meld/Creations/ConduitWard.
    What does not exist yet is a first-class AR-side “context contract” that
    gathers those lower-level spell/runtime artifacts into a stable, workspace-
    facing exposure model for `Rift` / `RiftSpace`.
  EVIDENCE:
  - src/melder\spellbook\bind\bind.py:198-266
  - src/melder\spellbook\spell.py:101-107
  - src/melder\spellbook\spell.py:265-298
  - src/melder\aether\conduit\conduit.py:3332-3513
  - src/melder\spellbook\spell_crafter\spell_crafter.py:235-261
  IMPACT: The next AR design step is not inventing more low-level runtime
    objects. It is defining one top-side workspace exposure/context contract
    that translates existing spell/profile/conduit truth into something the
    operator-facing `RiftSpace` can consume safely and consistently.
  NEXT: explain the current bind -> spell -> conduit flow to the user and then
    define the missing top-side context contract shape before implementing more
    workspace code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T01:04:00Z
  TYPE: FACT
  CLAIM: The bottom-up frame cleanup refactor made two older test expectations invalid. `Aether.cleanup_aetheric_frames()` now removes cleaned frames from the registry because each `AethericFrame.cleanup()` detaches itself upward, so the correct assertion is "captured frame object is cleaned and registry entry is gone," not "cleaned frame still exists in `_aetheric_frames`." Likewise, `Nexus.remove_rift(...)` cleans the Rift object, so tests must snapshot `rift.id` and `default_nexus_frame_name` before removal instead of reading cleaned properties afterward. The live unit test file was also renamed from the stale public-surface name to `tests/unit/melder/aether/test_nexus.py`.
  EVIDENCE:
  - src/melder\aether\aether.py:260-272
  - src/melder\aether\nexus\rift\rift.py:149-189
  - tests\integration\melder\aether\test_aether_integration_core.py:221-250
  - tests\unit\melder\aether\test_nexus.py:102-124
  - tests\unit\melder\aether\test_nexus.py:308-329
  - command:python -m pytest -q tests\integration\melder\aether\test_aether_integration_core.py tests\unit\melder\aether\test_nexus.py
  IMPACT: The Nexus/Aether test surface now matches the actual runtime lifecycle instead of preserving pre-refactor assumptions that would have pushed the implementation back toward the old split cleanup model.
  NEXT: use `test_nexus.py` as the live unit test surface going forward and leave historical artifact/doc references on the old filename alone until a dedicated documentation cleanup pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T22:25:53Z
  TYPE: FACT
  CLAIM: The existing runtime logging pattern is already clear enough to reuse
    for later Rift/workspace codegen and event logging. `Aether` and `Conduit`
    both resolve a `SafeLogger` through `InitHelpers.resolve_safe_logger(...)`
    and then emit method-scoped structured log calls through that wrapper,
    which already knows how to pass through richer channel-style logging when
    present and stdlib logging otherwise. That means the right later move is
    not inventing a second logger stack for Rift/workspace events, but
    reusing `SafeLogger` and adding structured event/codegen payloads on top
    of that pattern.
  EVIDENCE:
  - src/melder/utilities/helpers/init_helpers.py:1-29
  - src/melder/utilities/logger/safe_logger.py:1-205
  - src/melder/aether/aether.py:43-82
  - src/melder/aether/conduit/conduit.py:72-98
  - src/melder/aether/conduit/conduit.py:138-139
  - src/melder/aether/conduit/conduit.py:511-525
  IMPACT: Future codegen/event logging for Rift/workspace should plug into the
    existing `SafeLogger` pattern and use structured event records rather than
    inventing a parallel logging abstraction.
  NEXT: when the logging slice is active, define one structured event/codegen
    record schema and emit it through `SafeLogger` from Rift/workspace/runtime
    event sources.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T21:34:11Z
  TYPE: FACT
  CLAIM: The three nexus-frame mode semantics are now real in the runtime.
    `Nexus` now holds the hidden `Aether` reference directly for nexus-frame
    realization and disposal, `Rift` now queries `Nexus` for nexus-frame
    access instead of realizing nexus frames locally, `shared` now returns the
    one shared frame to any Rift, `one_per_workspace` now rejects access to any
    other Rift's private frame, and `indexed` now behaves as explicit
    shared-by-name access with separate create-vs-get paths. The remaining
    placeholder is the later eventstream: `Rift.on_nexus_frame_disposed(...)`
    is still only a no-op hook until the workspace event queue is built.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:38-47
  - src/melder/aether/nexus/nexus.py:58-72
  - src/melder/aether/nexus/nexus.py:87-127
  - src/melder/aether/nexus/nexus.py:621-746
  - src/melder/aether/nexus/nexus.py:996-1078
  - src/melder/aether/nexus/rift/rift.py:475-520
  - tests/unit/melder/aether/test_aetheric_rift_system.py:281-388
  - tests/unit/melder/aether/test_aetheric_rift_system.py:391-430
  IMPACT: The old awkward split where Rift realized nexus frames and Nexus only
    stored records is gone. Indexed mode now has an actual access model instead
    of just numbered frame-name generation.
  NEXT: keep the slice in review, then either build indexed detach/default
    selection semantics further or move back down into workstation/workspace.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T21:34:11Z
  TYPE: MEASURE
  CLAIM: The shared/indexed/one-per-workspace access slice is syntax-clean in
    the touched runtime and focused Nexus tests. The stale local Rift
    realization helpers are gone, and the only remaining frame-disposal
    placeholder is the intentional `Rift.on_nexus_frame_disposed(...)` no-op
    hook for the later eventstream task.
  EVIDENCE:
  - command:.venv\Scripts\python.exe -m py_compile src\melder\utilities\interfaces\interfaces.py src\melder\aether\aether.py src\melder\aether\nexus\nexus.py src\melder\aether\nexus\rift\rift.py tests\unit\melder\aether\test_aetheric_rift_system.py
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern 'get_nexus_frame_object|dispose_nexus_frame|_nexus_frame_objects_by_name|cleanup_frame\('
  IMPACT: The mode-behavior refactor is mechanically stable enough for review.
    Remaining uncertainty is behavioral verification in a user-run pytest
    environment, not source-shape drift.
  NEXT: report the slice truthfully as `Not run.` for pytest and continue only
    after you pick the next lower-layer focus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T21:30:37Z
  TYPE: DECISION
  CLAIM: The mode semantics are now concrete enough to implement. Nexus-frame
    realization should move into `Nexus` itself, with `Rift` querying `Nexus`
    for frame access instead of realizing nexus frames locally. `shared`
    should return the single shared frame to any Rift, `one_per_workspace`
    should only ever return the calling Rift's private frame, and `indexed`
    should return or attach named existing indexed frames while still allowing
    explicit creation of new indexed frames. This turns indexed mode into
    "shared-by-name" rather than "everyone implicitly gets everything."
  EVIDENCE:
  - user_instruction: "a rift can just query the nexus and get a reference to it"
  - user_instruction: "if we're not in indexed mode you can only return your own"
  - user_instruction: "when we're in shared mode anyone can return the shared one"
  - src/melder/aether/nexus/nexus.py:371-439
  - src/melder/aether/nexus/nexus.py:543-892
  - src/melder/aether/nexus/nexus_frame_record.py:11-246
  - src/melder/aether/nexus/rift/rift.py:21-150
  IMPACT: The next patch can stop splitting nexus-frame ownership awkwardly
    across `Rift` and `Nexus`. It also gives indexed mode a real access model
    instead of only numbered frame-name generation.
  NEXT: move nexus-frame realization into `Nexus`, add Nexus/Rift accessors for
    shared/indexed/one-per-workspace retrieval and indexed creation, then cover
    the mode rules in focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T21:13:21Z
  TYPE: FACT
  CLAIM: One lower-layer gap is intentionally left unresolved after the
    bottom-up frame ownership cut: when a nexus-managed frame disappears, the
    frame/registry/record cleanup is now coherent, but the live `Rift`
    workspace side still has no explicit event model for "frame disposed" or
    "workspace backing frame disappeared". The current runtime can survive the
    disposal mechanically, but the later workstation/workspace layer still
    needs a proper event/deque design so agents can observe, react, and
    rebuild degraded workspace state instead of silently assuming the frame is
    still there.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:92-130
  - src/melder/aether/aether.py:176-244
  - src/melder/aether/nexus/nexus.py:586-614
  - src/melder/aether/nexus/rift/rift.py:521-541
  IMPACT: The ownership model is in better shape now, but the later
    workspace/runtime event semantics must be designed explicitly rather than
    improvised during workstation work.
  NEXT: create a backlog task dedicated to Rift/workspace frame-disposal event
    handling and explicitly bring it back to the user later before that layer
    is implemented.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T20:54:55Z
  TYPE: FACT
  CLAIM: The frame-ownership contract is now cut to the bottom-up model the
    user selected. `AethericFrame` now requires an owning `Aether` in its
    constructor and unregisters itself bottom-up on `cleanup()`. The old
    top-down `Aether.cleanup_frame(...)` path is gone. `Aether` now only owns
    a private `_detach_cleaned_frame(...)` helper used after frame-owned
    teardown, and `Rift` now disposes nexus frames by calling the frame's own
    `cleanup()` rather than routing back through `Aether`. The direct
    `AethericFrame(...)` test call sites were updated to pass `Aether()`
    explicitly instead of preserving the old bare constructor.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:33-130
  - src/melder/aether/aether.py:80-82
  - src/melder/aether/aether.py:176-244
  - src/melder/aether/aether.py:319-346
  - src/melder/aether/nexus/rift/rift.py:505-516
  - src/melder/utilities/interfaces/interfaces.py:5067-5090
  - src/melder/utilities/interfaces/interfaces.py:5512-5590
  - tests/unit/melder/aether/test_aether.py:82-240
  - tests/unit/melder/aether/test_aetheric_frame.py:1-97
  - tests/integration/melder/aether/test_aether_integration_frames.py:221-255
  - tests/integration/melder/aether/test_aether_integration_registry_ops.py:70-89
  IMPACT: Frame cleanup and registry detachment now tell one story: frames own
    their own teardown, while Aether owns only the registry detach step after
    that teardown has completed. The repo no longer advertises the split
    top-down `cleanup_frame(...)` model.
  NEXT: report the slice as review-ready with `Not run.` for pytest and decide
    whether to keep pushing on frame behavior or move back into Rift/workspace.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T20:54:55Z
  TYPE: MEASURE
  CLAIM: The bottom-up frame-ownership slice is syntax-clean across the
    touched runtime and affected Aether/AethericFrame test files. The only
    remaining bare `AethericFrame(None, ...)` constructor match is the
    intentional negative test proving the new owner-required constructor
    contract.
  EVIDENCE:
  - command:.venv\Scripts\python.exe -m py_compile src\melder\utilities\interfaces\interfaces.py src\melder\aether\aether.py src\melder\aether\aetheric_frame.py src\melder\aether\nexus\nexus.py src\melder\aether\nexus\rift\rift.py tests\unit\melder\aether\test_aether.py tests\unit\melder\aether\test_aetheric_frame.py tests\unit\melder\aether\test_aetheric_rift_system.py tests\component\melder\aether\dev_ops\change_control_manager\test_change_control_manager_component.py tests\component\melder\aether\dev_ops\incident_manager\test_incident_manager_component.py tests\component\melder\aether\dev_ops\spell_system_states\test_spell_system_states_component.py tests\component\melder\aether\dev_ops\test_dev_ops_manager_component.py tests\component\melder\spellbook\spell_crafter\dag\test_spellbook_component_dag_targeting.py tests\component\melder\spellbook\spell_crafter\system\test_spellbook_component_spell_system_adjacency_builder.py tests\component\melder\spellbook\spell_crafter\system\test_spellbook_component_spell_system_adjacency_snapshot.py tests\component\melder\spellbook\spell_crafter\system\test_spellbook_component_spell_system_index.py tests\component\melder\spellbook\spell_crafter\system\test_spellbook_component_spell_system_node.py tests\component\melder\spellbook\spell_crafter\system\test_spellbook_component_spell_system_root_blueprint_builder.py tests\component\melder\spellbook\spell_crafter\system\test_spellbook_component_spell_system_validation_state.py tests\component\melder\spellbook\spell_crafter\system\test_spellbook_component_system_diagnostic.py tests\component\melder\spellbook\spell_crafter\system\validation\test_spellbook_component_system_validation_graph_consistency.py tests\component\melder\spellbook\spell_crafter\system\validation\test_spellbook_component_system_validation_system.py tests\integration\melder\aether\test_aether_integration_error_paths.py tests\integration\melder\aether\test_aether_integration_frames.py tests\integration\melder\aether\test_aether_integration_registry_ops.py tests\integration\melder\aether\test_aether_integration_frame_cleanup.py
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern 'AethericFrame\(\s*"|AethericFrame\(\s*None|cleanup_frame\('
  IMPACT: The contract cut is mechanically stable; remaining uncertainty is
    user-run pytest behavior, not syntax or stale-symbol drift.
  NEXT: report the change truthfully as `Not run.` for pytest and ask for the
    next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T20:46:38Z
  TYPE: DECISION
  CLAIM: The frame-ownership contract is changing again by explicit user
    direction. Instead of keeping a top-down `Aether.cleanup_frame(...)`
    removal path, `AethericFrame` should now require an owning `Aether`
    reference at construction time and should unregister itself bottom-up on
    `cleanup()`. That makes `AethericFrame` a true Aether-owned object rather
    than a standalone frame value, but it also means the direct
    `AethericFrame("name")` constructor pattern currently used in many tests
    has to move with it.
  EVIDENCE:
  - user_instruction: "when we make an aetheric_frame require the aether be passed in during construction"
  - user_instruction: "get rid of cleanup frame and just call cleanup on the frame itself"
  - src/melder/aether/aether.py:176-253
  - src/melder/aether/aether.py:300-346
  - src/melder/aether/aetheric_frame.py:16-155
  - tests/unit/melder/aether/test_aetheric_frame.py:1-196
  - tests/integration/melder/aether/test_aether_integration_frame_cleanup.py:1-97
  IMPACT: The next patch has to remove `cleanup_frame(...)`, make frame cleanup
    bottom-up, and update direct frame construction call sites/tests to the new
    owner-required constructor instead of leaving the repo on a split contract.
  NEXT: refactor `Aether`/`AethericFrame` around a non-recursive bottom-up
    detach helper, then update the direct frame tests to the new constructor.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T20:24:50Z
  TYPE: MEASURE
  CLAIM: After adding the missing `IAether.cleanup_frame(...)` protocol entry,
    the touched Nexus-frame lifecycle slice still compiles cleanly and the live
    tree stays free of the removed legacy `_nexus_frame_ref_counts`,
    `allow_direct_state_access`, and `IAethericRiftState` surfaces.
  EVIDENCE:
  - command:.venv\Scripts\python.exe -m py_compile src\melder\utilities\interfaces\interfaces.py src\melder\aether\nexus\nexus_frame_record.py src\melder\aether\nexus\nexus.py src\melder\aether\nexus\rift\rift.py src\melder\aether\aether.py tests\unit\melder\aether\test_aetheric_rift_system.py
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern "_nexus_frame_ref_counts|allow_direct_state_access|IAethericRiftState"
  IMPACT: The current frame-lifecycle slice is mechanically stable and the live
    codebase no longer advertises the older frame-count or public-state model.
  NEXT: report the slice as review-ready with `Not run.` for pytest and ask for
    the next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T20:23:33Z
  TYPE: FACT
  CLAIM: Nexus frame lifecycle is now real instead of name-only. `Nexus` now
    owns `NexusFrameRecord` metadata objects keyed by frame name, unnamed Rifts
    now receive deterministic `nexus_rift_N` names, `Rift` now realizes its
    assigned Nexus frames through hidden `Aether`, `Nexus.remove_rift(...)`
    now disposes orphaned non-immutable Nexus frames through the removing Rift,
    and `Aether.cleanup_frame(...)` now notifies Nexus first so external frame
    disposal clears the corresponding record and local Rift frame refs. The
    one still-open limit is indexed shared-access semantics: indexed mode now
    has concrete named-frame creation, but there is still no higher-level API
    for another Rift to deliberately attach/switch into an existing indexed
    frame.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_record.py:1-223
  - src/melder/aether/nexus/nexus.py:100-113
  - src/melder/aether/nexus/nexus.py:371-439
  - src/melder/aether/nexus/nexus.py:441-474
  - src/melder/aether/nexus/nexus.py:543-572
  - src/melder/aether/nexus/nexus.py:586-892
  - src/melder/aether/nexus/rift/rift.py:131-150
  - src/melder/aether/nexus/rift/rift.py:413-478
  - src/melder/aether/aether.py:176-235
  IMPACT: Shared and one-per-workspace Nexus-frame lifecycle now has concrete
    runtime behavior, and the codebase has the record layer needed for future
    indexed attach/access APIs without keeping the old raw ref-count model.
  NEXT: validate the focused tests or keep the slice in review and decide
    whether the next step is indexed attach/access API or workstation/workspace
    behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T20:23:33Z
  TYPE: MEASURE
  CLAIM: The new Nexus-frame record slice is syntax-clean and the old
    `_nexus_frame_ref_counts` path is gone from the live source/test tree.
  EVIDENCE:
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern "_nexus_frame_ref_counts|NexusFrameRecord|check_for_aetheric_frame|nexus_rift_"
  - command:.venv\Scripts\python.exe -m py_compile src\melder\aether\nexus\nexus_frame_record.py src\melder\aether\nexus\nexus.py src\melder\aether\nexus\rift\rift.py src\melder\aether\aether.py src\melder\utilities\interfaces\interfaces.py tests\unit\melder\aether\test_aetheric_rift_system.py
  IMPACT: The lifecycle refactor is mechanically stable enough for review. The
    remaining uncertainty is behavior-level validation in a user-run pytest
    environment, not syntax or stale-symbol cleanup.
  NEXT: report the slice truthfully as `Not run.` for pytest and ask whether to
    continue into indexed attach/access or workstation/workspace behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T20:18:01Z
  TYPE: PLAN
  CLAIM: The narrow next slice is now well-scoped enough to implement without
    reopening the public-root model. We should add a real `NexusFrameRecord`
    object, replace `_nexus_frame_ref_counts` with a record registry, have
    `Rift` realize nexus frames through `Aether._ensure_frame(...)`, add
    deterministic default Rift names (`nexus_rift_N`), and have
    `Aether.cleanup_frame(...)` notify Nexus before disposing a frame. This is
    the smallest patch that turns nexus-frame behavior from naming-only policy
    into actual lifecycle management.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:35-109
  - src/melder/aether/nexus/nexus.py:360-420
  - src/melder/aether/nexus/rift/rift.py:62-146
  - src/melder/utilities/interfaces/interfaces.py:5415-5538
  - src/melder/aether/aether.py:176-215
  IMPACT: We can land concrete shared and one-per-workspace frame lifecycle
    behavior now, while keeping the more ambitious indexed attach/access API as
    a later follow-up rather than blocking the whole frame model on it.
  NEXT: implement the record class, wire Rift frame realization and default
    naming, patch Nexus/Aether cleanup hooks, and add focused lifecycle tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T20:16:58Z
  TYPE: FACT
  CLAIM: The next lower-layer gap is now concrete. The live `Nexus` runtime
    still treats nexus-frame ownership as plain name assignment plus integer
    ref counts, while `Rift` still only stores assigned frame names and does
    not realize or manage those frames through `Aether`. `Aether.cleanup_frame`
    also removes frames without any Nexus-side detachment hook. That means the
    current code still lacks the richer nexus-frame lifecycle model we discussed
    for shared/indexed/one-per-workspace behavior.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:35-109
  - src/melder/aether/nexus/nexus.py:360-420
  - src/melder/aether/nexus/rift/rift.py:62-146
  - src/melder/aether/aether.py:176-215
  IMPACT: The next implementation slice should replace raw nexus-frame ref
    counts with real frame records and wire frame realization/disposal through
    `Rift`/`Aether` so the configured topology modes have concrete lifecycle
    behavior instead of only naming behavior.
  NEXT: define the narrow patch boundary for `NexusFrameRecord` plus shared and
    one-per-workspace lifecycle behavior, then implement that slice before
    reopening workstation/workspace work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T19:55:20Z
  TYPE: FACT
  CLAIM: The remaining live legacy debt after the Nexus rename is now narrow and
    concrete: the protocol layer still declares the old
    `IAethericRiftSystem*` / `IAethericRift*` types and aliases the new names
    on top, the dead `IAethericRiftState` protocol still survives in
    `interfaces.py`, and a few live Nexus configuration methods/docstrings
    still return or mention the old type names and ARS wording. This is not a
    behavior gap; it is stale type/documentation surface that should be cut
    outright because the user explicitly rejected keeping legacy scaffolding.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:5133-5579
  - src/melder/aether/nexus/configuration/nexus_configuration.py:506-562
  - src/melder/aether/nexus/configuration/nexus_configuration.py:853-889
  - src/melder/aether/nexus/configuration/rift_configuration.py:422-439
  IMPACT: The next patch should delete the alias-style legacy interface layer
    instead of preserving it, and it should finish the live Nexus docstring
    cleanup so the runtime/type surface tells one story only.
  NEXT: rename the protocol declarations to `INexus*` / `IRift*`, remove the
    dead Rift-state protocol, clean the stale live annotations/docstrings, and
    rerun syntax validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T19:55:20Z
  TYPE: MEASURE
  CLAIM: The final legacy-surface cleanup is syntax-clean and the active
    source/test tree no longer contains the old `IAethericRift*` protocol
    names, the dead `IAethericRiftState` interface, or the old
    `system_frame_*` vocabulary in the live Nexus runtime.
  EVIDENCE:
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern "IAethericRiftSystemConfiguration|IAethericRiftConfiguration|IAethericRift\b|IAethericRiftSystem\b|IAethericRiftState|AethericRiftState|RiftState retrieval|directly from ARS"
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern "system_frame_"
  - command:.venv\Scripts\python.exe -m py_compile src\melder\utilities\interfaces\interfaces.py src\melder\aether\nexus\configuration\nexus_configuration.py src\melder\aether\nexus\configuration\rift_configuration.py src\melder\aether\nexus\configuration\rift_access_mode.py src\melder\aether\aether.py src\melder\aether\nexus\nexus.py src\melder\aether\nexus\rift\rift.py tests\unit\melder\aether\test_aether.py tests\unit\melder\aether\test_aetheric_rift_system.py
  IMPACT: The public-root refactor no longer carries a split naming story in
    the live type/runtime surface. Remaining work can move downward into real
    Rift/Nexus behavior instead of more rename debt.
  NEXT: keep the task in review until the user either accepts the Nexus/Rift
    slice or redirects into the next lower-layer frame/workstation work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T19:58:16Z
  TYPE: FACT
  CLAIM: The last dead public-state API seam is now gone too. Because the new
    Nexus/Rift model no longer exposes a separate public Rift-state object, the
    old `allow_direct_state_access` / `state_access_token_*` configuration
    fields and fluent methods were dead surface area only. They have now been
    removed from the live Nexus configuration and interface layer instead of
    being left behind as misleading no-op knobs.
  EVIDENCE:
  - src/melder\aether\nexus\configuration\nexus_configuration.py:56-87
  - src/melder\aether\nexus\configuration\nexus_configuration.py:241-272
  - src/melder\aether\nexus\configuration\nexus_configuration.py:506-580
  - src/melder\utilities\interfaces\interfaces.py:5133-5547
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern "allow_direct_state_access|state_access_token_required|state_access_token_value|with_direct_state_access|with_state_access_token_required|with_state_access_token|IAethericRiftState|RiftState retrieval"
  IMPACT: The live Nexus surface no longer advertises state-access behavior for
    an object model that no longer exists. The remaining work can now move to
    actual Rift/Nexus behavior instead of cleanup debt.
  NEXT: keep the slice in review for user acceptance, then move into the next
    lower-layer Rift/Nexus behavior work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T22:47:05Z
  TYPE: PLAN
  CLAIM: The current public AR surface is still carrying the wrong root model:
    `Aether` facades the AR subsystem publicly and the design still assumes a
    separate public state object for Rifts. The approved simplification is a
    second singleton root, `Nexus`, privately hosted by `Aether` but not
    exposed through it; `Nexus` owns only Rift registry/config/lifecycle
    state, and `Rift` itself owns the live runtime state it needs.
  EVIDENCE:
  - src/melder/aether/aether.py:47-88
  - src/melder/aether/aether.py:272-423
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:22-57
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:13-63
  - src/melder/aether/aetheric_rift_system/aetheric_rift_state/aetheric_rift_state.py:8-41
  IMPACT: The next slice should replace the hosted-facade/state-hydration
    model rather than widen it.
  NEXT: add patch docs and route the board/story to this refactor before code
    edits begin.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T22:47:05Z
  TYPE: FACT
  CLAIM: The current implementation surfaces the old model in three concrete
    places that all have to move together: `Aether` still exposes direct
    public-ish Rift facade methods, the interface layer still codifies
    `IAethericRiftSystem` plus `IAethericRiftState` as first-class concepts,
    and the focused tests still validate that `Aether` is the normal entrypoint
    for creating/programming/accessing Rifts.
  EVIDENCE:
  - src/melder/aether/aether.py:272-423
  - src/melder/utilities/interfaces/interfaces.py:5133-5562
  - tests/unit/melder/aether/test_aether.py:248-380
  - tests/unit/melder/aether/test_aetheric_rift_system.py:1-198
  IMPACT: The refactor cannot be a narrow rename. We need one coherent pass
    across `Aether`, the AR interfaces/classes, and the focused tests or we
    will leave two public roots alive at once.
  NEXT: implement the singleton/public-surface change across those seams
    together, then refresh the active docs and tests to the new Nexus model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T22:47:05Z
  TYPE: DECISION
  CLAIM: The implementation should not preserve backward compatibility for the
    old Aether-facing Rift facade or the old ARS/state public surface. This
    refactor should cut directly to the new model instead of leaving aliases or
    duplicate entrypoints alive.
  EVIDENCE:
  - user_instruction: "hold up stop fucken backward compat just fix it bro"
  IMPACT: We can delete the obsolete public surface instead of carrying
    transition scaffolding that keeps the wrong model alive.
  NEXT: remove the old Aether Rift-facade methods and old ARS/state public
    assumptions outright while finishing the Nexus/Rift rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T23:13:23Z
  TYPE: FACT
  CLAIM: The public Rift surface is now cut to the new model. `Aether` eagerly
    creates and privately holds a `Nexus` singleton at boot, but no longer
    carries the old public Rift facade. `Nexus` is now the live singleton root
    for Rift registry/config/lifecycle state, and `Rift` now owns the live
    runtime/config/frame-assignment state it needs directly instead of relying
    on a separate public state object. The focused Aether/Nexus tests now
    assert this new ownership/public-root model.
  EVIDENCE:
  - src/melder/aether/aether.py:47-120
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:22-454
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:14-343
  - src/melder/utilities/interfaces/interfaces.py:5395-5559
  - tests/unit/melder/aether/test_aether.py:84-298
  - tests/unit/melder/aether/test_aetheric_rift_system.py:1-240
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md:12-119
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_aetheric_rift_core.md:4-88
  IMPACT: The repo no longer expects users to go through `Aether` for Rift work
    or to reason about a separate public `RiftState` object. The next follow-up
    can focus lower, on workstation/workspace behavior.
  NEXT: record validation truthfully, sync the board to review, and let the
    user decide whether to accept this slice or keep iterating.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T23:13:23Z
  TYPE: MEASURE
  CLAIM: Syntax validation passed for the touched Nexus/Rift runtime, test, and
    interface files via `py_compile`. Targeted pytest execution was not run in
    this environment.
  EVIDENCE:
  - command:.venv\Scripts\python.exe -m py_compile src\melder\aether\aether.py src\melder\aether\aetheric_rift_system\aetheric_rift_system.py src\melder\aether\aetheric_rift_system\aetheric_rift\aetheric_rift.py src\melder\aether\aetheric_rift_system\configuration\aetheric_rift_system_configuration.py src\melder\aether\aetheric_rift_system\configuration\aetheric_rift_configuration.py src\melder\utilities\interfaces\interfaces.py tests\unit\melder\aether\test_aether.py tests\unit\melder\aether\test_aetheric_rift_system.py
  IMPACT: The refactor is syntax-clean, but behavioral verification still
    depends on a user-run pytest environment.
  NEXT: report the slice as review-ready and say `Not run.` for pytest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-28T23:13:23Z
  TYPE: DECISION
  CLAIM: The new Nexus/Rift code needs one more contract pass for thread
    safety. Per the active runtime standard, cleanup-owning objects should have
    an instance `RLock` by default, but we should not cargo-cult extra locking
    around dict/list/set primitives now that Python 3.14t gives those
    containers internal locks. The narrow fix is to add per-instance `RLock`s
    to `Nexus` and `Rift`, then use them around cleanup and multi-step state
    mutations only.
  EVIDENCE:
  - user_instruction: "any object with cleanup requires a lock just by default"
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:47-60
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:175-213
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:38-55
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:121-157
  IMPACT: Without this pass, the new public root is not fully aligned with the
    repo's cleanup/thread-safety expectation for live mutable objects.
  NEXT: add per-instance `RLock`s to `Nexus` and `Rift`, guard cleanup and
    registry/state mutations, then re-run syntax validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T23:13:23Z
  TYPE: FACT
  CLAIM: `Nexus` and `Rift` now both carry per-instance `threading.RLock`
    fields and use them around cleanup plus the multi-step mutations that
    actually need serialization (`enable`, `disable`, `create_rift`, `add_rift`,
    `remove_rift`, `register_space`, `set_active_space`, and the live
    registration/activation flags). The refactor intentionally does not add
    extra locking around dict/list/set primitives themselves, matching the
    user’s Python 3.14t guidance.
  EVIDENCE:
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:47-60
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:93-103
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:175-213
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:246-387
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:38-55
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:104-157
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:307-402
  IMPACT: The new public root and live Rift object now match the repo’s
    cleanup/thread-safety expectation without over-locking container access.
  NEXT: run the final syntax pass, then return the task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T23:13:23Z
  TYPE: FACT
  CLAIM: One focused Nexus test was still carrying old mutable-config
    expectations. After `nexus.enable(configuration)`, the installed
    `NexusConfiguration` is intentionally frozen, so the test path that tried
    to mutate `nexus.configuration.with_denied_target_frame_names(...)` after
    enablement is stale. The correct contract is to build a fresh configuration
    and re-enable Nexus when a new process-wide policy needs to be installed.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_rift_system.py:190-208
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:227-253
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:167-170
  IMPACT: This is narrow test drift rather than a reason to weaken the frozen
    Nexus configuration contract.
  NEXT: patch the test to install a fresh configuration for the second-half
    allow-list scenario, then let the user re-run the suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T23:13:23Z
  TYPE: FACT
  CLAIM: The current refactor is still structurally incomplete in two concrete
    ways: the filesystem/module layout still advertises the old
    `aetheric_rift_system` / `aetheric_rift` names, and the live `Rift`
    constructor still accepts a Nexus reference without enforcing the intended
    `INexus` readiness contract (exists, not cleaned, configured, enabled).
  EVIDENCE:
  - src/melder/aether/aether.py:6-11
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:22-45
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:57-119
  - tests/unit/melder/aether/test_aetheric_rift_system.py:237-240
  IMPACT: Even though the runtime model changed, the source tree and some
    contracts still visually preserve the wrong domain language and do not yet
    fail fast on bad direct `Rift(...)` construction.
  NEXT: rename the package/files/interfaces to Nexus/Rift names and add direct
    `INexus` readiness checks to `Rift.__init__`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T23:46:06Z
  TYPE: FACT
  CLAIM: The package/file layout now matches the new public model: the live AR
    subtree sits under `src/melder/aether/nexus/`, the old
    `aetheric_rift_system` source package is gone, source/test imports now use
    `melder.aether.nexus.*`, and `Rift.__init__` now fails fast unless it is
    given a real `INexus` that is not cleaned and is already configured and
    enabled. The constructor also requires a finalized `RiftConfiguration` and
    coherent default-frame membership in the assigned frame-name tuples.
  EVIDENCE:
  - src/melder/aether/aether.py:6-11
  - src/melder/aether/nexus/nexus.py:4-17
  - src/melder/aether/nexus/rift/rift.py:7-20
  - src/melder/aether/nexus/rift/rift.py:53-103
  - src/melder/aether/nexus/configuration/nexus_configuration.py:4-13
  - src/melder/aether/nexus/configuration/rift_configuration.py:4-11
  - tests/unit/melder/aether/test_aether.py:4-7
  - tests/unit/melder/aether/test_aetheric_rift_system.py:3-7
  IMPACT: The codebase now lines up with the Nexus naming/story at the
    filesystem level and direct `Rift(...)` construction no longer permits
    half-live objects.
  NEXT: run a final syntax pass over the renamed package and focused tests,
    then keep this slice in review for acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T23:46:06Z
  TYPE: MEASURE
  CLAIM: A stale-import scan over source/tests is now clean for the old
    `aetheric_rift_system` / `aetheric_rift_state` source package paths.
  EVIDENCE:
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern "aetheric_rift_system|aetheric_rift_state"
  IMPACT: The rename pass is not leaving old live package imports behind in the
    active source/test tree.
  NEXT: finish validation and report this slice back for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-28T23:46:06Z
  TYPE: FACT
  CLAIM: The old `src/melder/aether/aetheric_rift_system/` path still exists
    on disk only because of stale `__pycache__` contents and empty moved-out
    subdirectories. There is no remaining live source in that tree.
  EVIDENCE:
  - command:Get-ChildItem -Recurse -Force src\melder\aether\aetheric_rift_system | Select-Object FullName,PSIsContainer,Length
  IMPACT: It is safe to delete the old directory tree outright; doing so will
    make the filesystem finally match the renamed `src/melder/aether/nexus/`
    package layout.
  NEXT: remove the stale `aetheric_rift_system` directory tree and then verify
    the new `nexus/` path is the only live AR package root.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T00:00:00Z
  TYPE: DECISION
  CLAIM: Rift creation should stay ritualized and explicit even under the new
    Nexus model. `Nexus.create_rift(...)` should require a `RiftConfiguration`
    object, and that config should be single-use/consumed on successful Rift
    creation. To keep Nexus useful, it should also own named reusable profile
    templates so callers can ask for
    `create_rift_configuration(profile_name=...)` and still receive a fresh
    per-Rift config object rather than reusing the template object itself.
  EVIDENCE:
  - user_instruction: "nexus.create_rift_configuration(profile_name: Optional[str] = None) -> RiftConfiguration"
  - user_instruction: "nexus.register_rift_profile(name: str, configuration: RiftConfiguration) -> None"
  - user_instruction: "nexus.create_rift(configuration: RiftConfiguration, creation_token: Optional[str] = None, ...) -> Rift"
  IMPACT: The next patch should add profile-template storage and config
    consumption semantics to Nexus/RiftConfiguration instead of letting
    `create_rift(...)` hide all defaulting internally.
  NEXT: add single-use config semantics to `RiftConfiguration`, add Nexus
    profile registration/cloning support, and update the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T15:52:13Z
  TYPE: FACT
  CLAIM: Nexus now supports the explicit config/profile ritual we wanted.
    `create_rift(...)` consumes a single-use `RiftConfiguration`, and Nexus can
    now own named frozen profile templates so
    `create_rift_configuration(profile_name=...)` returns a fresh cloned config
    object rather than reusing the template instance. The focused tests now
    cover both consumed-config rejection and profile-derived config creation.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:221-352
  - src/melder/aether/nexus/nexus.py:363-460
  - src/melder/aether/nexus/nexus.py:721-767
  - src/melder/aether/nexus/configuration/rift_configuration.py:30-181
  - src/melder/aether/nexus/configuration/rift_configuration.py:244-268
  - tests/unit/melder/aether/test_aetheric_rift_system.py:99-164
  IMPACT: Rift creation is now explicit and reusable in the right way:
    templates live on Nexus, but each Rift still gets its own config object.
  NEXT: keep the Nexus slice in review and, if accepted, move downward into
    workstation/workspace ownership and behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T15:52:13Z
  TYPE: MEASURE
  CLAIM: The renamed Nexus package still passes syntax validation and the
    stale-import scan remains clean after the profile/config-consumption pass.
  EVIDENCE:
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern "aetheric_rift_system|aetheric_rift_state"
  - command:.venv\Scripts\python.exe -m py_compile src\melder\aether\aether.py src\melder\aether\nexus\nexus.py src\melder\aether\nexus\rift\rift.py src\melder\aether\nexus\configuration\nexus_configuration.py src\melder\aether\nexus\configuration\rift_configuration.py src\melder\aether\nexus\configuration\nexus_frame_mode.py src\melder\aether\nexus\rift_space\rift_space.py src\melder\aether\nexus\rift_space\static_rift_space.py src\melder\aether\nexus\rift_space\dynamic_rift_space.py src\melder\utilities\interfaces\interfaces.py tests\unit\melder\aether\test_aether.py tests\unit\melder\aether\test_aetheric_rift_system.py
  IMPACT: The new API surface is mechanically stable; remaining verification is
    user-run pytest rather than source-shape cleanup.
  NEXT: report the slice back with `Not run.` for pytest and wait for either
    acceptance or the next lower-layer design ask.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T19:43:47Z
  TYPE: FACT
  CLAIM: The internal Nexus-owned frame terminology is now cleaned up where the
    live Nexus model actually uses it: `system_frame_*` became
    `nexus_frame_*` across the Nexus runtime/config/test surface, including the
    Rift fields, the Nexus internal frame-budget registry, the configuration
    keys and fluent methods, the focused tests, and the live interface surface
    those files use. The remaining `system_frame_name` mention is confined to
    the legacy/internal `IAethericRiftState` protocol, which is no longer part
    of the live public model.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:63-108
  - src/melder/aether/nexus/nexus.py:406-770
  - src/melder/aether/nexus/rift/rift.py:49-50
  - src/melder/aether/nexus/rift/rift.py:67-137
  - src/melder/aether/nexus/configuration/nexus_configuration.py:75-78
  - src/melder/aether/nexus/configuration/nexus_configuration.py:260-263
  - src/melder/aether/nexus/configuration/nexus_configuration.py:303-324
  - tests/unit/melder/aether/test_aetheric_rift_system.py:112-115
  - tests/unit/melder/aether/test_aetheric_rift_system.py:262-285
  IMPACT: The live Nexus layer no longer talks about those internal frames as
    “system” state, which makes the ownership domain clearer and lines up with
    the new public root name.
  NEXT: keep the task in review and move down into workstation/workspace
    behavior if the user accepts the current Nexus/Rift slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T19:43:47Z
  TYPE: MEASURE
  CLAIM: The final `nexus_frame_*` terminology pass is syntax-clean across the
    renamed runtime/config/test surface.
  EVIDENCE:
  - command:.venv\Scripts\python.exe -m py_compile src\melder\aether\nexus\nexus.py src\melder\aether\nexus\rift\rift.py src\melder\aether\nexus\configuration\nexus_configuration.py src\melder\aether\nexus\configuration\nexus_frame_mode.py tests\unit\melder\aether\test_aetheric_rift_system.py
  IMPACT: The rename did not introduce another mechanical break in the live
    Nexus slice.
  NEXT: report the slice back as review-ready and say `Not run.` for pytest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T19:18:39Z
  TYPE: DECISION
  CLAIM: Internal frame terminology should stop using `system_frame_*` now that
    the public root is `Nexus`. Where the field or config key refers to
    Nexus-owned internal frame assignment/lifecycle rather than target/userland
    frames, the code should say `nexus_frame_*`.
  EVIDENCE:
  - user_instruction: "yeah rename that shit please"
  - src/melder/aether/nexus/nexus.py:63-108
  - src/melder/aether/nexus/configuration/nexus_configuration.py:75-78
  - src/melder/aether/nexus/rift/rift.py:49-50
  IMPACT: This removes one last confusing semantic leak from the older model
    and makes it clearer that these fields belong to Nexus-managed internal
    frame behavior, not Aether-global substrate state.
  NEXT: rename the internal runtime/config/test/interface vocabulary from
    `system_frame_*` to `nexus_frame_*`, then rerun syntax validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task now captures an implemented public-root refactor: hidden `Aether`
substrate, public `Nexus` singleton root, live `Rift` objects owning their own
runtime state, no separate public `RiftState`, and an explicit single-use
config/profile ritual for Rift creation. The next step, if accepted, is to move
downward into workstation/workspace ownership and behavior rather than
revisiting the public root again.
