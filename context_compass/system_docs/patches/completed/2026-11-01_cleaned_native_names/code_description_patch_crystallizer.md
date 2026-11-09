# Persisted cleaned intent execution contract
<!-- BEGIN ENTRY: "Old and canonical cleaned-name suppression" -->
## Trigger
A persisted lifecycle name crosses a record/replay boundary; a missed guard reconstructs a root.
## Control flow
Keep journal fold unchanged. With no singleton twin, return as before. With a twin and final state
equal to exact cleaned or CLEANED, add the original named shortfall and return before configuration,
activation or composition. Otherwise run the existing enabled/disabled replay unchanged.
## Errors and rollback
Keep record-major admission and the engine's reverse teardown on actual failures; no bypass.
Canonical serialization stays generic state.name, and RecordedUnitState.value stays cleaned.
## Invariants and idempotency
Both sequential and parallel replay call these same guarded stages. Final state wins; no root is
reconstructed for either cleaned spelling. No guarantee of touching an existing live owner is added.
## Non-goals
No general string normalization, fold rewrite, record version change or transfer/disposal change.
## Validation focus
Actual valid-major5 cached loads for legacy and canonical state names, original shortfalls and
zero reconstructed roots, enabled/disabled and later-wins controls, plus canonical capture.
<!-- END ENTRY: "Old and canonical cleaned-name suppression" -->
