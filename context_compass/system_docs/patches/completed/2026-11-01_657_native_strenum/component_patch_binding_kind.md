# Spell Examination Profiles: binding kind compatibility

<!-- BEGIN ENTRY: "SpellBindingKind canonical strings and legacy integers" -->
## Boundary and before/after
The binding strategy assigns SpellBindingKind members to binding profiles. Before this
change their values are 1-4; Nexus serializes the member name into its descriptor.
Afterward the four members are StrEnum with exact member-name values, while profile
identity and descriptor name publication remain unchanged.

## Interfaces and failure behavior
CLASS, CALLABLE, INSTANCE and OTHER retain their paths, names, order and identities.
Their .value and str become canonical strings, an intentional documented change from
numeric .value and the old Enum rendering. A by-value lookup using the historical
integers must return the same member; pickle payloads that reconstruct those numbers
must still load. Unknown strings and numbers must raise ValueError. No claim is made
for unobserved external consumers or all possible serialization formats.

## State, ownership and ordering
No profile state, lifecycle, ownership, locking or cleanup change. Change only the enum
and its narrow legacy lookup. Preserve the producer's member assignments and the
Nexus descriptor's name projection. Read both source paths before modifying the enum.

## Validation and rollback
Add a causal test with actual protocol-4 pre-change pickle bytes for all four members,
canonical string values and JSON, numeric construction, invalid values and a real
strategy-to-descriptor projection. Run it red on the old source, then green with the
existing profile/strategy/descriptor tests. Roll back the base, explicit values and
legacy reader together. Record exact source and test hashes and release consequences.
<!-- END ENTRY: "SpellBindingKind canonical strings and legacy integers" -->