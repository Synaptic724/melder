# Code-description patch: configuration default and reload accounting

## Trigger justification
An eager default interacts with write-once properties, clearing, and recorded-value diagnostics.
The required policy is small but crosses more than the fluent setter.

## Control-flow description
1. Initialize the property map with the new False value and register its bool type.
2. Clear returns the map to that same early-default state.
3. Normal defaults fill missing keys; optional validation defaults include the flag too.
4. The new fluent method stores its argument through the existing setter and returns self.
5. Reload applies recorded values through the existing property API.
6. Before existing backfill comparison, remove the eager flag from the accounted-present
   keys when it was absent from the record and its current value is still False.
7. Existing default loading, sorted backfill reporting, validation, and freeze then complete.

## Edge / error behavior and rollback semantics
- Recorded True/False is never reported as defaulted.
- Missing recorded flag on a fresh or cleared configuration returns False plus backfill evidence.
- Preserve an existing non-default True when reload has no replacement, consistent with current
  populate-missing behavior. No additional provenance state is required.
- Non-bool values retain current generic validation failure timing; no coercion is added.
- Existing cleaned/frozen refusal and best-effort rejected-key collection are not redesigned.

## Invariants and idempotency expectations
- Default loading never blocks later explicit priority selection before freeze.
- Repeated valid setup writes are allowed; finalized configuration refuses them.
- Matching and priority application belong to later Bind implementation, never the reload loop.
- Existing key-set accounting is a diagnostic value boundary, not a copy of a live disposal list.

## Explicit non-goals
No Bind/Spell changes, runtime method lookup, cleanup alteration, schema-wide refactor,
new root configuration fields, record migration, or source/repository asset format change.

## Validation focus points
Exercise raw initialization, clear/reassembly, defaults before/after setter, defaults-free
finalization, invalid bool values, recorded True/False, missing-record backfill, preserved
preconfigured True, and frozen/cleaned public setters.
