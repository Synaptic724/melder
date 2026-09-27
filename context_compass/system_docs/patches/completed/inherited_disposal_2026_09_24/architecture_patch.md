# Inherited disposal matching

<!-- BEGIN ENTRY: Binding disposal admission -->
## Scope and non-goals
Patch ID: inherited_disposal_2026_09_24.
Admit requested inherited cleanup methods at class bind time. Keep shallow class profiles,
unrelated spell IDs, non-class disposal policy, compiler/runtime paths and public signatures intact.
No subclass wrappers, package release, dependencies or packaged-asset rebuild.

## Changed components
| Component | Delta | Owner |
| --- | --- | --- |
| Binding Pipeline | Candidate-only inherited callable lookup | workflows_0 |

## Interface and boundary deltas
Bind retains inherited callable disposal names that were previously omitted. The established
ordered list still flows into Spell, fingerprinting, compiler records and Creations unchanged.
No public parameter, return type or ownership boundary changes.

## Cross-component invariants
- Bind MUST resolve names before fingerprinting and Spell construction.
- Existing direct-profile matches MUST retain their current eligibility.
- Fallback MUST respect first-definition MRO shadowing and avoid executing descriptors.
- The shallow profile method_names MUST NOT grow; bindings whose effective disposal list is
  unchanged retain their existing identity. Corrected disposal metadata deliberately changes IDs.
- Book priority, overlap ownership, deduplication and runtime cleanup ordering MUST remain intact.

```text
requested names -> direct profile / inherited static MRO match -> existing ordered list -> Spell
```

## Migration and rollout
1. Add regression guards, then correct Bind matching.
2. Verify native tests and both CommandOps registration cases against local source.
3. Promote the binding contract, refresh affected source maps and hand results to command_0.
Consumers obtain corrected metadata on rebinding; already-created Spell objects are not mutated.

## Rollback
Revert only this scoped helper/matching delta and its contract changes. This restores the omission;
the previous red evidence remains available. No persisted schema migration is introduced.

## Validation and ticket coverage
TASK-2026-09-24-investigate-inherited-cleanup-profiling owns all changes and evidence.
Require single/multiple inheritance, shadows, overrides, configured/explicit groups, order/dedup,
actual many/unique teardown, unchanged unrequested base-method identity, and the two original tests.

## Unknowns and decisions
No blocking unknown remains. This is a small predicate correction without changed synchronization,
rollback or orchestration; a separate code-description patch is not required.
<!-- END ENTRY: Binding disposal admission -->
