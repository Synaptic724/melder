# SpellType binding-family compatibility

<!-- BEGIN ENTRY: "Spell type exact strings and resolution matrix" -->
## Component and interface
Bind derives one of fourteen SpellType members from the binding profile. The
resolution matrix uses member names to select class, callable or existing-object
policies. Integer Enum values become exact member-name strings under StrEnum; module,
member names, order and existing bare str output remain.

## Boundaries and failures
Numeric by-value inputs 1-14 and captured old numeric pickles remain readable. Direct
.value becomes string and is release-noted. Profile classification, matrix policy,
validation, ownership and lifecycle do not change. Unknown enum values raise
ValueError. External numeric-output consumers remain UNKNOWN.

## Order and validation
Read the enum, Bind classification and matrix. Add causal tests for all fourteen old
pickle payloads and new exact strings, then run real Bind and matrix tests. Restore
coverage remains part of the final combined native cut. Roll back the base, values and
legacy reader together; reconcile documentation and graph before final assets.
<!-- END ENTRY: "Spell type exact strings and resolution matrix" -->