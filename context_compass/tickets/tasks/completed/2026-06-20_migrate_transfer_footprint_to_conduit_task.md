# Task: Migrate transfer-ownership footprint discovery from the strategy into the Conduit

## Metadata
- Task ID: TASK-2026-06-20-migrate-transfer-footprint-to-conduit
- Story: UNKNOWN (standalone migration task)
- Status: review
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p2
- Created: 2026-06-20T15:29:07Z
- Updated: 2026-06-20T18:57:00Z

## Objective
Make `TransferOwnershipTransactionStrategy` envelope-only (DevOps scope isolation only) by MOVING
the existing footprint-discovery code (live-object reach) out of the strategy and into the Conduit
call site that already owns the `TRANSFER_OWNERSHIP` transaction. No new logic — migrate + rewire.

## Ticket Contract
- ENTRY_GATE: active board row routes here; the transaction lives in `conduit.transfer_spell_ownership`
  (conduit.py:2849), metadata is built in `_build_transfer_transaction_metadata` (conduit.py:2871),
  and the Conduit has `self._aetheric_frame.devops_information_registry` (conduit.py:375).
- EXECUTION_BOUNDARY: `conduit.py` (the metadata builder + migrated private helpers),
  `transfer_ownership_transaction_strategy.py` (strip the 4 runtime reaches, read metadata), and the
  transfer strategy unit tests. No behavior change to the transfer itself.
- DEPENDENCIES: `TransferOfOwnership._build_preflight_summary` (read-only; transfer_of_ownership.py:259).
- EXIT_GATE: strategy uses ZERO live-object reach (no get_object, no live spell, no TransferOfOwnership);
  the Conduit builds the full footprint into metadata; user-run 3.14t suite green.
- FAILURE_ESCALATION: CONFLICT if a moved method needs runtime state the Conduit cannot supply;
  BLOCKER on an import cycle (use a local import in the metadata builder).

## What reaches into the runtime today (the 4 violations in the strategy)
- `_resolve_conduit_object` -> `registry.get_object(conduit)` for source + target (strategy.py:84-94).
- `_resolve_transfer_spell` -> `source_conduit.get_spell_by_*` (strategy.py:95-98).
- `TransferOfOwnership(...)._build_preflight_summary(spell_obj)` (strategy.py:110-123).
- `_collect_cluster_memberships` -> `registry.get_object(conduit_cluster).get_members()` (strategy.py:425-431).

## Migration map (move, don't rewrite)
- MOVE strategy -> Conduit (private helpers, registry param -> `self._aetheric_frame.devops_information_registry`;
  source = self, target = target_conduit, spell resolved via self.get_spell_by_*):
  `_resolve_transfer_spell`, `_resolve_spellbook_id_for_conduit`, `_collect_cluster_memberships`,
  `_collect_borrower_participants`, `_normalize_borrower_metadata`, and the `_build_preflight_summary` call.
- Conduit `_build_transfer_transaction_metadata` stamps the full footprint into metadata:
  `participant_conduit_ids`, `affected_cluster_ids`, `affected_identity_keys`, `source_spellbook_id`,
  `target_spellbook_id`, `binding_key`, `preflight_borrowers`, `preflight_dependencies`,
  `spell_id`, `spell_index_id`.
- KEEP in strategy (DevOps scope assembly): the `make_scope_key_*` loop, `_collect_spellbook_ids_from_identities`,
  `_add_transaction_owner_scopes`. Strategy reads the footprint from metadata; deletes the 4 reaches.

## Steps / Checklist
- [x] Stage 1: Conduit migration — `_build_transfer_transaction_metadata` resolves the live spell,
      runs the read-only `_build_preflight_summary`, and collects the footprint via the migrated
      `_resolve_transfer_spell`/`_resolve_spellbook_id_for_conduit`/`_collect_cluster_memberships`/
      `_collect_borrower_participants`/`_normalize_borrower_metadata` (registry =
      `self._aetheric_frame.devops_information_registry`; local import of TransferOfOwnership).
      conduit.py:2880-3231 (verified via Grep; bash py_compile is the stale mount).
- [x] Stage 2: Strategy slim-down — `build_start_plan` reads the footprint from metadata and builds
      scopes only; the 4 runtime reaches + 5 helpers + the TransferOfOwnership/Conduit/Spell imports
      are gone. The strategy no longer even imports a runtime type.
- [x] Stage 3: Strategy unit tests — replaced the live-object preflight test with a metadata-driven
      scope test + a missing-footprint guard test; removed the now-orphaned `patch` import + `_FakeCluster`.
- [x] Run Ticket Microcycle; findings documented in Notes.

## Deliverables
- Envelope-only `TransferOwnershipTransactionStrategy`; footprint discovery owned by the Conduit.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py
- src/.../change_control_manager/transaction_manager/strategies/transfer_ownership_transaction_strategy.py
- tests/unit/.../change_control_manager/test_transaction_strategy_builder_and_strategies.py

## Validation
- Not run (agent: Py3.10 sandbox cannot import the 3.14t chain).
- Recommended: `pytest tests/unit/melder/aether/dev_ops/change_control_manager -q` on .venv_new.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: direction confirmed by user (transaction lives in Conduit -> footprint discovery
  belongs there); migration map grounded in source evidence.

## Notes
- DATETIME: 2026-06-20T15:29:07Z
  TYPE: DECISION
  CLAIM: Footprint discovery (live spell + preflight borrowers/deps + cluster members) moves into the
    Conduit metadata builder (domain side, runs before the transaction opens), where it is allowed to
    reach the runtime. The strategy becomes metadata-only scope assembly. Staged conduit-first (safe:
    strategy keeps its own discovery until Stage 2, only metadata grows).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2849-2953
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transfer_ownership_transaction_strategy.py:84-176
  IMPACT: Removes the DevOps-purity violation from the last reaching strategy.
  NEXT: Stage 1 conduit edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-20T18:57:00Z
  TYPE: FIX
  CLAIM: Blast-radius miss + fix. Stage 2 changed the strategy CONTRACT: the envelope strategy now
    requires the conduit-built `participant_conduit_ids` and raises without it. Stage 3 only updated the
    STRATEGY unit tests; it MISSED the pre-existing component/integration tests that open transfer via
    the low-level `begin_transaction("transfer_ownership", minimal_metadata)` / `transaction(...)`
    primitive (the old strategy self-discovered the footprint from minimal metadata; the new one cannot).
    5 session-lifecycle tests broke: component 351/407/504, integration 1099/1208. FIX (Option A): each
    now builds the footprint via `owner._build_transfer_transaction_metadata(spell=spell_id,
    target_conduit=target, move_creations=False, include_dependencies=False, force_unshare=True,
    invalidate_after_transfer=True, mark_dependencies_dirty=False)` — same call the public surface uses.
    The migration SOURCE was never wrong (every public-path `transfer_spell_ownership` test stayed green);
    only the direct-primitive callers needed the now-required footprint.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_transactions.py:381,438,542
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:1131,1245
  - src/melder/aether/conduit/conduit.py:2880 (_build_transfer_transaction_metadata)
  IMPACT: The 5 direct-entry transfer tests align with the post-migration contract.
  NEXT: User runs the 3.14t suite to confirm green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-20T18:57:00Z
  TYPE: FACT
  CLAIM: Deliberately UNTOUCHED (verified still correct post-migration): the transfer
    `respects_frame_disable_flags` tests (component 678, integration 1489) keep minimal metadata because
    the posture gate `_transaction_blocked_for_current_posture` fires INSIDE `begin_transaction`
    (conduit.py:2359) and raises "...is disabled for the current frame posture" BEFORE the strategy runs;
    and the `requires_complete_metadata` tests (component 812, integration 1775) still pass because
    incomplete metadata (no `participant_conduit_ids`) raises RuntimeError before any live session.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2359
  - tests/component/melder/aether/conduit/test_conduit_component_transactions.py:678,812
  IMPACT: Scope of the fix is exactly the 5 session-lifecycle tests; the gate/validation tests are
    unaffected by the contract change.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 6
- DATETIME: 2026-06-20T18:57:00Z
  TYPE: MEASURE
  CLAIM: Verification. Grep confirms exactly 5 `metadata=owner._build_transfer_transaction_metadata(`
    sites (component 381/438/542, integration 1131/1245). Each edit is a paren-balanced
    `metadata={...},` -> `metadata=builder(...),` swap with the call closer untouched. bash py_compile is
    UNUSABLE here: the sandbox mount serves a stale, truncated view of the integration file (it truncates
    line 1808 — an unedited requires-complete test — mid-string to `"target_conduit_`, and `cp` to /tmp
    propagates the corruption); the editor/Grep see the intact real file. pytest = Not run (agent Py3.10
    sandbox cannot import the 3.14t chain).
  EVIDENCE:
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:1808 (real
    line via editor: `if normalized_metadata.get("target_conduit_id") == "target-only":`)
  IMPACT: Edits structurally verified despite no clean bash compile signal.
  NEXT: User runs the 3.14t component + integration transfer suites.
  REREAD: HELPFUL
  SCORE_0_TO_10: 6

## Context / Handoff Summary
Migrate (not rewrite) the transfer-ownership footprint discovery from the strategy into the Conduit's
`_build_transfer_transaction_metadata`, making the strategy envelope-only. Conduit-first staging; then
slim the strategy; then update the strategy unit tests. Agent cannot run pytest; user runs 3.14t.
