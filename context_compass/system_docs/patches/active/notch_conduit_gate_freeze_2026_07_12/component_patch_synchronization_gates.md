# Component Patch: Synchronization Gates (park-mode close_and_drain)

## Patch ID
notch_conduit_gate_freeze_2026_07_12

## Component
`utilities/synchronization/creation_gate.py`,
`utilities/synchronization/creation_gate_controller.py`.

## Before
- `CreationGate` freeze options are binary: `close()` parks new entrants
  but does not wait for in-flight tickets; `close_and_wait_until_free()`
  drains tickets but is TERMINAL (`_closed=True`) - waiters and later
  entrants RAISE "CreationGate is closed", and `open()` never clears
  `_closed`, so a terminally drained gate cannot be resurrected.
- The controller's only lineage drain
  (`close_and_wait_until_conduit_lineage_free`) inherits the terminal
  semantics.

## After
- NEW `CreationGate.close_and_drain(timeout=30.0, interval=0.1)`:
  `close()` semantics (enabled=False, event cleared, `_closed`
  UNTOUCHED) + the existing ticket-drain poll. New entrants park at
  `wait()`; in-flight tickets drain to zero; timeout raises RuntimeError;
  a later `open()` fully resumes parked waiters. The terminal verb is
  unchanged for shutdown consumers.
- NEW `CreationGateController.close_and_drain_conduit_lineage(root_conduit_id, timeout=30.0, interval=0.1)`:
  detached lineage snapshot walk (same shape as the terminal variant at
  :595-637) calling `close_and_drain` per gate; missing/empty root is a
  no-op.

## State/Failure Deltas
- Drain timeout raises RuntimeError naming the wait; the gate is left
  CLOSED-parked (not terminal) - the caller's reopen path (strategy
  on_end via finalize) restores admission.

## Dependency/Ordering
- Leaf-first: gate verb, then controller verb, then the DevOps facade
  verb (dev_ops_transactions component patch).

## Amendment: Ticket-First Admission (owner finding, 2026-07-12)
The original consumer protocol (check closed -> check enabled -> wait ->
register) carried a TOCTOU drain race: a drainer could disable
admission, observe zero tickets, and return while a meld that had
already passed its checks registered late and executed inside the
"drained" exclusive window. NEW `CreationGate.admit_ticket()` closes it
LOCK-FREE (owner ruling: no lock): append the ticket FIRST (visible to
every drain poll), then validate - terminal closed pops + raises;
disabled pops + parks + retries; enabled returns HOLDING the ticket.
Either the drain poll sees the ticket and waits, or the admitter's
post-append state read sees the freeze and backs out. All four
consumers (Conduit.meld, Conduit.meld_existing_spell,
CreationContext.execute, CreationContext.execute_no_hooks) replace
their check-then-register prologues with one `admit_ticket()` call +
try/finally unregister. Consumer-visible message unified to the gate's
"CreationGate is closed." (all existing tests match loosely). Note:
the Nexus-side RiftGate has its own admission shape
(command_system.py:1029) - flagged for a separate audit, not touched.

## Validation Expectations
- Gate rows: parks new waiters while frozen; drains existing tickets;
  bounded (raises at timeout); `is_closed()` stays False throughout;
  `open()` resumes a parked waiter; terminal verb behavior unchanged.
- Admission rows: admit-on-open holds one ticket; terminal refusal
  leaks no ticket; a parked admitter holds zero steady-state tickets
  through a freeze (the drain guarantee) and admits with one on open().
- Controller row: lineage walk freezes every gate under the root and
  tolerates unknown roots as no-ops.
- Consumer doubles updated: creation-context `_Gate` stub speaks
  admit_ticket; conduit facade rows assert the admit/unregister bracket.
