# Private Spellbook conjure for a supplied normal conduit

## Current slice
Owner explicitly requests this one method first, with direct tests. Add
Spellbook._conjure_existing_conduit(conduit, *, policy="default", dynamic=False, name=None).
The receiving Book already exists; ordinary construction selected its configuration. The caller
prepares a live normal, detached, unregistered target and its root-owned runtime resources first.
This method does not change Conduit status, create another Conduit, or wire the public upgrade yet.

## Control flow
1. Validate Book/target liveness, target normal state and same-frame identity.
2. Admit the Book's CONJURE transaction before its lock, mirroring ordinary conjure.
3. Enforce single-conjure, recorded configuration discipline and native spell-ID integrity.
4. Prepare/freeze configuration, structural phases and cache classification with existing helpers.
   Emit the receiving Book twin even when shared configuration was already locked.
5. Run normal resolution phases under the supplied Conduit's existing ID. Enforce verdict/policy.
6. Fire the normal pre hook. Temporarily drain the existing gate for attachment, preserving its
   prior admission state. Recheck root name/id before changing runtime ownership.
7. Attach this Book/configuration and selected hooks to the supplied runtime; rebind its Meld and
   retained Space Meld lookup aliases and invalidate their Book-dependent caches. Preserve stores.
8. Perform normal root/index registration and Conduit record emission, then restore admission.
9. Use the normal activation tail for Book attachment, identity, ownership stamping, cache/Nexus/risk
   work and activation/post hooks. Return the exact supplied object; end admission in finally.

## Lifecycle and failure
The caller owns structural promotion/detachment and quiescence of foreign-thread managed Spaces;
their thread-local stacks cannot be enumerated from this method. Managed scopes on the calling
thread, registered manual Spaces and idle pooled Spaces can be rebound explicitly.
Configuration/validation/policy/name failures precede ownership replacement. Later publication
failures retain normal conjure's explicit cleanup responsibility; do not claim application callback
effects roll back. Callback exceptions retain the existing logged/suppressed lifecycle behavior.
No inherited definitions, copied root verdicts or per-meld configuration checks.

## Validation
Direct real-component tests exercise exact object/id retention, new/empty and explicitly bound Books,
normal status/frame/one-shot refusal, selected hooks and their order, cached old-ID refusal, fresh and
retained Space resolution, configuration failure, root-name collision and cleanup isolation.
Run ordinary conjure/configuration/Bind compatibility cases. The old upgrade regressions remain red
until the later caller integration; do not wire or change them in this single-method slice.
