# Session status and outcome enum contract

<!-- BEGIN ENTRY: "SessionStatus and OutcomePolicy" -->
## Representation and compatibility
Both enums use lowercase strings for uppercase names. New values equal names exactly;
the eight old lowercase values and old pickle payloads remain readable. Unknown, mixed-case
and whitespace values retain ValueError. Member identity and the BROKEN/ABORTED distinction
remain unchanged.

## Snapshot and failure behavior
TransactionSession.describe and status-bearing errors preserve their old lowercase tokens
separately from enum .value. UNWIND still runs inverses in reverse order; LEAVE_BROKEN still
runs none and records residue. No change to claims, locks, cleanup ownership or transition
ordering is selected.

## Validation
Capture real pre-change session outputs and old protocol-4 payloads; test both policies,
terminal states, stable snapshots/errors, exact old/new inputs and invalid strings. Update
only the existing direct BROKEN.value expectation and add its legacy input assertion.
Run the entire native mediator unit directory.
<!-- END ENTRY: "SessionStatus and OutcomePolicy" -->