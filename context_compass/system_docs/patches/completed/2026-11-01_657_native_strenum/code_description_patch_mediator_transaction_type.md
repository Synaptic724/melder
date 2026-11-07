# Aetheric mediator transaction-type projection

<!-- BEGIN ENTRY: "Keep transaction reporting tokens and filters" -->
## Flow
The enum constructor resolves exact names and maps only exact old lowercase
strings through its missing-value hook. A member projects its old lowercase
reporting token. Request and staged descriptions, session snapshots, strategy
fact reports and builder descriptions/errors use that projection.

## Filter contract
Activity filtering retains old lowercase strings and enum members, recognizes
canonical exact strings, and leaves unknown strings with no matches. No lock,
claim ownership or cleanup changes are introduced. Test real records, queries,
legacy pickles and the full affected mediator suite.
<!-- END ENTRY: "Keep transaction reporting tokens and filters" -->
