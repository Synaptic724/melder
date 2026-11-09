# DevOps claim-mode compatibility

<!-- BEGIN ENTRY: "Exact names with stable acquisition tokens" -->
## Representation
DevOps ClaimMode remains StrEnum with exact member-name values; original x/s/ix
inputs and old pickles remain readable. A wire projection gives the historical
short code; direct enum value/string conversion changes and is release-noted.

## Consumers and behavior
Each affected strategy continues emitting x/ix in scope-claim tuples. The
transaction manager stores x/s/ix and the embargo manager renders blocking
modes using the same original tokens. The mode matrix and claim ownership use
actual enum members and are unchanged; no locks or lifecycle ordering change.

## Validation
Test every member, old values/pickles, actual plan, request and conflicting
acquisitions. Run the affected strategy and ownership-transfer regressions.
<!-- END ENTRY: "Exact names with stable acquisition tokens" -->
