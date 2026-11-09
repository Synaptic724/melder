# System diagnostic severity compatibility

<!-- BEGIN ENTRY: "System validation diagnostic severity" -->
## Component and before/after
SystemDiagnostic carries a severity member. The system validation pipeline uses member
identity to separate errors and warnings and gates resolution only on errors. Its current
auto-valued Enum has ERROR=1 and WARNING=2; it becomes StrEnum with values ERROR and
WARNING. No validator, state, ownership, cleanup or locking behavior changes.

## Interface and failures
Old numeric by-value inputs and captured numeric pickle payloads remain readable.
Unknown values raise ValueError. Direct .value becomes a string and must be disclosed.
The existing error and warning member identity checks remain unchanged, including when
plain strings share the new values. Unknown external numeric consumers are not covered.

## Order, validation and rollback
Read the enum, validation system and relevant tests. Run causal tests on old source,
then apply the enum-only change. Test both old pickle payloads, numeric and canonical
values, and existing real diagnostic/validation branches. Roll back the base, explicit
values and legacy reader together. Refresh docs and graph before final asset checks.
<!-- END ENTRY: "System validation diagnostic severity" -->