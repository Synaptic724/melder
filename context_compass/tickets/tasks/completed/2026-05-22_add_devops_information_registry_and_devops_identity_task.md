# Task: Add DevOps Information Registry And DevopsIdentity

## Metadata
- Task ID: TASK-2026-05-22-add-devops-information-registry-and-devops-identity
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-22T22:08:36Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Add an `AethericFrame`-owned `DevOpsInformationRegistry` plus a renamed
`DevopsIdentity` surface so dev-ops has one explicit object/relationship
topology registry for future transaction and reporting work.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a frame-owned dev-ops registry and
  identity rename before wider strategy work.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/dev_ops/**`
  - direct import/update surfaces that currently reference
    `TransactionIdentity`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_migrate_bind_transaction_resolution_into_mediator_task.md`
  - patch lane `system_docs/patches/active/devops_information_registry_identity/`
- EXIT_GATE: `AethericFrame` owns a new registry, `DevOpsManager` borrows it,
  `TransactionIdentity` is replaced by `DevopsIdentity`, and both objects
  expose explicit cleanup-safe registration APIs.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rename or registry owner
  placement forces wider runtime migration than the approved slice.

## Scope Boundaries
- In scope:
  - new `DevOpsInformationRegistry`
  - rename `TransactionIdentity` to `DevopsIdentity`
  - registry cleanup, identity cleanup, and `AethericFrame`/`DevOpsManager`
    ownership wiring
  - relation maps for spellbook/conduit/link/cluster and transaction storage
- Out of scope:
  - strategy behavior changes
  - transaction policy changes
  - spellbook/conduit registration wiring beyond what is required for the
    identity rename boundary

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user approved starting with the registry and identity
  layer before wider strategy work.

## Steps / Checklist
- [ ] Create patch-lane artifacts for registry and identity work.
- [ ] Add `DevOpsInformationRegistry` with relation and transaction indexes.
- [ ] Rename `TransactionIdentity` to `DevopsIdentity`.
- [ ] Wire `DevOpsManager` to own the registry.
- [ ] Update direct runtime imports/references for the identity rename.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- `DevOpsInformationRegistry`
- `DevopsIdentity`
- `AethericFrame` registry ownership wiring
- `DevOpsManager` registry access wiring

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-22_add_devops_information_registry_and_devops_identity_task.md`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/system_docs/patches/active/devops_information_registry_identity/**`
- `src/melder/aether/aetheric_frame/dev_ops/**`
- directly implicated identity import surfaces

## Validation
- Not run.
- Recommended commands:
  - `./.venv_new/Scripts/python.exe -m pytest -q tests/unit/melder/aether/dev_ops`

## Risks / Rollback Notes
- Risk: rename surface may be wider than the registry object itself because
  identity imports exist in spellbook, conduit, mediator, and session layers.
  Rollback: keep runtime behavior unchanged and stop after the rename boundary
  if wider transaction behavior starts leaking in.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into transaction strategy behavior in this slice.

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
  - `system_docs/patches/active/devops_information_registry_identity/architecture_patch.md`
  - `system_docs/patches/active/devops_information_registry_identity/component_patch_devops_information_registry.md`
  - `system_docs/patches/active/devops_information_registry_identity/component_patch_devops_identity.md`
  - `system_docs/patches/active/devops_information_registry_identity/component_patch_devops_manager.md`
  - `system_docs/patches/active/devops_information_registry_identity/code_description_patch_devops_information_registry.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: registry ownership, relation indexes, cleanup guarantees, and
  narrow rename impacts.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:37:34Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this remaining active lane for closure and
    requested that it be turned in and moved to the completed task set.
  EVIDENCE:
  - user_instruction
  IMPACT: This task is closed and should no longer route active work on the
    attention board.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-22T22:08:36Z
  TYPE: PLAN
  CLAIM: The current dev-ops stack has no single authoritative object and
    relation registry. `DevOpsManager` owns ops subsystems, `SpellSystemStates`
    owns lineage/validity, and `ChangeControlTransactionManager` only has a
    shallow link mirror. The approved next slice is to add an
    `AethericFrame`-owned `DevOpsInformationRegistry`, hand that registry into
    `DevOpsManager`, and replace `TransactionIdentity` with a more general
    `DevopsIdentity`.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:13-367
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:25-1290
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py:435-515
  IMPACT: This gives future transaction strategy work one explicit topology
    surface instead of forcing mediator logic to stitch identity and relation
    truth together from multiple scattered runtime objects.
  NEXT: create the patch lane, then implement the registry and identity objects
    plus `DevOpsManager` ownership wiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T22:25:38Z
  TYPE: DECISION
  CLAIM: Registry ownership belongs on `AethericFrame`, not `DevOpsManager`.
    `DevOpsManager` is a consumer/facade, but the frame owns the child object
    cleanup order, so the registry must outlive object unregister calls during
    conduit, spellbook, cloud, and cluster teardown.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:63-127
  - src/melder/aether/aetheric_frame/aetheric_frame.py:133-240
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:21-138
  IMPACT: The implementation must create the registry in `AethericFrame`,
    hand it into `DevOpsManager`, and defer registry cleanup until after
    frame-owned objects have torn themselves down.
  NEXT: wire `AethericFrame` to own the registry and let `DevOpsManager` borrow it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T22:25:38Z
  TYPE: FACT
  CLAIM: The first registry/identity slice is now landed in source: new
    `DevopsIdentity` and `DevopsInformationRegistry` objects exist, the frame
    owns the registry, `DevOpsManager` borrows it, and the first runtime
    surfaces (`Spellbook`, `Conduit`, `ConduitCloud`, `ConduitCluster`,
    `ConduitWard`) now create dev-ops identities and register into that frame
    registry. The mediator also registers live transaction sessions into the
    registry by request id.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:1-215
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1-565
  - src/melder/aether/aetheric_frame/aetheric_frame.py:101-129
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:83-103
  - src/melder/aether/spellbook/spellbook.py:199-220
  - src/melder/aether/conduit/conduit.py:249-266
  - src/melder/aether/aetheric_frame/conduit_cloud.py:83-101
  - src/melder/aether/conduit/conduit_cluster.py:84-103
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:190-205
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:179-190
  IMPACT: The topology/transaction registry layer now exists before the
    strategy redesign, so later transaction policy work can resolve affected
    objects from one frame-owned dev-ops surface instead of scattered runtime
    lookups.
  NEXT: run a narrow compile-surface check, then stop and review the landed
    registry/identity shape before wiring more behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T22:40:58Z
  TYPE: FACT
  CLAIM: The new registry/identity layer parses, but the new docstrings are
    uneven and need a cleanup pass. The current `DevopsInformationRegistry`
    and `DevopsIdentity` surfaces describe the right objects, but several
    method docstrings are thinner than the active Python overlay requires and
    some wording does not yet clearly explain cleanup/registration ordering.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1-565
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:1-246
  - src/melder/aether/aetheric_frame/aetheric_frame.py:101-150
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:53-222
  IMPACT: Before we widen this registry slice, the new public/dev-ops-facing
    surfaces need rich, contract-first docstrings that match the actual frame
    ownership and cleanup model we just landed.
  NEXT: tighten the registry/identity/owner docstrings, then rerun a narrow
    compile check only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T22:40:58Z
  TYPE: MEASURE
  CLAIM: The registry/identity source surface now has richer contract-first
    docstrings on the new objects and their new owner accessors, and the
    touched file set still passes a narrow `py_compile` sanity check after the
    rename and wiring changes.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:1-246
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1-565
  - src/melder/aether/aetheric_frame/aetheric_frame.py:21-414
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:21-222
  IMPACT: The registry/identity layer is now in a better state for design
    review without widening into behavior changes or pretending full runtime
    validation already happened.
  NEXT: stop here for review unless you want the next slice to wire additional
    object registrations or transaction-consumer lookups into the registry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T22:40:58Z
  TYPE: FACT
  CLAIM: The explicit `register_spellbook_conduit_relation(...)` API was the
    wrong owner. Spellbook<->conduit ownership is now being pushed toward
    identity-derived registry state instead: the registry rebuilds that
    relation from registered `spellbook` and `conduit` identity metadata, and
    `DevopsIdentity.update_metadata(...)` now refreshes the derived relation
    map when object metadata changes.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:161-347
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:530-554
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:184-196
  - src/melder/aether/conduit/conduit.py:250-265
  IMPACT: This removes one chunk of explicit relation bookkeeping from the
    runtime surface and moves ownership mapping into the identity/registry
    layer where it belongs.
  NEXT: re-run the narrow compile-surface check and then stop for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T22:40:58Z
  TYPE: FACT
  CLAIM: The borrowed registry reference is now wired through the main dev-ops
    manager layer. `SpellSystemStates`, `IncidentManager`, `RiskManager`, and
    `ChangeControlManager` now all receive the same frame-owned
    `DevOpsInformationRegistry`, while `DevOpsManager` passes that borrowed
    reference through instead of creating its own registry.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:111-129
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:91-111
  - src/melder/aether/aetheric_frame/dev_ops/incident_manager/incident_manager.py:18-96
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:51-112
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:42-114
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:61-122
  IMPACT: The frame topology/transaction registry is now a first-class
    borrowed dependency across the dev-ops layer instead of only existing at
    the frame and mediator edges.
  NEXT: rerun the narrow compile check and stop for review of the current
    wiring before widening into more registry consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T23:05:36Z
  TYPE: FACT
  CLAIM: The next three cleanup steps are concrete now. `Spellbook` already
    advertises only `bind`/`scan`, but `Conduit` still incorrectly advertises
    `mutation` and `cluster_link`; link relation ownership still enters the
    registry from `Spellbook._create_link_contract/_sever_link_contract`
    instead of `ConduitWard._create_new_contract/_remove_contract`; and the
    registry still lacks object-returning convenience queries for strategy
    consumers even though the underlying maps and transaction indexes already
    exist.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1750-1830
  - src/melder/aether/spellbook/spellbook.py:2008-2088
  - src/melder/aether/conduit/conduit.py:744-782
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:781-838
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:959-1005
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:490-940
  IMPACT: We can finish identity truth and move link ownership to the real
    contract source without widening into bind strategy behavior yet, while
    also giving the future strategy layer cleaner query helpers than raw id
    maps.
  NEXT: patch conduit transaction availability, move link edge registration to
    `ConduitWard`, and add object-returning registry query helpers plus
    live-transaction object lookup by identity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T23:05:36Z
  TYPE: FACT
  CLAIM: The first three follow-up steps are now landed in source. `Conduit`
    identity truth is narrowed to `bind`, `scan`, `link`, and
    `transfer_ownership`; link relation ownership moved from `Spellbook` into
    `ConduitWard` contract create/remove; and the registry now exposes
    object-returning query helpers for spellbook ownership, provider/borrower
    edges, cluster memberships, and live transactions by identity/type.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:744-781
  - src/melder/aether/spellbook/spellbook.py:1750-1830
  - src/melder/aether/spellbook/spellbook.py:2008-2031
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:792-833
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:959-1012
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:490-892
  IMPACT: The registry is now closer to being the real topology source for
    strategy resolution instead of a passive mirror, and the remaining work can
    move into actual bind/scan strategy behavior.
  NEXT: rerun the narrow compile-surface check and then stop for review before
    touching bind/scan strategy logic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This slice is the pre-strategy registry layer. It should land the new dev-ops
registry and identity rename without widening into transaction strategy
behavior yet.

