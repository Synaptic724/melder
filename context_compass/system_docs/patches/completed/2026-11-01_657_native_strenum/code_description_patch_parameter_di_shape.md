# Parameter DI shape dispatch

<!-- BEGIN ENTRY: "Preserve identity at shape classifiers" -->
## Control flow
For requirements iteration compare the one captured shape by identity against the
three DI members. For Phase 3 dependency keys compare the member by identity against
single/collection. For each Phase 4 strategy read the parameter shape once for its
existing membership condition and compare the two members by identity. Existing
subsequent per-member branches and their read ordering stay.

## Failure and compatibility
Unknown/foreign values keep their previous non-match behavior; no new validation,
normalization or exception is introduced. Legacy enum construction maps the exact
old numeric values, including numerically equal hashable values, to the old members.
Tests exercise raw strings and a same-valued foreign StrEnum, and real typed members.
<!-- END ENTRY: "Preserve identity at shape classifiers" -->
