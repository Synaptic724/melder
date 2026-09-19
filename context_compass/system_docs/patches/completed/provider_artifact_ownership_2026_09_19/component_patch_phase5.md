# Phase 5 publication ownership

Patch ID: provider_artifact_ownership_2026_09_19

<!-- BEGIN ENTRY: "CompilerPhase5: bounded artifact attachment" -->
## Purpose and boundary
Phase 5 builds a visible system index and rooted dependency blueprints. Its attachment setters clear
later analysis/model/plan/codegen and creation contexts on the Spell receiving the new artifacts.

## Before and after
Before: every visible snapshot Spell receives those destructive setters, including borrowed providers
and same-book dependencies outside a local target's rebuild queue.
After: retain full graph construction; invoke setters only for IDs explicitly authorized by the pass.
Conduit-wide runs publish owned-local IDs, while local runs publish the single selected target.

## Interface deltas
Add a required private publication_spell_ids collection to the attachment helper. Both internal callers
must provide it. No fallback to all visible IDs; tests must state the intended publication set.

## State and lifecycle
Unselected Spells retain their existing canonical artifacts, contexts and spellspace flags. Selected
Spells keep the current invalidation/rebuild behavior. Full dependency information stays in the new index.

## Failure modes
Current phase failure propagation remains. This repair prevents missing-codegen errors caused by
invalidating providers outside the corresponding compilation queue; it does not hide absent payloads.

## Dependency and ordering
Read current phase-5 setters, artifact cleanup and frame/local planning entrypoints first. Publish before
the selected target's later phases, exactly as before. Do not add locks or change transaction ordering.

## Validation
Native borrower prefixes, repeated/two-borrower cycles, explicit/implicit validation and cleanup;
same-book late consumer plus provider remeld; helper selection and owner-target invalidation controls.

## Open decisions
None blocking the current-model repair. Broad existing-object proposals are retired by owner direction.
<!-- END ENTRY: "CompilerPhase5: bounded artifact attachment" -->
