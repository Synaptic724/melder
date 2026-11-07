# Spell state flag compatibility

<!-- BEGIN ENTRY: "Flag ownership and name strings" -->
## Before and after
SpellState becomes StrEnum with values exactly equal to its existing names; all
historical numeric inputs and captured old pickles resolve to the same members.
Direct numeric .value and default str rendering change and must be release-noted.

## Family boundary
SpellSystemState.has_flag, set_validity and update_flags accept only actual
SpellState members for flag membership/add/remove, ignoring None and non-family
values. A reason or raw string of the same spelling cannot clear an owned flag.
Previously a non-family addition was retained; it is now ignored and disclosed.
Valid flag ordering, validity, risk publication and transfer semantics remain.

## Validation
Pin the collision against the current code, then run state/registry and transfer
suites after the paired enum and flag-boundary change.
<!-- END ENTRY: "Flag ownership and name strings" -->
