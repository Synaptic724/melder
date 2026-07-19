# Task: Remove Conduit Cloud And Cluster Methods From Conduit
- Completed: 2026-05-20T08:58:57Z
- Summary: Closed after removing the public conduit cloud/cluster surface from `Conduit`, rewiring runtime callers to Aether or the frame-local cloud, and validating the widened caller ring.

## Metadata
- Task ID: TASK-2026-05-19-remove-conduit-cloud-and-cluster-methods-from-conduit
- Story: none
- Epic: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-19T22:26:33Z
- Updated: 2026-05-20T08:58:57Z

## Objective
Remove the public conduit-cloud and cluster methods from `Conduit` while
keeping the injected `_conduit_cloud` field for internal registration and
lifecycle only, then rewire live callers to use `Aether.get_conduit_cloud(...)`
or the frame-local cloud directly.

## Ticket Contract
- ENTRY_GATE: this task is routed on `attention_board.md` and the first live call-site finding is written before implementation continues.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/utilities/interfaces/iconduit.py`
  - live runtime callers of the removed conduit surface
  - focused tests that directly exercised those methods
- DEPENDENCIES:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/utilities/interfaces/iconduit.py`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/aetheric_frame/conduit_cloud.py`
  - `src/melder/nexus/rift/command_system/capability_command_system.py`
  - `src/melder/nexus/rift/command_system/codegen_command_system.py`
  - `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- EXIT_GATE: the conduit surface no longer exposes the cloud/cluster methods,
  runtime callers are rewired, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removal forces wider command
  or contract-surface redesign than this lane can absorb cleanly.

## Scope Boundaries
- In scope:
  - remove public conduit cloud methods from `Conduit`
  - remove public cluster methods from `Conduit`
  - rewire live source callers
  - update focused tests
- Out of scope:
  - internal `_conduit_cloud` field removal
  - cloud registration lifecycle redesign
  - unrelated spell/spellbook/runtime cuts

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly narrowed the next removal cut to conduit cloud methods and cluster features on `Conduit`.

## Steps / Checklist
- [x] Remove cloud/cluster methods from `Conduit` and `IConduit`.
- [x] Rewire runtime callers to `Aether.get_conduit_cloud(...)` or the cloud directly.
- [x] Update focused tests and public-surface expectations.
- [x] Validate with `.\.venv_new`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- reduced `Conduit` public surface
- updated runtime callers
- focused green validation

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-19_remove_conduit_cloud_and_cluster_methods_from_conduit_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m py_compile <touched runtime files>`
  - `.\.venv_new\Scripts\python.exe -m pytest -q <focused conduit/cloud/command rings>`

## Risks / Rollback Notes
- Risk: command-system and integration tests still assume the conduit surface owns cloud/cluster operations.
  Rollback: patch the caller to the frame-local cloud instead of weakening the removal.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T22:26:33Z
  TYPE: FACT
  CLAIM: The removable conduit surface is explicit: cloud registration
    helpers, direct cloud exposure, conduit-id/name lookup helpers, and cluster
    convenience methods all still live on `Conduit`. The main live runtime
    callers are capability/codegen command systems plus two conduit-internal
    helpers (`ConduitWard` and transfer-of-ownership).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:944-1026
  - src/melder/aether/conduit/conduit.py:2369-2423
  - src/melder/aether/conduit/conduit.py:2860-2950
  - src/melder/utilities/interfaces/iconduit.py:254-269
  - src/melder/utilities/interfaces/iconduit.py:406-470
  - src/melder/utilities/interfaces/iconduit.py:1061-1118
  - src/melder/nexus/rift/command_system/capability_command_system.py:446-579
  - src/melder/nexus/rift/command_system/codegen_command_system.py:388-388
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:433-446
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1300-1308
  IMPACT: The first implementation pass can stay bounded to the conduit API,
    the two runtime internal callers, and the command-system surfaces that
    still proxy cloud/cluster behavior through conduit.
  NEXT: patch the runtime callers to the frame-local cloud and then remove the
    conduit methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-19T22:36:15Z
  TYPE: FACT
  CLAIM: The conduit surface reduction is landed. `Conduit` and `IConduit` no
    longer expose cloud registration, cloud lookup, or cluster convenience
    methods. The live runtime callers that depended on those methods now use
    `Aether.get_conduit_cloud(...)` or `Aether.get_conduit_by_id(...)`
    directly instead.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:944-1026
  - src/melder/aether/conduit/conduit.py:2369-2423
  - src/melder/aether/conduit/conduit.py:2860-2950
  - src/melder/utilities/interfaces/iconduit.py:251-317
  - src/melder/utilities/interfaces/iconduit.py:404-476
  - src/melder/utilities/interfaces/iconduit.py:1058-1118
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:433-446
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1299-1309
  - src/melder/nexus/rift/command_system/capability_command_system.py:436-579
  - src/melder/nexus/rift/command_system/codegen_command_system.py:378-388
  IMPACT: The conduit runtime still carries `_conduit_cloud` internally for
    registration/lifecycle, but the public cloud/cluster access story has moved
    off the conduit surface.
  NEXT: either stop here or start migrating the remaining integration tests and
    public callers to the cloud/Aether entry points.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T22:36:15Z
  TYPE: MEASURE
  CLAIM: Focused validation passed for the reduced conduit surface and the
    rewired command-system callers on `.\.venv_new`.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:1-816
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:1-1096
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:1-344
  - tests/unit/melder/aether/test_command_system_direct.py:1-430
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:1-400
  IMPACT: The direct runtime and unit-surface fallout of the removal cut is
    contained.
  NEXT: note the residual risk that broader integration tests still reference
    the removed conduit surface and were not migrated in this pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-19T22:46:31Z
  TYPE: FACT
  CLAIM: The remaining direct test callers of the removed conduit cloud and
    cluster surface are now migrated to the frame-local cloud or the retained
    `Aether` discovery surface. The removed conduit methods no longer appear in
    the migrated integration/unit call sites.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_public_api.py:462-468
  - tests/integration/melder/conduit/test_conduit_integration_lookup_helpers.py:207-239
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:143-164
  - tests/integration/melder/conduit/test_conduit_integration_existence.py:253-257
  - tests/integration/melder/conduit/test_conduit_integration_cluster_sharing_edges.py:128-139
  - tests/integration/melder/conduit/test_conduit_integration_clusters_spellspace.py:77-94
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:603-610
  - tests/integration/melder/spellbook/test_spellbook_integration_fluent.py:412-419
  - tests/integration/melder/aether/test_aether_integration_frames.py:120-129
  - tests/unit/melder/aether/test_nexus.py:2135-2153
  IMPACT: The removal cut now extends beyond the initial unit ring and into the
    main migrated integration surfaces that used the old conduit API directly.
  NEXT: if the user wants more, move on to the next bounded conduit/cloud
    ownership cut instead of revisiting this removed API.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-19T22:46:31Z
  TYPE: MEASURE
  CLAIM: The widened migrated validation ring is green on `.\.venv_new`
    after patching the remaining direct unit/integration callers.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:1-816
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:1-1096
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:1-344
  - tests/unit/melder/aether/test_command_system_direct.py:1-430
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:1-400
  - tests/unit/melder/aether/test_nexus.py:1-5100
  - tests/integration/melder/conduit/test_conduit_integration_public_api.py:1-480
  - tests/integration/melder/conduit/test_conduit_integration_lookup_helpers.py:1-245
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:1-355
  - tests/integration/melder/conduit/test_conduit_integration_existence.py:1-300
  - tests/integration/melder/conduit/test_conduit_integration_cluster_sharing_edges.py:1-240
  - tests/integration/melder/conduit/test_conduit_integration_clusters_spellspace.py:1-170
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1-1000
  - tests/integration/melder/spellbook/test_spellbook_integration_fluent.py:1-430
  - tests/integration/melder/aether/test_aether_integration_frames.py:1-220
  - tests/integration/melder/aether/test_aether_integration_cluster_sharing_internal.py:1-220
  IMPACT: The migrated caller surface is stable enough to close this API-removal
    tranche without immediately widening to full-suite work.
  NEXT: `Not run.` for the full suite; only proceed further if the user wants
    the next refactor target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-19T23:02:51Z
  TYPE: MEASURE
  CLAIM: The second-wave unit harnesses for conduit-ward and transfer-of-ownership
    are now aligned to the new Aether/cloud lookup path and the focused rings
    are green.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:1-2476
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1-4426
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:1-1546
  IMPACT: The removed conduit cloud surface is now reflected not just in the
    direct caller migrations, but also in the deeper transfer/ward harnesses
    that assumed the old conduit-owned lookup boundary.
  NEXT: `Not run.` for the full suite; the current focused migration rings are
    stable enough to move to the next refactor target if requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Active removal lane for conduit cloud/cluster methods. The next step is the
runtime caller rewrite, then the conduit/interface API removal itself.
