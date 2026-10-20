# Component patch: SpellbookCreationSystem - conjure wires parked versions

## Metadata
- Patch ID: parked_versions_wired_at_conjure_2026_10_16
- Component: `SpellbookCreationSystem.define_conduit_into_spells`
  (src/melder/aether/spellbook/spellbook_creation_system.py)
- Writer: melder_0 (synaptic_python_developer)
- Created: 2026-10-16T09:42:54Z
- Status: built as written; promoted at landing (0.2.8248) and archived 2026-10-16T11:41:08Z

## Before (0.2.8247)
- `define_conduit_into_spells(spellbook, conduit)` is conjure's owner wiring, called once from the conjure tail after
  the `on_conduit_activated` hooks and before the creation cache loads. Under the Book lock it walks
  `spellbook._spells` (the active versions) and for each one: `spell._add_owned_conduit(conduit._id, conduit._name,
  conduit._creations, dynamic_environment=conduit.__dynamic_environment__,
  creation_gate_controller=conduit._creation_gate_controller, caching_enabled=...)`, then
  `spell.resolution_required = False`, then `conduit._register_to_creations(spell, spell.user_created_object)` for an
  existing object (a failure there is logged). Any failure for a spell is logged and the loop goes on.
- `spellbook._inactive_spells` - versions parked by `bind_inactive` - is never walked. A version parked before
  conjure keeps `_owner_creations` None and no CreationContextFactory; `_apply_notch` stamps nothing, so after a
  notch its first meld raises RuntimeError "Spell has no configured CreationContextFactory." (every existence) and a
  managed consumer's per-creation pool read raises the missing-pool MeldExecutionError.
- A post-conjure `bind_inactive` stamps the new parked version with the same `_add_owned_conduit` call and does
  nothing else (no registration, no resolution flag).

## After
- The same method, after the active loop and inside the same `with spellbook._lock` block, walks
  `spellbook._inactive_spells.values()` and stamps each parked version with the identical `_add_owned_conduit` call
  (same conduit fields, same caching posture value computed once at the top). Nothing else is done for a parked
  version: no `_register_to_creations`, no `resolution_required` write.
- A failure for one parked version is logged ("Failed to define conduit into parked spell_id=<id>: <error>", method
  tag `_define_conduit_into_spells`, exc_info) and the loop goes on, the active loop's policy.
- Every parked version is stamped unconditionally, as every active version is: at conjure none can carry a stamp yet
  (a Book conjures once; nothing stamps a parked version before its conduit exists; a transfer needs a conjured
  Book), so no "already stamped" branch is needed.
- The docstring's Contract names the parked versions and why they get the stamp alone.

## Interface deltas
- None. Signature, return value and raised exceptions (none) are unchanged.

## State and failure deltas
- After conjure every parked version has `_owner_conduit_id`, `_owner_conduit_name`, `_owner_creations`,
  `_caching_enabled`, a configured CreationContextFactory and a reset context; a managed parked version has its pool
  in the root's store and an entry in `ReleaseManagedSpell` (`Creations.ensure_managed_quantity`).
- The failure above is gone: after a notch, the parked version's first meld runs the gated revalidation and builds,
  as for a version staged after conjure.
- New logged failure: a raising stamp of a parked version (none known); that version stays unwired, as an active
  version whose stamp raises does today.

## Dependency and ordering
- Lock order: Book lock (held) -> spell lock -> store leaf -> registry leaf, the active loop's order
  (`Spell._add_owned_conduit` takes the spell lock; `ensure_managed_quantity` takes the store lock and registers
  outside it).
- Position: unchanged (after the activation hooks, before the creation-cache load and the conduit phases' cache
  staging). The cache classifies only live, resolvable, non-existing-creation ids, which parked versions are not, so
  the stamp does not change cache classification.

## Validation expectations
- Unit (new file, tests/unit/melder/spellbook/test_spellbook_creation_system_parked_versions.py): parked versions are
  stamped with the active loop's arguments; a parked existing object is stamped but not registered while an active
  one is; a parked version's `resolution_required` is left as it was; one raising parked stamp is logged and every
  other version is still wired.
- Integration (new file, tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py),
  dynamic worlds, both staging moments compared: unique, unique_per_conduit, many, managed_spell_quantity, an existing
  object and a function staged before conjure meld after a notch as when staged after it; before its notch the
  version is not meldable by id in either case; a managed parked version has its pool and its registry entry right
  after conjure and leases from it after the notch.
- Unchanged and green: the existing `define_conduit_into_spells` tests (tests/unit/melder/spellbook/test_spellbook.py,
  tests/component/melder/spellbook/test_spellbook_component_conduit_definition.py), the direct-cleanup lock-order
  component tests, the spellbook unit tree, the conduit integration tree and the crystallizer restore suites, with
  the GIL off and on.
- Acceptance: probes/probe_owner_questions.py Q1 prints "meld works" for every existence without its probe-only patch.
