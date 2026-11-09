# Scope prefix enum contract

<!-- BEGIN ENTRY: "ScopePrefix and ScopeKey" -->
## Representation and compatibility
The three uppercase member names become their string values. The old lowercase values
remain readable by exact by-value construction and old pickles; unknown values fail.

## Isolation boundary
ScopeKey continues to emit world, frame:<name> and subsystem:<name> exactly, with the
same validation and is_world comparison. Transaction strategies must continue to claim
the same keys, so overlapping work cannot pass by using different case.

## Validation
Compare three actual pre-change pickle payloads and exact key examples, exercise the
real frame-create strategy and claim table, and run all native mediator unit tests.
<!-- END ENTRY: "ScopePrefix and ScopeKey" -->