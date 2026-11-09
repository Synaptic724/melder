# Managed-mode typed input boundary

<!-- BEGIN ENTRY: "Managed mode normalization across string enums" -->
## Inputs and decision order
None still selects elastic. A ManagedSpellMode member returns itself. A plain string
or non-enum string subclass resolves case-insensitively by name, with the existing
unknown-name ValueError. A member of another Enum family, including a string-backed
one, MUST reach the wrong-type TypeError rather than the string branch. A non-string
Existence member was already rejected; an unrelated pre-existing StrEnum with a mode
spelling was previously accepted as a string and is now explicitly rejected.

## State and failures
This check runs before pool activity and changes no state, locks or cleanup. No
unknown value is silently defaulted. Historical numeric enum construction is a
separate, explicit reader on the two enum classes; the Bind mode parameter does not
accept a raw integer merely because the enum does.

## Validation
Exercise same-family members, plain strings in both cases, old numeric/pickle reads,
Existence and a foreign StrEnum sharing a mode string, invalid inputs, real managed
binding, binding-manifest hash, pool lifecycle and record/restore paths.
<!-- END ENTRY: "Managed mode normalization across string enums" -->