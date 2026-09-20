# Architecture Patch: Runtime admission for non-resolvable registrations

- Patch ID: non_resolvable_runtime_admission_2026_09_19
- Owner: updater_0
- Status: active

<!-- BEGIN ENTRY: Selected registration admission -->
## Objective and Boundary
Enforce the existing immutable Spell.resolvable capability at actual direct resolution and reuse-only
entry. Preserve observational lookup and the compiled runtime's existing ownership/cache machinery.
Required supplied-value execution and nested constructor preflight are a separate S4 task.

## Interface and Ownership Deltas
No public signature or stored state changes. Meld gains one shared cold error helper using the existing
MeldExecutionError. ConduitMeld and SpellSpaceMeld check the selected native capability before optional
validation, override normalization, hooks, context build or existing-object return.

## Invariants and Fast Path
- Explicit selection never substitutes another provider when the selected registration is False.
- False refusal names the selected version and gives caller-supply/resolvable-registration guidance.
- Lookup/probe helpers remain observational and may describe False registrations.
- Capability is immutable per version and the bool participates in False version identity.
- Fast-door entries are minted only after successful normal admission/execution. A False target cannot
  reach insertion. Existing epoch/context guards continue to handle version/cleanup transitions.
- Do not add another per-hit capability read to the warm door without evidence that the invariant fails.

## Migration and Validation
1. Add public normal/reuse/scoped/refusal regressions and establish red results.
2. Add the shared error and four post-selection checks; preserve matching and ownership.
3. Prove repeated refusal, False with overrides/hooks, True controls and mode/version transitions.
4. Run concrete Meld, fast-door and existing compiler compatibility; refresh docs/assets and hand off
   required-input execution with its original uncompleted proof obligations.

## Rollback and Ticket Coverage
Revert only this admission change and regenerate affected assets. Preserve S2/S3 and other agents' work.
TASK-2026-09-19-enforce-non-resolvable-runtime-admission owns this patch; S4 remains open afterward.
<!-- END ENTRY: Selected registration admission -->
