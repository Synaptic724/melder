# Component patch: Ownership transfer - instances move by default (slotted_lifetime_ownership_2026_10_14)

Components: Conduit Runtime (`transfer_spell_ownership`), ConduitWard and Contracts (`_transfer_spell_ownership`,
`TransferOfOwnership`). Defect D3 (transfer half), rescoped by the owner on 2026-10-14 (epic Decision Log, "transfer
default"); D4 (children move with a moved holder) landed in 0.2.8238 through the Creations rows.

## Before / after
- Before: `transfer_spell_ownership(..., move_creations=False)` by default. The transfer moves the spell (the whole
  index, the registry entry, the owner pointer and owner store, borrowers), and `_teardown_creations` takes the active
  member's entries out of the source store, keeps them only for rollback and moves them nowhere: a transferred
  `unique` is rebuilt by the target as a second instance while whatever already held the first keeps it, and no
  `close` ever runs on the first (probes t3, u2). The docstrings call this tearing the source side down.
- After: the public verb (and the ward's mirror) default to `move_creations=True`: the source's instances of every
  index member move into the target's store with the spell, so a transferred `unique` stays one object (and a holder's
  adopted children move with it, 0.2.8238). `move_creations=False` keeps its behaviour as the caller's opt-out. A move
  into a slot the target already fills keeps its behaviour (the moved entry replaces it; probe m1). Lineage instances
  still never move; spellspace and cluster instances are not in a conduit's store. Nothing is disposed by a transfer.
- Docstrings (`Conduit.transfer_spell_ownership`, `ConduitWard._transfer_spell_ownership`, the `TransferOfOwnership`
  class and constructor, `_move_creations`, `_teardown_creations`) and the docs page state what each value does.
- Handover (0.2.8240, docstring and docs only, owner-directed): a transfer hands over stewardship, not a working
  setup. The spells the transferred one depends on stay with the source unless `include_dependencies` moves the
  direct ones; once the source tears down, the target can start out broken, purges what it does not want, binds
  what it needs (`UnresolvedInputError` names each missing input) and melds its own version (probe h1, h2).
- `TransferOfOwnership.__init__` keeps `move_creations=False` as its own default: the conduit and the ward always pass
  the value, and 119 unit tests construct the helper directly with the default.

## Interface deltas
Public: `Conduit.transfer_spell_ownership(move_creations=True)` (was False) - Breaking, in the release note with the
opt-out. Internal: `ConduitWard._transfer_spell_ownership(move_creations=True)`.

## State / failure deltas
- A default transfer keeps the source's instances (moved, not rebuilt); the source's teardown no longer sees them and
  the target's teardown disposes them once.
- No new failure modes; a failed transfer's rollback moves the instances back (unchanged code path).

## Dependency / ordering
None beyond the 0.2.8238 Creations rows (children travel in a holder's row).

## Validation expectations
Integration: a default transfer keeps a transferred `unique` one object (a source consumer and the target's meld
share it; disposed once, at the target's teardown, not at the source's); a tracked `many` object moves by default;
`move_creations=False` still builds a new instance on the target. The existing transfer suites run unchanged.
