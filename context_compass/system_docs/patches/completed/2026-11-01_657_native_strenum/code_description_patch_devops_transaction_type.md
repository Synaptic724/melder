# DevOps transaction-type projection

<!-- BEGIN ENTRY: "Preserve routing, reports and structural validation" -->
## Flow
Enum construction accepts exact names and maps only exact old lowercase values.
Existing name normalizers still strip and lowercase inputs for strategy dispatch.
Fact and embargo paths project only this enum to its historical token, retaining
other accepted string-like and value-bearing behavior. Activity views similarly
project enum members while preserving ordinary string formatting.

## Validation gate
Bind/notch enum members and the two old lowercase strings reach the structural
validator as before. The extra compiled-member notch check remains identity-based.
Unknown or differently cased raw strings retain their prior admission behavior.
Tests cover old and new forms, historical pickles, routing, reports and ownership.
<!-- END ENTRY: "Preserve routing, reports and structural validation" -->

<!-- BEGIN ENTRY: "Compare transaction forms without changing enum equality" -->
## Trigger and flow
The exact-name migration broke consumers that compared the previous lowercase values directly.
For an actual ChangeTransactionType or an exact canonical plain string, return its historical
lowercase token for local comparison. Return all other inputs unchanged. The caller preserves
the original request object; no generic case folding or enum equality/hash override is added.

## Validation and non-goals
Verify all members and old/canonical strings, unknown spellings and foreign values. This helper
does not change the structural validator's existing identity-specific NOTCH behavior, admission,
claiming, record output or lifecycle.
<!-- END ENTRY: "Compare transaction forms without changing enum equality" -->

<!-- BEGIN ENTRY: "Preserve the structural gate for exact string values" -->
## Trigger and flow
The mediator admits a canonical plain name and retains it in the staged request. The
validator MUST compare a local historical-token projection to bind/notch before its
existing binding-key, Book, and pending-spell checks; it MUST NOT rewrite the request.

## Edge cases and verification
The extra compiled-member check remains `is ChangeTransactionType.NOTCH`, so both raw
spellings retain the old raw-notch path. Unknown or mixed-case raw strings and foreign
objects keep their prior comparison behavior. Verify real commit, validation failure
propagation, old and exact strings, member identity and an unrelated-kind control.
<!-- END ENTRY: "Preserve the structural gate for exact string values" -->
