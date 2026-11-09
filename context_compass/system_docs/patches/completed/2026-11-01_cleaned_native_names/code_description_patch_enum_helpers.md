# EnumHelpers execution contract
<!-- BEGIN ENTRY: "Type-sensitive cached name resolution" -->
## Trigger
Family errors and a memoized multi-argument boundary are input-type sensitive.
## Control flow
None refuses. A requested-family member returns unchanged. Any other Enum refuses before the
string branch. A string tries the existing lowercased key first; only a missing key searches actual
declared names by their lowercase spelling, including aliases. Unknown names retain ValueError.
Use type-sensitive keys in the existing bounded cache so cached strings cannot skip family checks.
## Errors and rollback
Keep ValueError for unsupported values. No value conversion, implicit stringify, whitespace trim
or alternate lifecycle behavior. Restore the whole helper edit together if its contracts fail.
## Invariants and idempotency
Same accepted input returns the same actual member; repeated calls change no runtime state.
Retain lowercase-key precedence for any existing enum with case-colliding names.
## Non-goals
No SpellInputUtils changes, global lookup tables, enum base migration or broad normalization.
## Validation focus
Causal uppercase/mixed-name failures; foreign Enum/StrEnum cold and warmed orders; unchanged
lowercase/member/error contracts through the complete existing helper module.
<!-- END ENTRY: "Type-sensitive cached name resolution" -->
