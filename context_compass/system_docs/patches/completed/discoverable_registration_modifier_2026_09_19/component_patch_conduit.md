# Component Patch: Conduit Runtime Binding Facades

<!-- BEGIN ENTRY: Conduit binding capability forwarding -->
## Purpose and Boundary
Conduit exposes bind and bind_inactive over its owning Spellbook and enforces existing facade gates.

## Before and After
Add the explicit default-True resolvable parameter to both facades and forward it unchanged.
Neither facade stores another copy of the flag or interprets it as conduit posture.

## Interface Deltas
An additive keyword matching Spellbook; existing arguments and return identities are unchanged.

## State and Lifecycle
No new Conduit state or cleanup. Preserve existing transaction/posture/cleaned-object checks.

## Failure Deltas
Do not coerce the bool or catch new Bind refusal errors; let the existing call chain report them.

## Dependencies and Order
Requires Spellbook and Bind native transport. Conduit-created registrations must agree with direct ones.

## Validation
Exercise active and inactive forwarding with real public facade calls where possible, and verify
the corresponding registered Spell's value instead of asserting only a mock call signature.

## Unknowns
Meld and fast-return refusal is S4 work; binding forwarding does not establish execution safety.
<!-- END ENTRY: Conduit binding capability forwarding -->
