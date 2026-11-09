# Binding lifetime and managed-mode compatibility

<!-- BEGIN ENTRY: "Existence and managed pool mode strings" -->
## Before and after
Existence chooses instance lifetime and ManagedSpellMode chooses pooled lease policy.
Both currently have numeric auto values and render their names as strings. They become
StrEnum with exact member-name values, preserving the current str output and members.

## Interface, state and failure invariants
Historical numeric by-value inputs and captured numeric pickles remain readable.
Direct .value changes to string and must be disclosed. Binding-manifest and spell-crystal
name projections and hashes stay unchanged. Bind accepts same-family mode members and
plain names; foreign enum members, including Existence, remain TypeError even after
becoming strings. Existence lifetimes, pool behavior, ownership, cleanup and transfer
semantics are unchanged. Unknown external numeric-output consumers remain UNKNOWN.

## Ordering, validation and rollback
Read both enum modules, Bind and relevant tests. Run causal tests on old sources, then
change both declarations and Bind's foreign-enum/string boundary together. Verify old
pickles, exact strings, helper family controls, binding hash, managed-pool and real
record/restore tests. Roll back both enum readers and the guard as a unit.
<!-- END ENTRY: "Existence and managed pool mode strings" -->