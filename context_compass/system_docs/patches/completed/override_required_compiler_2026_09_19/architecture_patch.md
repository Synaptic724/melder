# Architecture Patch: Non-resolvable compiler policy

- Patch ID: override_required_compiler_2026_09_19
- Status: active
- Owner: updater_0

<!-- BEGIN ENTRY: Descriptive registrations and executable compilation -->
## Objective and Boundary
Consume native Spell.resolvable without conflating a visible definition with a construction provider.
Preserve Phase-1/2 declarations, classify required selected False inputs as OVERRIDE_REQUIRED, and
carry their registered references and required-input data through Phase 10.

## Changed Components and Interfaces
- Compiler records: append SocketKind.OVERRIDE_REQUIRED; add descriptive referenced_spell_ids and
  parameter_kind to local socket descriptors without changing ParameterDIShape.
- Phase 3: apply capability after existing matching; keep executable and descriptive targets separate.
- Phase 4: report required overrides and use resolved policy for binding cycles; apply constructor-DI
  policies only to resolvable roots, retaining profile/registration/descriptor validity checks.
- Phase 5: build the executable snapshot/index/blueprints from resolvable visible entries only.
  All bound definitions and their local topology remain in their owning registration/state stores.
- Phase 8: retain the no-edge socket; never enqueue reference IDs, and include resolved policy in signatures.
- Phase 9/10: retain required_override_params as plain value tuples in every plan variant/family.
- Spellbook creation: skip False roots for executable payload/cache and plan eligibility.
- SpellSystemStates: include OVERRIDE_REQUIRED in the existing frame-key selector watcher so
  bind/notch/removal invalidates reference-only consumers without constructing a dependency edge.
- Meld's existing structural-to-resolution handoff invalidates the conduit-local verdict after a
  structural rerun, preventing a stale executable plan from surviving new provider selection.

## Invariants
- Ordinary defaults stay PLAIN and retain their values; no synthetic None or declaration mutation.
- Implicit annotation matching prefers True providers, then one False definition, retaining cardinality errors.
- Explicit SpellMap selectors never redirect to another provider. False plus spell_override payload refuses.
- SpellContract remains linked-provider DI; a selected False provider is an incompatible-provider error.
- Collections include True providers in their existing order, including the existing empty-list behavior.
- No new ownership/lifetime/version model and no key uniqueness bypass.
- Artifact visibility does not expand publication authority; retain the provider-artifact ownership repair.
- Use existing input-signature/cache-version machinery. S4/S6 own executable/wire compatibility enforcement.

## Migration Order
1. Add compiler regression baseline and resolved records/Phase-3 policy.
2. Align Phase-4 construction diagnostics and Phase-5 executable root admission.
3. Carry required-input tuples through occurrence signatures, injection and both planner variants.
4. Verify focused compiler/default/provider compatibility and hand the contract to S4/S5/S6.

## Validation and Completion Limit
Tests cover scan/pass-cache parity, explicit selectors, optional/default and collection distinctions,
descriptive cycles, False-only/mixed roots, model/plan propagation and unchanged ordinary compilation.
This is not runtime enforcement: S4 must check actual supplied values before constructor side effects
and guard direct/fast/cached resolution; S5/S6 still provide graph projection and durable replay.

## Rollback
Revert this compiler patch's changes and regenerate affected docs/assets without undoing S2 registration.
No release, public deployment, external state mutation or source-body identity change occurs here.

## Ticket Coverage
TASK-2026-09-19-implement-override-required-compiler implements S3 under
EPIC-2026-09-19-discoverable-non-resolvable-registrations. S4/S5/S6 consume its outputs.
<!-- END ENTRY: Descriptive registrations and executable compilation -->
