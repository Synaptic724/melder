# Qualified spell-name collisions: validation control flow

## Trigger
This changes a validation gate and its pass-scoped memoization semantics.

## Control flow
Check cancellation and required context; preserve the existing nameless guard. Derive the target's
canonical address. Reuse the current pass's address map or build it from a copy of the visible pool.
Derive each named entry's address with the same helper and append its existing diagnostic metadata.
Publish a completed map to the pass cache. Emit one error only when the target address has multiple
visible entries; include that address and guidance to change its frame or binding.

## Edge and error behavior
Without a pass cache, calculate fresh. With a cache, share only within that validation pass. Preserve
cancelled and cleaned-state exceptions; do not catch normalization errors or mutate registrations.

## Invariants and idempotency
Two spell names at one explicit address collide; one name at two addresses does not. Default/explicit
__default__ bindings and case variants agree. The strategy appends diagnostics, never renames spells.

## Non-goals
No class identity lookup, class-to-registration index, shadowing rules, new configuration or hot-path work.

## Validation focus
Exercise cache/no-cache results, normalized genuine collisions and fully wired qualified resolutions.
