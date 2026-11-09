# Participation state legacy token control flow

<!-- BEGIN ENTRY: "Exact legacy values and stable registry output" -->
## Enum by-value read
Use the enum missing-value hook only for the four explicitly listed old lowercase
strings. Accept ordinary string subclasses but do not coerce other enum families.
Return the corresponding member; return None for everything else so ordinary unknown,
mixed-case, whitespace and invalid values raise ValueError as before.

## Registry output
The shared participant renderer derives the old lowercase token from the member name,
rather than its newly canonical uppercase value. Keep the existing member-typed write
guard, ACTIVE-only emits check, lock scope and detached row shape.

## Tests
Verify both canonical and exact old tokens, old pickle loads, rejected unknowns, plain
lowercase row values for all four states and strict raw/foreign registry rejection.
<!-- END ENTRY: "Exact legacy values and stable registry output" -->