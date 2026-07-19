# Component Patch: Conduit

## Before
- conduit wraps spell-index spell lookup with an extra read-side lock
- `Conduit.meld(...)` cannot request reuse-or-fail explicitly

## After
- conduit no longer adds the extra read-side wrapper lock on spell-index lookup
- `Conduit.meld(...)` passes `existing_only` through to `Meld`

## Interface Deltas
- `Conduit.meld(...)` gains `existing_only`

## State / Failure Deltas
- spell-index lookup read path is thinner
- conduit callers can explicitly request existing-only reuse without triggering
  creation
