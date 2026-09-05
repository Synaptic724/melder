# Component patch: Creations disposal-list ownership

## Purpose and boundary
Creations owns live objects and cleanup entries for one scope. The established method policy
comes from each Spell; this task changes storage references, not invocation behavior.

## Before / after
- Before: singleton/many registration, extraction, and restoration copy each method list.
- After: all six contacts retain the same established inner list.
- The two registries, their detach-before-dispose flow, and scope routing remain unchanged.

## Interface deltas
Existing optional list parameters and in-memory transfer dictionaries are unchanged.
When disposal is enabled, a supplied list is retained even when empty. Omitted metadata
continues producing an empty list. When disabled, no disposal entry is added.

## State and lifecycle
Creations owns registry entries and raw instances; it borrows the established method list.
Extraction/removal carries both object and method-list identity. Restoration does not clone
either. Cleanup MUST NOT clear the borrowed list; another scope may still retain it.

## Failure modes
Keep collision and malformed-restore errors unchanged. One failing method stops that object's
chain, other entries continue, and errors aggregate through the existing ExceptionGroup path.

## Dependency and ordering
Verified producers and compiler propagation precede this task. Creations has six substitutions.
Real runtime verification also exposed two inline copies in generalized manifest no-overrides
registration; that caller must retain names too. ConduitCreations and the existing-object
Conduit caller already forward metadata directly.
Keep reverse key/bucket traversal and inter-scope cleanup ownership unchanged.

## Validation expectations
Test singleton/many registration and transfer identity, empty/omitted metadata, disabled
disposal, reusable clear/pool paths, and actual method order after transfer. Real runtime tests
cover solo, generalized, and many-only graphs, both priorities, and override variants.
Keep existing reverse-order and method-failure regressions passing.

## Unknowns and open decisions
None in this six-contact change. No private-policy mutation or persistent replay is introduced.
