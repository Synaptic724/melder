# Epic: Reusable Lesser Runtime Pooling
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Epic ID: EPIC-2026-05-24-reusable-lesser-runtime-pooling
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-24T16:22:21Z
- Updated: 2026-05-30T15:06:13Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder runtime reuse and pooling

## Problem / Opportunity
Lesser-conduit creation and destruction are still expensive enough that we need a
real reuse model instead of relying on micro-optimizations. The code now has:
- a working pooled `SpellSpace` seam,
- a root-owned `ConduitPool` field wired into `Conduit`,
- a hard cleanup lane for conduits,
- but no reusable lesser-conduit reset lane yet.

The next step is not more local speed trivia. It is a coherent runtime reuse
model where root-owned pools can retain expensive lesser shells and return them
to service safely.

## MRP Alignment (Most Reasonable Product)
The MRP here is not "generic pooling." It is a trustworthy runtime lifecycle:
- root conduits stay authoritative and unpooled by default,
- lesser conduits can be retained and reused,
- reset work is explicit and bounded,
- hard destroy still exists and stays deterministic,
- subtree cleanup and pool return remain coherent under real lineage structure.

That gives us the minimum durable foundation for later elastic tuning without
shipping a trap.

## Ticket Contract
- ENTRY_GATE: current pooling lanes are routed and the user explicitly asked for one compaction-safe umbrella epic.
- EXECUTION_BOUNDARY: pooled spellspace semantics, root-owned conduit pooling, lesser reset semantics, lineage detach/re-attach, and Nexus/dev-ops reporting that directly depends on that lifecycle.
- DEPENDENCIES: `tickets/tasks/2026-05-24_prepare_spellspace_for_pooling_task.md`, `tickets/tasks/2026-05-24_start_conduit_pool_task.md`, `system_docs/src_architecture.md`, `system_docs/src_components.md`, `system_docs/readable_src_graph.json`.
- EXIT_GATE: root-owned pooling, lesser reset lane, recursive subtree pooling, and hard-destroy teardown all have accepted stories/tasks and board sync is complete.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the reset lane requires public API changes or if `CreationGate` must gain a new runtime reset contract.

## Goals (Outcomes)
- Define a root-owned pooling model for lesser conduits that does not pool root conduits by default.
- Make the lesser cleanup reset lane explicit and separate from hard destroy.
- Preserve expensive conduit-owned runtime shells across lesser reuse.
- Keep hard destroy deterministic for frame/root teardown.
- Keep compaction-safe durable context in one top-level planning document.

## Non-Goals (Explicit Exclusions)
- No percentage-based pool tuning work in this epic.
- No gate pooling redesign in this epic.
- No root-conduit pooling by default.
- No broad refactor of unrelated dev-ops or transaction systems.

## Scope Boundaries
- In scope:
  - root-owned `ConduitPool` lifecycle
  - lesser-conduit reset semantics
  - recursive subtree pooling of lesser descendants
  - `ConduitWard` detach/reset helpers
  - `Creations` non-destructive reset helpers
  - spellspace reset interaction with conduit pooling
  - Nexus/dev-ops reporting that depends on pooled lesser state
- Out of scope:
  - root pooling
  - elastic heuristics beyond the currently agreed defaults
  - unrelated AR/viewer design work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user asked for one epic that captures the pooled-lesser runtime plan before the next compaction cycle.

## Success Metrics
- Root conduits own one `ConduitPool` and all lessers use that shared pool reference.
- Lesser `cleanup()` performs reset/pool-return instead of hard destruction.
- Root/frame teardown still permanently destroys pooled lessers.
- Subtree cleanup of nested lessers returns the whole descendant set to the root-owned pool.
- Full pytest remains green after each accepted slice.

## Requirements (Functional + Non-Functional)
- Functional:
  - Root-owned pool must be present on every conduit object.
  - Direct lesser construction and `create_lesser_conduit(...)` must both resolve the same root-owned pool.
  - Lesser reset must detach lineage and clear live runtime state without deleting the shell.
  - Hard destroy must remain available through `permanent_cleanup()`.
- Non-functional:
  - No extra defensive branching in the cleanup router beyond the permanent flag.
  - No local alias clutter in hot/reset paths without a measured reason.
  - No regression in thread-safety; nogil frame rules remain in force.

## Constraints / Assumptions
- Root conduits are not pooled by default.
- `ConduitCloud` is normal/root-only by contract.
- Cluster operations are normal-only by contract.
- `CreationGate` can be retained unless reuse proves it needs a new explicit reset contract.
- The current soft/hard split for `SpellSpace` is the model we mirror, but not blindly.

## Dependencies / External References
- `codex/context_compass/tickets/tasks/2026-05-24_prepare_spellspace_for_pooling_task.md`
- `codex/context_compass/tickets/tasks/2026-05-24_start_conduit_pool_task.md`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/aether/conduit/conduit_pool.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Root-Owned Pool Contract
  - Root conduits own the pool, lessers always receive the shared root-owned pool reference, and the full suite stays green.
- [ ] Milestone 2: Reusable Lesser Reset Lane
  - Lesser cleanup resets and returns to pool without destroying the shell, and recursive descendant pooling is coherent.
- [ ] Milestone 3: Hard Destroy / Reporting Alignment
  - Root/frame teardown still permanently destroys pooled lessers and reporting surfaces stay truthful.

## Stories (Required to Complete)
- [ ] Story: TBD - Define lesser-conduit reset contract and descendant subtree pooling.
- [ ] Story: TBD - Add non-destructive `Creations` reset and spellspace reset interplay.
- [ ] Story: TBD - Add `ConduitWard` detach/reset helpers and parent/root re-attach flow.
- [ ] Story: TBD - Align Nexus/dev-ops reporting with pooled lesser runtime truth.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Keep root-owned `ConduitPool` mandatory on all conduit objects.
- [ ] Task: Preserve the hard-destroy lane and route root/frame teardown through `permanent_cleanup()`.
- [ ] Task: Verify every slice against the full pytest suite.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Root conduits own one `ConduitPool`, and all lesser conduits share it.
- Lesser cleanup uses a real reset lane instead of destructive teardown.
- Descendant lessers pool recursively when a lesser subtree is cleaned.
- Hard-destroy callsites use `permanent_cleanup()` where runtime teardown truly means destruction.
- Nexus/dev-ops state remains internally consistent after pooling slices land.

## Risks / Mitigations
- Risk: Reset lane leaves stale lineage or creation state alive.
  - Mitigation: implement reset helpers at the real state owners (`ConduitWard`, `Creations`, spellspace handling) instead of faking reset in the pool.
- Risk: `CreationGate` turns out to need an explicit reset contract.
  - Mitigation: keep the first reuse slice gate-retaining and raise a bounded follow-up if reuse proves it unsafe.
- Risk: Cleanup contract drift breaks existing runtime teardown semantics.
  - Mitigation: keep `permanent_cleanup()` as the hard lane and validate with full pytest after each slice.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Use focused unit/component/integration files for each pooling slice first.
- Run the full pytest suite after any change that touches cleanup routing, lineage detach, or root/frame teardown.
- Preserve truthful reporting: if full validation was not run for a slice, state that explicitly.

## Rollout / Adoption Plan
- Land root-owned pool ownership first.
- Land lesser reset helpers second.
- Land recursive subtree pooling third.
- Land reporting alignment last.
- Keep root pooling out of the rollout until lesser pooling is stable.

## Open Questions
- Do we need a dedicated pooled-lesser conduit state for reporting, or can the pool own that state alone?
- Does `CreationGate` need a reusable reset method, or is retaining the live gate enough?
- Should Nexus continue publishing pooled lessers as descriptor-visible objects, or should pooled state remain internal?

## Decision Log
- Root conduits are not pooled by default.
- Root-owned `ConduitPool` is mandatory on all conduit objects.
- Cleanup routing should branch on the permanent flag, not on conduit state.
- `ConduitCloud` remains normal/root-only.
- Cluster operations are normal-only.
- Hard cleanup already exists; the open design problem is the reset lane.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: after the reusable lesser runtime model is accepted and split into child stories/tasks

## Notes
- DATETIME: 2026-05-24T16:22:21Z
  TYPE: FACT
  CLAIM: Root-owned conduit pooling is now partially wired. `ConduitPool` exists, root/normal conduits create it, and lesser conduits carry the root-owned pool reference. The unresolved problem is not pool ownership anymore; it is the lesser reset lane.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:112-128
  - src/melder/aether/conduit/conduit.py:273-305
  - src/melder/aether/conduit/conduit.py:1543-1660
  - src/melder/aether/conduit/conduit_pool.py:1-84
  IMPACT: The next slices should focus on reset semantics, not on who owns the pool.
  NEXT: define the reusable lesser reset lane and descendant subtree pooling behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T16:22:21Z
  TYPE: DECISION
  CLAIM: Root/frame teardown now routes through hard destroy rather than the soft cleanup lane. This keeps the current cleanup split coherent while we build the lesser reset path.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:349-553
  - src/melder/aether/aetheric_frame/aetheric_frame.py:214-223
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:279-332
  - src/melder/nexus/nexus_frame_manager.py:313-322
  IMPACT: We can safely design the lesser reset lane without losing the existing hard-destroy semantics for root/frame teardown.
  NEXT: define what `ConduitWard`, `Creations`, and spellspace reset must do in the soft lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T17:19:14Z
  TYPE: FACT
  CLAIM: The current pool seam has two immediate correctness gaps before wider lesser reset work continues: a drained `CreationGate` cannot be reopened for pooled reuse because `open()` never clears `_closed`, and `upgrade_to_normal(...)` leaves an upgraded conduit attached to the old root-owned `ConduitPool` instead of giving the new normal root its own pool.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:123-149
  - src/melder/utilities/synchronization/creation_gate.py:328-375
  - src/melder/aether/conduit/conduit.py:1525-1549
  - src/melder/aether/conduit/conduit.py:1678-1719
  IMPACT: Reused pooled lessers can stay terminally gate-closed after a lineage drain, and upgraded normals keep the wrong pool ownership surface.
  NEXT: patch gate reopen semantics, assign a fresh root-owned `ConduitPool` during lesser->normal upgrade, and add focused tests for both seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T17:20:47Z
  TYPE: MEASURE
  CLAIM: The gate-reopen and upgraded-root-pool fixes are landed and green. `CreationGate.open()` now clears terminal closed state so pooled lesser gates can be reused, and `upgrade_to_normal(...)` now assigns a fresh root-owned `ConduitPool` to the upgraded conduit instead of leaving it attached to the former root pool.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:123-149
  - src/melder/aether/conduit/conduit.py:1516-1530
  - tests/unit/melder/utilities/synchronization/test_creation_gate.py:250-267
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:275-313
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\synchronization\test_creation_gate.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit`
  IMPACT: Reused pooled lessers can reopen retained gates correctly, and a lesser promoted to normal now owns the right pool surface for future child-lesser work.
  NEXT: return to the broader lesser reset audit, starting with peer-contract state and meld cache reset on the soft pool lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T17:20:47Z
  TYPE: FACT
  CLAIM: After rereading `CreationGate` and its controller tests, terminal close is intentional permanent semantics. The wrong assumption was in the pooled-lesser lifecycle, not in `CreationGate`: pooled lessers must not depend on reopening a gate after `close_and_wait_until_free()`.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:23-27
  - src/melder/utilities/synchronization/creation_gate.py:330-381
  - tests/unit/melder/utilities/synchronization/test_creation_gate.py:250-298
  - tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py:236-324
  IMPACT: The right fix is to keep terminal close permanent, revert the gate change, and move temporary gate re-enable semantics onto conduit reuse instead of the gate primitive itself.
  NEXT: revert the `CreationGate.open()` semantic change and re-enable pooled lesser gates only on conduit reacquire.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T17:34:09Z
  TYPE: FACT
  CLAIM: Terminal conduit-gate close is a real intended runtime surface, not just test scaffolding. The DevOps layer exposes explicit close-and-drain APIs for one conduit and one lineage, and component/unit tests assert that these paths leave gates terminally closed afterward. Temporary pause/resume is the separate `close()` / `open()` path.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:23-27
  - src/melder/utilities/synchronization/creation_gate.py:328-381
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:276-372
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:404-472
  - src/melder/utilities/synchronization/creation_gate_controller.py:557-637
  - tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py:236-324
  - tests/component/melder/aether/dev_ops/test_dev_ops_manager_component.py:323-359
  IMPACT: Pooled lesser conduits cannot safely rely on reopening a gate after any DevOps close-and-drain path; reusable lessers must avoid those terminal APIs while they are still pool candidates.
  NEXT: audit which runtime paths can still invoke DevOps conduit/lineage drain against reusable lesser shells and wall those off from the soft pool lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T18:06:48Z
  TYPE: FACT
  CLAIM: The pooled lesser handout path is not bypassing formal peer linking. `create_lesser_conduit(...)` only reattaches lineage through `ConduitWard._link_lesser_conduit(...)`, while real peer contracts still go through `Conduit.link(...) -> ConduitWard._link(...) -> _create_new_contract(...)`, which allocates Spellbook contracted buckets and later populates them through `_add_contracted_spell(...)`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1616-1746
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:575-715
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:939-955
  - src/melder/aether/spellbook/spellbook.py:1727-2003
  IMPACT: Pool reuse only needs lineage reattachment on handout, but reset must fully sever peer-contract state first or stale `_contracts` and Spellbook contracted maps will survive into the next use.
  NEXT: design the ward reset cut so soft pooled-lesser cleanup clears peer contracts through the real sever path before lineage detachment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T18:50:00Z
  TYPE: DECISION
  CLAIM: Public conduit mutation surfaces must reject lesser conduits before any transaction, contract, mutation, or cluster machinery is touched. The direct lesser guard already exists on bind/scan/begin/end transaction, but link and transfer ownership still rely too far downstream, and mutation-research access should align to the same surface-level rule.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2022-2235
  - src/melder/aether/conduit/conduit.py:2320-2577
  - src/melder/aether/conduit/conduit.py:3078-3115
  - src/melder/aether/conduit/conduit.py:3468-3484
  - src/melder/aether/conduit/conduit_cluster.py:241-245
  - src/melder/aether/aetheric_frame/conduit_cloud.py:188-190
  IMPACT: Lesser conduits will fail consistently at the public conduit API boundary instead of leaking into mediator, contract, cluster, or mutation subsystems.
  NEXT: add one shared normal-conduit gate helper and route link, transfer ownership, and mutation-research access through it, then align focused conduit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T18:51:47Z
  TYPE: MEASURE
  CLAIM: The normal-only public conduit gate is now consistent for the requested mutation surfaces. `begin_transaction`, `end_transaction`, `bind`, `scan`, `link`, and `transfer_spell_ownership` all reject lesser conduits at the conduit API boundary before mediator, ward-contract, or cluster machinery is touched.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:884-916
  - src/melder/aether/conduit/conduit.py:2022-2448
  - src/melder/aether/conduit/conduit.py:2534-2588
  - src/melder/aether/conduit/conduit.py:3078-3144
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py
  - tests/unit/melder/aether/conduit/test_conduit_facade.py
  - tests/unit/melder/aether/conduit/test_conduit_transactions.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_contracts.py tests\unit\melder\aether\conduit\test_conduit_dynamic.py tests\unit\melder\aether\conduit\test_conduit_facade.py tests\unit\melder\aether\conduit\test_conduit_transactions.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit`
  IMPACT: Lesser conduits now fail fast at the intended public surface and no longer rely on downstream transaction or contract code to reject invalid mutation entry.
  NEXT: return to the pooled-lesser reset lane and decide what non-lineage state still has to be cleared before a lesser goes idle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T18:56:50Z
  TYPE: FACT
  CLAIM: The requested lesser-surface gate is now implemented with direct inline `ConduitState.lesser` checks rather than a helper abstraction. The public lesser failure happens immediately on begin/end transaction, bind, scan, link, transfer ownership, and mutation-research access.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2022-2448
  - src/melder/aether/conduit/conduit.py:2489-2588
  - src/melder/aether/conduit/conduit.py:3078-3144
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py
  - tests/unit/melder/aether/conduit/test_conduit_facade.py
  - tests/unit/melder/aether/conduit/test_conduit_transactions.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit`
  IMPACT: The lesser mutation-authority boundary is now enforced at the exact public surfaces you called out, without introducing an extra helper seam.
  NEXT: return to the pooled-lesser reset lane and decide what state beyond lineage/spellspace/creations must be cleared before a lesser goes idle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T19:41:32Z
  TYPE: MEASURE
  CLAIM: The pooled-lesser reporting slice is landed and full-suite green. Lesser conduit identities now attach to the devops registry, spellbook->primary-conduit mapping stays normal-only, pooled lessers advertise `ConduitState.pooled_lesser` to devops and Nexus while idle, and pooled handout restores them to `lesser` before lineage reattachment.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_state/conduit_state.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py
  - src/melder/nexus/frame_descriptor_manager.py
  - tests/unit/melder/aether/conduit/test_conduit_state.py
  - tests/unit/melder/aether/dev_ops/test_devops_information_registry.py
  - tests/unit/melder/aether/test_frame_descriptor_manager.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q`
  IMPACT: Devops and Nexus can now observe idle pooled lesser shells without confusing them for root/authority conduits, and the pooling lane has an explicit visible idle state.
  NEXT: return to the remaining soft reset work and decide whether any non-lineage runtime state beyond creations/spellspaces/hooks still needs to be cleared before pooled lesser reuse.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T20:17:30Z
  TYPE: DECISION
  CLAIM: `ConduitState.pooled_lesser` should stay a narrow lifecycle/reporting state, not a broad runtime branch target. The minimal special handling is still the same: pool transition (`lesser -> pooled_lesser -> lesser`), hard lesser cleanup routing, ward-state mirroring, the devops normal-only spellbook ownership filter, and Nexus publication. The extra runtime-specific branches that do not need it are the constructor-time lesser-like branch in `Conduit._configure_conduit_state(...)` and the explicit pooled-lesser rejection in `ConduitWard._link(...)`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:369-370
  - src/melder/aether/conduit/conduit.py:434-460
  - src/melder/aether/conduit/conduit.py:644-700
  - src/melder/aether/conduit/conduit.py:1003-1009
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:595-657
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1192-1213
  - src/melder/nexus/frame_descriptor_manager.py:332-335
  IMPACT: The pooled-lesser state stays visible where we explicitly want it, but the general runtime no longer grows extra state-specific branches that should never matter after the conduit is handed back out of the pool.
  NEXT: trim the two unnecessary runtime branches, rerun the focused conduit/devops/Nexus tests, and keep the rest of the pooled-lesser lifecycle surface unchanged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T20:17:30Z
  TYPE: MEASURE
  CLAIM: The pooled-lesser runtime trim is landed and the broader affected unit ring is green. The remaining explicit `pooled_lesser` handling is now the intentional lifecycle/reporting surface only: pool transition, hard lesser cleanup routing, DevOps normal-only spellbook ownership filtering, and Nexus publication. The unnecessary branches in `Conduit._configure_conduit_state(...)` and `ConduitWard._link(...)` are gone.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1003-1009
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:595-657
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1192-1213
  - src/melder/nexus/frame_descriptor_manager.py:332-335
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_lifecycle.py tests\unit\melder\aether\conduit\test_conduit_state.py tests\unit\melder\aether\conduit\conduit_ward\test_conduit_ward.py tests\unit\melder\aether\conduit\test_conduit_contracts.py tests\unit\melder\aether\dev_ops\test_devops_information_registry.py tests\unit\melder\aether\test_frame_descriptor_manager.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit tests\unit\melder\aether\dev_ops\test_devops_information_registry.py tests\unit\melder\aether\test_frame_descriptor_manager.py`
  IMPACT: The pooled-lesser state is still visible where we explicitly chose to expose it, but it no longer widens the general runtime contract surface beyond the minimum lifecycle/reporting seams.
  NEXT: return to the remaining soft lesser reset work and decide what non-lineage runtime state still needs clearing before a pooled lesser is reusable.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T20:38:59Z
  TYPE: FACT
  CLAIM: If we want DevOps to know current lesser ownership while attached, the cheapest correct implementation is a tiny lineage relation index in `DevopsInformationRegistry`, not a metadata rebuild scheme. The registry already uses set-based relation maps for provider/borrower and cluster membership, and the real attach/detach lifecycle seams are `ConduitWard._link_lesser_conduit(...)` and `_detach_for_pool()`. Because pooled lessers are guaranteed to have no parent and no child lessers, the only relation we need is active parent<->lesser membership while attached.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:617-923
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1183-1207
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:374-512
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:372-382
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:939-953
  - src/melder/aether/conduit/conduit.py:369-375
  - src/melder/aether/conduit/conduit.py:1714-1721
  - src/melder/aether/conduit/conduit.py:1759-1766
  IMPACT: The next cheap DevOps slice is localized: add parent->lesser set indexing and child->parent lookup in the registry, expose tiny conduit-identity helpers that mirror the existing provider/cluster helper style, and update the ward attach/detach paths only.
  NEXT: if we implement it, touch `devops_information_registry.py`, `devops_identity.py`, and `conduit_ward.py`, then add focused ward + registry tests for attach, detach-to-pool, and permanent cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T20:38:59Z
  TYPE: MEASURE
  CLAIM: The narrow DevOps lesser-lineage slice is landed and green. `DevopsInformationRegistry` now owns set-based parent<->lesser relation indexes, `DevopsIdentity` exposes tiny conduit-only lesser-parent wrappers, and `ConduitWard` updates the relation only on `_link_lesser_conduit(...)` attach and `_detach_for_pool()` detach. That gives DevOps current active lesser ownership while attached, and pooled lessers naturally drop the relation when returned to the pool.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:78-81
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:128-131
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:617-796
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:445-512
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:372-382
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:939-953
  - tests/unit/melder/aether/dev_ops/test_devops_information_registry.py
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\test_devops_information_registry.py tests\unit\melder\aether\conduit\conduit_ward\test_conduit_ward.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit tests\unit\melder\aether\dev_ops tests\unit\melder\aether\test_frame_descriptor_manager.py`
  IMPACT: DevOps can now answer “which active lesser is attached to which parent right now” without tracking noisy pooled lineage or widening the runtime contract beyond the attach/detach seams.
  NEXT: return to the remaining conduit reset hardening and decide whether `Meld` caches and per-conduit resolution state should be cleared on pooled lesser return.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T21:02:19Z
  TYPE: DECISION
  CLAIM: The previous DevOps lineage-index slice is too heavy for this lane. The minimal accepted shape is to keep lesser ownership as one metadata field only: `parent_conduit_id` on the existing conduit identity. That field should be updated when a lesser attaches, cleared when the lesser detaches into the pool, and otherwise left alone. No extra parent->children or child->parent registry indexes are needed because DevOps can compute anything richer later if it ever cares.
  EVIDENCE:
  - user_direction: current thread
  - src/melder/aether/conduit/conduit.py:866-895
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:343-382
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:921-958
  IMPACT: The next patch should delete the broad lineage-index idea entirely and collapse the DevOps update to one cheap metadata refresh on attach plus one cheap metadata refresh on detach.
  NEXT: add `parent_conduit_id` to `_refresh_devops_identity_state()`, move the initial refresh to a point where ward state exists, refresh the child after `_link_lesser_conduit(...)`, clear it after `_detach_for_pool()`, and run the focused conduit/devops tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T21:02:19Z
  TYPE: MEASURE
  CLAIM: The DevOps lesser-ownership slice is now reduced to the lightweight version: no new registry lineage indexes, no extra helper surface, and no broad runtime checks. The conduit identity metadata now carries `parent_conduit_id`, it is set when `_link_lesser_conduit(...)` attaches a lesser, cleared when `_detach_for_pool()` removes it, and cleared on lesser->normal upgrade. The initial identity refresh now runs after the ward exists so the metadata write order is coherent.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:250-254
  - src/melder/aether/conduit/conduit.py:319-326
  - src/melder/aether/conduit/conduit.py:866-895
  - src/melder/aether/conduit/conduit.py:1554-1559
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:375-382
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:949-955
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py
  - tests/unit/melder/aether/dev_ops/test_devops_information_registry.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\conduit_ward\test_conduit_ward.py tests\unit\melder\aether\conduit\test_conduit_dynamic.py tests\unit\melder\aether\dev_ops\test_devops_information_registry.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit tests\unit\melder\aether\dev_ops tests\unit\melder\aether\test_frame_descriptor_manager.py`
  IMPACT: DevOps can now see the only volatile lesser-ownership fact we actually care about, while the pooling lane avoids the heavier relation-index design and the extra internal-call overhead that came with it.
  NEXT: return to the remaining conduit reset hardening and re-evaluate whether `Meld` caches or conduit-local resolution state should be cleared on pooled lesser return.
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
This epic is the compaction-safe umbrella for pooled spellspace plus reusable
lesser-conduit runtime work. The hard destroy lane already exists. Root-owned
pool ownership is partially wired. The next real work is the soft lesser reset
lane: subtree pooling, `ConduitWard` detach/reset, `Creations` reset, and the
reporting decision around pooled lesser visibility.
