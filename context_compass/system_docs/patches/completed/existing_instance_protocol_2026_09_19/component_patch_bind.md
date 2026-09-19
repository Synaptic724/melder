# Binding Pipeline admission delta

Patch ID: existing_instance_protocol_2026_09_19

<!-- BEGIN ENTRY: "Binding Pipeline: actual-instance validation" -->
## Component purpose and boundary
Bind examines targets, validates binding policy and constructs the Spell handed to Spellbook.
Its Protocol helper already checks public members declared directly on a Protocol.

## Before/after behavior
Before: ClassBindingProfile invokes the helper; InstanceBindingProfile and OtherBindingProfile skip it.
After: all three invoke that same helper on the actual binding target. Instance-added callable members
are accepted, and instance shadowing with a non-callable value is rejected.

## Interface deltas
The private helper accepts an object candidate (class or supplied value). The public binding shape
does not change. Failed supplied admission uses an Existing object prefix, Protocol name and member list.

## State and lifecycle deltas
No new fields/stores or cleanup custody. Failure occurs before Spell construction/publication. Existing
profile/fingerprint work and existing lock ownership retain their established ordering.

## Failure mode deltas
Missing/non-callable required members raise TypeError at bind instead of becoming false provider
candidates. The checker's normal attribute access can propagate user descriptor errors; do not suppress them.

## Dependency and ordering constraints
Internal-registration, concrete-target, profile and existence validation precede Protocol admission.
Generalize the helper's wording without broadening which Protocol members are inspected.

## Validation expectations
Native active/staged rejection before/after conjure; exact-reference injection through four routes;
instance-only and shadowed members; both existing profile families; compatible class and callable controls.

## Unknowns and open decisions
No new ownership or Protocol feature decision is selected. Existing shared checker limits are documented.
<!-- END ENTRY: "Binding Pipeline: actual-instance validation" -->
