# Component Patch: Selector-sensitive invalidation

<!-- BEGIN ENTRY: Required-input frame-key watchers -->
## Before and After
The existing spellbook-scoped collection-frame reverse index handles selector changes without direct
dependency IDs, but admits only NORMAL collection sockets. OVERRIDE_REQUIRED has the same need:
new providers, removals and notches must invalidate its consuming Spell even without a construction edge.

## State and Interfaces
Reuse existing SpellSystemStates maps, registration/cleanup paths and mark_collection_dependents_dirty
commit notifications. Keep the established method/field names; document the additional required-input
selector semantics. No new registry, ownership, locks or cache framework.

## Producer Contract
Phase 3 publishes dependency_key for executable selection only. Non-resolvable roots preserve
declarations without a watched constructor key. Normalize Optional/ForwardRef selection keys in the
same way as candidate matching. Actual referenced_spell_ids remain descriptive, never dependency IDs.

## Validation
After False-to-True notch or a new matching provider bind, an existing consumer rebuilds and injects
the provider on its next meld. Include Optional without a default. Verify watcher replacement/cleanup
and existing collection tests; preserve book-local scope and avoid global invalidation.
<!-- END ENTRY: Required-input frame-key watchers -->
