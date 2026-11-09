# Aetheric mediator claim-mode compatibility

<!-- BEGIN ENTRY: "Exact enum values with stable claim tokens" -->
## Representation
Mediator ClaimMode remains a StrEnum but its values exactly match member names.
Old x, s and ix inputs and old pickles still resolve; unknown values remain errors.
Its internal wire projection yields the original short codes for the real output
boundaries; direct value/string conversion changes and must be release-noted.

## Consumers and behavior
TransactionRequest stores sorted short-code claim tuples and rehydrates them to
members. ClaimTable snapshots and ClaimBlock evidence continue emitting short codes.
Compatibility checks keep strict family validation and the existing x/s/ix matrix.
No locks, cleanup, admission ordering, scope semantics or DevOps enum changes.

## Validation
Test all three names, old tokens/pickles, real request round-trip, snapshots,
block evidence and invalid/foreign inputs, then the complete native mediator suite.
<!-- END ENTRY: "Exact enum values with stable claim tokens" -->
