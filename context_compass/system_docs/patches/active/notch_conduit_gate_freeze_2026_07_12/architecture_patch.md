# Architecture Patch: Notch Conduit-Lineage Gate Freeze

## Metadata
- Patch ID: notch_conduit_gate_freeze_2026_07_12
- Status: active
- Owner: melder_0 (owner-directed design, 2026-07-12)
- Ticket: tickets/epics/2026-06-20_implement_new_mediator_strategies_epic.md
- Supersedes: remediation_lineage_mediation_2026_07_12 (reverted by owner,
  commit 7abb39e62; that design admitted the meld-side validator into the
  transaction plane - owner rejected it in favor of gate-side exclusivity)

## Objective
Close the probe-proven lineage race (a notch flipping
`SpellIndex.selected_spell_id` while a meld-time validator is in flight
writes the validator's verdict under the freshly promoted member's id,
terminally poisoning it) by giving the NOTCH transaction thread exclusive
runtime rights: its strategy freezes the affected conduits' CreationGates
(park new melds, drain in-flight meld tickets to zero) before the swap and
reopens them on every exit path. Owner ruling: conduit-lineage grain (the
conduit gate always exists and its ticket spans the whole meld, validator
included - the per-index gate is minted lazily and misses the validator);
DevOps must use DevOps tools (the strategy reaches gates only through the
DevOps-owned `ConduitLineageGateOps` facade, per the unelect precedent).

## Non-Goals
- No change to meld hot paths, `_apply_notch`, scopes, claim modes, or
  transaction types. No new mediator machinery.
- No remediation/validator participation in the transaction plane (the
  reverted design; stays reverted).
- No per-spell-index gate freeze (owner: unsafe while that gate is minted
  lazily by the CreationContextFactory; a not-yet-built index has no gate
  while a validator can already be in flight).
- add_to_index / remove_from_index / transfer freezes: same pattern, later
  slice (notch is the proven attacker).

## Unchanged Invariants
- Readers-never-enter: melds/validators never take embargo claims.
- Envelope law: the strategy coordinates DevOps surfaces only; the domain
  swap stays in `Spellbook._apply_notch` inside the held window.
- Notch seal (spellbook + conduits + binding key, EXCLUSIVE) unchanged.
- LoadGate semantics unchanged (freeze is orthogonal; a notch during a
  world load still parks at `wait_for_passage` before any freeze).
- `CreationGate.close_and_wait_until_free` keeps its terminal semantics
  for shutdown consumers.

## Changed Components
1. `utilities/synchronization/creation_gate.py` - NEW `close_and_drain`:
   PARK-mode freeze (close() + poll tickets to zero, bounded; `_closed`
   untouched so `open()` fully resumes). The existing terminal verb stays.
2. `utilities/synchronization/creation_gate_controller.py` - NEW
   `close_and_drain_conduit_lineage(root_conduit_id, timeout, interval)`:
   lineage-snapshot walk calling the park-mode verb per gate.
3. `aether/aetheric_frame/dev_ops/conduit_lineage_gate_ops.py` - NEW
   `quiesce_conduit_lineage(root_conduit_id, timeout, interval)`: the
   DevOps facade verb strategies use (reopen stays
   `enable_conduit_lineage`).
4. `.../strategies/notch_transaction_strategy.py` - `build_start_plan`
   stashes the sealed conduit set as `quiesce_root_conduit_ids` in
   normalized metadata; `on_start` quiesces each lineage via the
   metadata-carried `conduit_lineage_gate_ops` facade (absent facade =
   no-op, unelect precedent); `on_end` reopens each (fail-closed).
5. `aether/conduit/conduit.py::notch_spell` - metadata gains
   `conduit_lineage_gate_ops` (frame DevOps facade; mirrors
   conduit_cluster.py:868).
6. `.../transaction_manager/transaction_mediator.py` - strategy `on_end`
   dispatch RELOCATES into `_finalize_root_session` (fires exactly once
   per root end - commit, abort, or error). The dispatch in
   `end_transaction_for_identity`'s finally and the explicit dispatch on
   the `_start_strategy_transaction` failure path are removed (both are
   covered by finalize; keeping them would double-fire). Evidence that
   relocation is behavior-safe: every registered strategy's `on_end` is a
   documented no-op EXCEPT unelect's reopen, which today never fires on
   the success path (latent leak; this fix heals it), and
   `end_transaction_for_identity`'s only callers are the spellbook bind
   wrappers (spellbook.py:3822,:5521) whose family on_end is a no-op.

## Interface Deltas (all additive except the dispatch relocation)
- `CreationGate.close_and_drain(timeout: float = 30.0, interval: float = 0.1) -> None`
- `CreationGateController.close_and_drain_conduit_lineage(root_conduit_id: str, timeout: float = 30.0, interval: float = 0.1) -> None`
- `ConduitLineageGateOps.quiesce_conduit_lineage(root_conduit_id: str, timeout: float = 30.0, interval: float = 0.1) -> None`
- Notch metadata contract gains optional `conduit_lineage_gate_ops`;
  normalized plan metadata gains `quiesce_root_conduit_ids: tuple[str, ...]`.

## Concurrency Contract (the freeze)
- Order per notch: admit (claims held) -> on_start quiesce (park + drain,
  30s/gate bound; timeout raises -> start-failure abort reopens) ->
  domain swap (`_apply_notch`) -> commit -> finalize dispatches on_end ->
  reopen. In-flight melds (validator included - the conduit ticket spans
  the whole meld, conduit.py:3592-3603) complete BEFORE the swap, so
  verdicts land under the pre-flip selected id; melds arriving mid-window
  park at `CreationGate.wait()` and resume post-reopen against post-notch
  truth (park point precedes spell resolution, so no stale spell in hand).
- Self-deadlock (notch from inside a meld hook on the same lineage): the
  drain waits on its own thread's ticket -> bounded timeout ->
  teach-grade RuntimeError -> abort path reopens. Documented refusal.
- No AB-BA: the freeze holds no runtime locks while waiting (gate close is
  lock-brief; the drain is a poll); melds hold no embargo claims.

## Migration Order
1. Gate verb -> controller verb -> facade verb (leaf-first, additive).
2. Mediator on_end dispatch relocation (+ removal of the two old sites).
3. Notch strategy freeze + caller metadata line.
4. Tests; probe docstring truth-sync (regression monitor contract).

## Rollback
Reverse order; every delta is additive except the dispatch relocation,
which reverts to the two original dispatch sites.

## Validation Expectations
- Unit: gate park+drain contract (parks, drains, bounded, non-terminal,
  reopenable); controller lineage walk; facade delegation; strategy
  on_start/on_end freeze contract (recording fake facade); mediator
  dispatches on_end exactly once on commit AND on abort, never twice.
- Acceptance: tests/integration/melder/aether/conduit/
  test_lineage_remediation_notch_race.py flips green ("notch PARKED
  behind the window" is a documented legal shape; drain bound 30s covers
  the probe's 15s barrier).
- Agent: AST/pytest Not run (3.14t owner-run; sandbox cannot import
  melder). All seams file-tool verified.

## Coverage Matrix
- Race both directions: validator-first (drain waits it out) and
  notch-first (later melds park at entry). Probe covers the straddle;
  sequential control covers the harness invariant.
