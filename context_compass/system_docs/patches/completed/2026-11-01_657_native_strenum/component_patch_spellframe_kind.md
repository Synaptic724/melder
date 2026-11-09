# SpellframeKind string contract

<!-- BEGIN ENTRY: "SpellframeKind binding and record values" -->
## Before and after
The three values are already identical to their names. The selected change makes the
enum string-backed while preserving names, explicit values, member order and module.
String equality and rendering change as requested; family identity remains available
through the actual enum type and must not be inferred from equal strings.

## Binding and persistence
The real binding signature returns kind.value, a plain string; the binding manifest hashes
kind.name; SpellCrystal captures kind.name. These values remain byte-for-byte identical
for the same input. Protocol restore/graft retains its existing hydration and shortfall
contracts. Unknown direct values continue to raise ValueError.

## Tests and rollback
Embed the captured old protocol-4 bytes for all three members and verify readback, new
round trips and JSON. Pin the real fixed bare/category signature and manifest examples,
then run existing complete consumers including the real cached protocol restore and
index graft. Roll back the one enum base and docstring together if necessary; no record
format or numeric version change is selected. External persistence beyond exercised
formats remains UNKNOWN.
<!-- END ENTRY: "SpellframeKind binding and record values" -->