# DevOps incident enum compatibility

<!-- BEGIN ENTRY: "Incident severity and status exact strings" -->
## Component and before/after
IncidentManager owns incident records and filters their status by identity. The two
vocabularies currently use integer auto values 1-4. They become StrEnum with each
existing lowercase name as its exact value; no incident ownership or transitions change.

## Interfaces, state and failures
Historical numeric by-value inputs and captured protocol-4 enum pickles MUST reconstruct
the same member. Unknown values raise ValueError. Direct .value becomes a string and
must be release-noted. Manager filtering MUST continue to require member identity: a
raw same-spelled string and another enum family do not match. Its status transitions,
record ownership, teardown, transfer incident emission and locking stay unchanged.

## Dependencies, order and validation
Read both enum sources, the actual Incident and manager paths and the transfer incident
emitter. Run causal tests before editing. Validate the eight old pickle payloads, numeric
constructors, exact string/JSON values, real manager filters and status transitions, and
the relevant existing incident and transfer tests. Roll back both enums and their legacy
readers together. External direct numeric-value consumers remain UNKNOWN.
<!-- END ENTRY: "Incident severity and status exact strings" -->