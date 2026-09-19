# Bind Protocol gate control flow

Patch ID: existing_instance_protocol_2026_09_19

<!-- BEGIN ENTRY: "Bind: Protocol gate ordering" -->
## Trigger justification
The change extends an admission policy gate and must preserve preceding error precedence.

## Control-flow description
Inside Bind's existing lock: refuse internals and invalid concrete targets, obtain the normal profile,
resolve metadata/fingerprint, classify existing values and validate lifecycle/callable rules. If the
frame is a Protocol and the profile is class or existing-value, run the current helper on the target.
On success continue classification/Spell creation. On failure raise before returning a publishable Spell.

## Edge/error behavior and rollback
Sort failing member names as before; preserve the Class prefix and use Existing object for supplied
values. No partial Spell is published. Keep the existing lock context and exception propagation.
Do not insert new rollback state or call methods on the supplied object.

## Invariants and idempotency
The helper inspects the actual candidate with the current member-access rules, without constructing it.
Bind remains the only new validation point; no repeated reflection in meld or compiler phases.
The patch introduces no mutable state and changes no registration-uniqueness decisions.

## Explicit non-goals
Do not widen the helper to inherited Protocol members, annotation-only fields, signature compatibility
or factory-return checking. Do not change instance storage, disposal, transfer, fingerprints or caches.

## Validation focus points
Error precedence, actual-instance surface, rejection before active/staged publication, compatible
compiler/injection paths and existing class/factory/grouping contracts.
<!-- END ENTRY: "Bind: Protocol gate ordering" -->
