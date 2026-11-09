# Permission and policy enum compatibility

<!-- BEGIN ENTRY: "Ward permission and policy exact strings" -->
## Component and before/after
Permissions bounds per-spell capability; Policies gates ward contracting directions.
Both currently use integer Enum values. Their values become their exact lowercase
member names under StrEnum; member identities, ordering and imports remain stable.

## Interfaces and invariants
Historical numeric by-value inputs and captured numeric pickles remain readable;
unknown values raise ValueError. Direct .value changes to string and is release-noted.
The type-sensitive enum helper and strict initial policy check MUST continue rejecting
foreign enum families. Permission ceilings, blocked/whitelist behavior, link direction,
contract ownership, transfer rollback and the recorded plain name strings stay unchanged.

## Order, validation and rollback
Read the declarations and actual bind/ward conversion and capability paths. Run causal
checks before edits. Validate old pickles/numeric inputs, canonical string/JSON values,
foreign-family and plain-string helper calls in both cache orders, real policy/permission
behavior and checkpoint restore. Roll back both enum bases, strings and legacy readers
together. External numeric-output consumers remain UNKNOWN.
<!-- END ENTRY: "Ward permission and policy exact strings" -->