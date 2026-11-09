# State change reason compatibility

<!-- BEGIN ENTRY: "Transition reason name and legacy reads" -->
## Before and after
SpellStateChangeReason is a 27-member Enum with numeric auto values and acts as the
latest transition reason. Convert it to StrEnum values matching each member's name.
Member names, ordering, identity through state transitions and module path stay.

## Boundary and validation
Original numeric by-value construction and captured protocol-4 pickle payloads remain
readable. Direct .value changes from integer to the name string and default str output
changes; document both. State and transfer behavior must pass existing real tests.
SpellState is not changed here: its separate flag-set equality risk stays open.

## Rollback
Revert the base, values, numeric reader and focused tests together.
<!-- END ENTRY: "Transition reason name and legacy reads" -->
