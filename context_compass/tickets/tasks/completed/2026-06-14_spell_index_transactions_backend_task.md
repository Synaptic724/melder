# Task: SpellIndex transactions — mediator backend (notch / add / remove)

## Metadata
- Task ID: TASK-2026-06-14-spell-index-transactions-backend
- Story: none (serves the SpellIndex multi-member model lane)
- Status: in_progress
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p1
- Created: 2026-06-14T21:19:47Z
- Updated: 2026-06-14T21:19:47Z

## Objective
Land the mediator/transaction BACKEND for the three SpellIndex operations the
user specified, so general_0's SpellIndex multi-member model lane can plug its
member-store ops into ready transaction windows. Backend only; the member-store
mutation is left as three seam hooks for general_0.

## Design (user-locked)
- Every spell is always in exactly one index; exclusive membership; only the
  active (notched) member is live; no empty index except transiently inside a
  transaction. (general_0's lane: tickets/tasks/2026-06-12_spell_index_lineage_separation_map_task.md)
- THE SEAL (user, 2026-06-14): each index op claims, all EXCLUSIVE,
  - the owning spellbook scope  -> blocks bind/new-spell, transfer, other index ops
  - the owning conduit scope    -> blocks link / sever / cluster / transfer
  - the targeted binding key     -> the resolution location
  isolated to exactly those spellbook(s)+conduit(s); the rest of the frame runs
  free. add_to_index seals BOTH source and target sides.
- No `make_scope_key_index` was needed: spellbook-X already serializes every
  structural op on that book, so concurrent same-index corruption is impossible.

## What landed (this lane)
- Enum: ChangeTransactionType.NOTCH / ADD_TO_INDEX / REMOVE_FROM_INDEX.
- Strategies (claim seal): NotchTransactionStrategy, AddToIndexTransactionStrategy,
  RemoveFromIndexTransactionStrategy. Registered in TransactionStrategyBuilder;
  allow-listed in TransactionMediator.start_transaction.
- Spellbook entry methods (admit -> seam -> commit):
  notch_spell(spell_index, member);
  add_spell_into_spellindex(spell, target_index, source_index=None);
  remove_spell_from_spellindex(spell, source_index).
- Conduit facades for all three.
- Unit tests: claim-set seal tests for all three + builder.resolve asserts.

## SEAM CONTRACT for general_0 (the three `_apply_*` on Spellbook)
All run INSIDE the held transaction window (scopes claimed, race-safe). All
currently raise NotImplementedError.
- `_apply_notch(*, spell_index, member)`: make `member` the active member of
  `spell_index`; de-register the outgoing active SHA + register the incoming in
  the id maps; bump `Spell._door_epoch`.
- `_apply_add_to_index(*, spell, source_index, target_index)`: detach `spell`
  from its source index, attach to `target_index`; GC the source index if it
  empties; rekey SHA id maps + door epoch as active membership changes.
- `_apply_remove_from_index(*, spell, source_index)`: detach `spell` from
  `source_index`, mint a fresh single-member index for it; rekey + door epoch.
Commit-side fact baselines + dirty marking are already handled by the base
apply_commit_delta; the eager member-store writes belong in these seams.

## Files / Paths Impacted
- .../change_control_manager/transaction_request/transaction_request.py (enum)
- .../transaction_manager/strategies/{notch,add_to_index,remove_from_index}_transaction_strategy.py (new)
- .../transaction_manager/strategies/transaction_strategy_builder.py (register)
- .../transaction_manager/transaction_mediator.py (allow-list)
- src/melder/aether/spellbook/spellbook.py (3 entry methods + 3 seams + _spell_index_binding_key)
- src/melder/aether/conduit/conduit.py (3 facades)
- tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_strategy_builder_and_strategies.py

## Validation
- py_compile: all touched files OK (sandbox).
- Unit ring + conduit + spellbook suites: GREEN in the user's 3.14t venv (user-run).
- The three `_apply_*` seams raise NotImplementedError, so the ops are not
  callable end-to-end until general_0 implements them; nothing existing calls
  them (purely additive).

## Risks / Rollback Notes
- TOOLING: this mount intermittently truncates large-file writes mid-stream;
  every file here was written via a write-to-/tmp -> verify -> copy -> py_compile
  loop and recovered from git HEAD when the working tree was nibbled. Re-verify
  with py_compile after any further edit.

## Notes
- DATETIME: 2026-06-14T21:19:47Z
  TYPE: HANDOFF
  CLAIM: Mediator backend for the 3 SpellIndex transactions is complete and
    green. The member-store work is the three `_apply_*` seams (contract above).
    Seal = spellbook X + conduit X + binding X (add seals both sides); no index
    scope needed.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py (notch_spell / add_spell_into_spellindex / remove_spell_from_spellindex / _apply_*)
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py
  IMPACT: general_0 can implement the SpellIndex multi-member model against ready
    transaction windows.
  NEXT: general_0 implements the three seams; then end-to-end tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
