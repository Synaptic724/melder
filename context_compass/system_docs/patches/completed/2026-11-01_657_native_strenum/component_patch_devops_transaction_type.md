# DevOps transaction-type compatibility

<!-- BEGIN ENTRY: "Exact transaction names with stable control-plane reports" -->
## Representation
ChangeTransactionType remains StrEnum with exact member-name values. Original
lowercase inputs and pickles continue to resolve. A projection returns original
lowercase tokens for reporting; direct enum value/string output changes.

## Consumers and behavior
The builder and mediator continue normalizing enum and string transaction names.
Fact-family reports, admitted/extended claim reasons, start-failure reasons and
activity-view enum inputs retain historical lowercase tokens. The structural
validator preserves its prior handling of enum members and legacy raw bind/notch
values, including its identity-specific notch branch. No lock or claim changes.

## Validation
Exercise every value and old reader, dispatch, actual admission reason, fact
reporting, activity query and structural validation; run the change-control and
ownership-transfer tests and the final combined selection.
<!-- END ENTRY: "Exact transaction names with stable control-plane reports" -->

<!-- BEGIN ENTRY: "Transaction comparison projection" -->
## Boundary and validation
The DevOps vocabulary provides a private stateless comparison projection for its own members
and exact canonical plain strings, yielding historical lowercase tokens. Other inputs are
returned unchanged. This preserves legacy comparison behavior without altering StrEnum
value, hashing or equality; unrecognized raw spellings are not broadly case-folded.
Spellbook and Conduit apply it only at their pre-existing comparison boundaries. Verify old,
canonical, invalid and foreign-family inputs together with real transactions and posture gates.
<!-- END ENTRY: "Transaction comparison projection" -->

<!-- BEGIN ENTRY: "Canonical raw values reach structural commit validation" -->
## Before and after
The mediator accepts and stores a raw exact BIND string, but the structural validator
currently skips it; old bind and the BIND member run the gate. Project recognized
canonical strings through the existing comparison token before the bind/notch gate.

## Invariants and validation
Keep the original staged request, old lowercase behavior and unknown spelling treatment.
Keep the compiled-member shortcut exclusive to the actual NOTCH enum member; raw notch
and raw NOTCH both take the historical raw-string path. Test real mediator-to-commit
validation and controls before and after the change.
<!-- END ENTRY: "Canonical raw values reach structural commit validation" -->
