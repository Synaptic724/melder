# Phase 5 artifact publication flow

Patch ID: provider_artifact_ownership_2026_09_19

<!-- BEGIN ENTRY: "Phase 5: preserve dependency artifacts" -->
## Trigger
Shared-state invalidation and owner-versus-borrower publication change at a compiler phase boundary.

## Control flow
Build the full visible/scoped snapshot, system index and root blueprint map using current rules.
For each snapshot ID, skip attachment when the ID is outside publication_spell_ids. For selected IDs,
attach the index; attach/build the blueprint for constructed spells, retaining existing invalidation.
The invoking artifact retains its full root map/index for validation and subsequent target compilation.

Frame-wide entry uses the owning book's active _spells_by_id keys. Local entry uses its target ID only,
because its subsequent plan pipeline builds only that target. Dependencies remain readable graph inputs.

## Errors and rollback
Do not catch missing-artifact failures or alter validation state to force progress. Existing transactional
and phase-failure handling remains. Excluded providers are untouched even if consumer compilation fails.

## Invariants and repeatability
Repeated borrower passes preserve provider artifacts and references. Selected-target recompilation still
clears and replaces its own outputs. Publication selection is per pass, with no additional persistent state.

## Non-goals
Do not reconstruct supplied objects, broaden existence modes, change cache versions, recompile provider
canonical state under borrower visibility, or change the original tests to expect an exception.

## Verification
Exercise full and local entrypoints; preserve graph nodes/edges for excluded providers, maintain active
target invalidation and verify final owner meld returns the original stateful unique object.
<!-- END ENTRY: "Phase 5: preserve dependency artifacts" -->
