# Aetheric mediator transaction-type compatibility

<!-- BEGIN ENTRY: "Exact transaction names and historical reporting tokens" -->
## Representation
All eight TransactionType values match their names exactly. Exact lowercase
historical inputs and pickles resolve to the same members; unknown spellings fail.
A member projection produces its historical lowercase token. Direct enum value
and string output change and must be release-noted.

## Consumers and behavior
Request and staged descriptions, session snapshots, fact family reports and
strategy descriptions/errors retain historical lowercase tokens. Activity filters
accept historical lowercase, canonical values and members; unknown strings match
nothing. No claim, lifecycle, lock order or strategy-dispatch change is intended.

## Validation
Test every name, old inputs and pickles, reporting and actual activity filtering;
then run the native mediator suite under the GIL off and on.
<!-- END ENTRY: "Exact transaction names and historical reporting tokens" -->
