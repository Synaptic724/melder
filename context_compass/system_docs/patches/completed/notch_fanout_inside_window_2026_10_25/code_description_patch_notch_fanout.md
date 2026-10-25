# Code-description patch: the notch's borrower fan-out inside its window

## Metadata
- Patch ID: notch_fanout_inside_window_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T14:01:58Z
- Updated: 2026-10-25T14:01:58Z
- Ticket: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout, parent
  EPIC-2026-10-25-notch_fanout_inflight_melds

## Trigger justification
- The notch transaction pipeline's order changes (domain effect -> fan-out -> commit).

## Control flow
1. start_transaction (seal + quiesce of every linked lineage, on_start).
2. `_owned_notch_target`; `_spellbook._notch_spell(..., after_switch=fan_out)`: switch, check, then fan-out
   (deactivate outgoing on peers, activate incoming on peers, ward emission), then the research journal.
3. Exception: `_notch_spell` has reverted the Book; if the fan-out started, `_undo_borrower_fan_out`; end_transaction
   failed (on_end reopens); re-raise.
4. Success: end_transaction success (commit hooks, on_end reopens the gates).

## Edge and error semantics
- No fan-out when there is no outgoing version or the notch is a no-op. An undo error raises RuntimeError chained to it.

## Invariants and idempotency
- The peer flips are idempotent; the inverse emission is the forward emission with the ids swapped.

## Explicit non-goals
- Changing meld-side refusals.
