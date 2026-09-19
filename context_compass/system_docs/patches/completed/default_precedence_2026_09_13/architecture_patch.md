# Patch: Honor ordinary constructor defaults

- Patch ID: default_precedence_2026_09_13
- Owner: updater_0
- Task: TASK-2026-09-13-optional-dependency-default-resolution-test
- Status: implemented and verified; owner review pending

<!-- BEGIN ENTRY: "Constructor default precedence" -->
## Objective and boundary
An ordinary explicit Python default supplies the argument. It must not create an inferred DI edge,
be replaced by a registered provider, or fail because such a provider is absent.
Apply this at Phase 1 rather than substituting constructor arguments after graph construction.

## Invariants
- SpellContract and SpellMap descriptors retain their existing explicit DI classification and behavior.
- Any other has_default=True parameter is PLAIN; falsey defaults are included.
- Annotation/default metadata and exact default object identity remain preserved.
- Parameters without defaults retain existing inference, validation and ambiguity rules.
- No added work or branches on the warm Meld execution path.
- Old cached execution plans must not retain the previous inferred edge.

## Changes
Parameter classification adds the ordinary-default branch; caching advances its semantic version.
No public signature, descriptor optionality policy, ownership contract or persistence format changes.
The descriptor-ban proposals and separate late-bound provider-root issue are outside this patch.

## Sequence and validation
Implement classification and cache invalidation together. Turn the existing 20 red cases green,
keep their 20 controls green, and update the existing version-history contract. Use the existing
automatic invalidation mechanism; no new cache replay tests or cache implementation work.
Run relevant requirements/DI suites, update authored context and regenerate affected indexes/graph/assets.

## Rollback
Revert the classifier and cache-version change together. Generated caches are disposable accelerators;
neither direction may treat plans from the other semantic version as compatible.
<!-- END ENTRY: "Constructor default precedence" -->
