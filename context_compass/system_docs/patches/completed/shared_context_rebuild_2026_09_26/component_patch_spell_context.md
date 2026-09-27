# component_patch_spell_context

## Metadata
- Patch ID: shared_context_rebuild_2026_09_26
- Component: Spell context lifecycle (Spell, CreationContextFactory, CreationContextRebuild)
- Status: active
- Updated: 2026-09-26T13:58:21Z

## Before
- Spell reached its spell-index gate only through the context being retired. A factory leader whose build
  raised left the CounterSwitch at 1, so later callers parked on the switch with no timeout until some reset.
- CreationContextRebuild existed in src, unused, and depended on Spell fields that did not exist; its publish
  step marked plan-less spells resolution_required, which today routes a lane that cannot compile them.

## After
- Spell: `_creation_gate` (set by `_configure_creation_context_factory` from
  `CreationContextFactory.resolve_spell_index_gate`; None in automatic mode; dropped with the factory) and
  `_creation_context_failure`; both appended last in `__slots__` and deleted in cleanup.
- Factory: leader failure records the cause on the spell, releases its claim (1 -> 0) and re-raises; success
  clears the recorded cause; a follower woken with nothing published raises RuntimeError chained from it.
- CreationContextRebuild: publishes only spells whose plan is present, leaves resolution flags to producers,
  drains with a 1 ms poll (rare path; the 100 ms default doubled the concurrency file's run time).

## Interface Deltas
- `CreationContextFactory.resolve_spell_index_gate(spell) -> Optional[CreationGate]`.

## State and Failure Deltas
- No pending state without a live builder. A failed rebuild window records its cause for unpublished spells,
  idles the switch and reopens the gate.

## Validation Expectations
- Factory unit tests: failed leader records and releases, follower reports the cause, parked follower wakes
  when the leader fails, success clears the cause, gate resolution per mode.
- test_creation_context_rebuild.py: drain before enter, publish before reopen, no publish without a plan,
  context kept when not reset, failure recording, posture restore, index-ordered locks, entry-failure unwind.
- Spell unit tests: gate set in dynamic, unset in automatic, dropped with the factory.
