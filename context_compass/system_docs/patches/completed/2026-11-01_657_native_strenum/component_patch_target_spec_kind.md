# Override target-kind compatibility

<!-- BEGIN ENTRY: "Override target kind exact strings" -->
## Component and before/after
TargetSpec.parse classifies an override key as PATH, UNIQUE or BROADCAST. The resolver
uses member identity for its ranked path/wildcard dispatch. Numeric Enum values become
exact member-name strings under StrEnum; module, order and member identity remain.

## Interface and invariants
Old numeric inputs 1-3 and captured numeric pickles remain readable; unknown values
raise ValueError. Direct .value changes to string and is release-noted. Target grammar,
parse errors, resolver ranking, cuts, error text and construction plans remain intact.
Unknown external numeric-output consumers are not covered.

## Order and validation
Read enum, parser, resolver and relevant tests. Run causal tests before source edits.
Validate old numeric/pickle inputs, exact strings, all three parse kinds and existing
real resolver/override tests. Roll back base, values and reader together; reconcile
docs and graph before final generated assets.
<!-- END ENTRY: "Override target kind exact strings" -->