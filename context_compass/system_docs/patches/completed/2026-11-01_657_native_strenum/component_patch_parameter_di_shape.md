# Parameter DI shape compatibility

<!-- BEGIN ENTRY: "Names, legacy inputs and typed dispatch" -->
## Before and after
The six Phase 1 ParameterDIShape values become exact-name strings with StrEnum.
Their historical numeric 1-6 inputs and captured pickles continue resolving to the
same members; names, order and Phase 1 classifications stay.

## Consumer boundaries
Requirements iteration, Phase 3 dependency keys and Phase 4 parameter/annotation
strategies keep the family-sensitive member dispatch that ordinary Enum supplied.
Raw strings and foreign same-valued members do not trigger those internal branches.
Phase 2's unmatched identity branch already skips them. SocketKind and its integer
record rows are not modified in this slice.

## Validation
Run focused legacy/name and actual consumer boundary tests, then existing compiler,
validation and component behavior tests. Disclose direct numeric/string differences.
<!-- END ENTRY: "Names, legacy inputs and typed dispatch" -->
