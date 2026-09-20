# Component Patch: Meld capability refusal

<!-- BEGIN ENTRY: Concrete runtime doors and shared diagnostic -->
## Before and After
Before, False direct targets can fall into missing compilation artifacts or return an existing supplied
object on reuse-only paths. After selection, both concrete doors reject False with MeldExecutionError.
Normal True resolution and existing-object lifetimes retain their current behavior.

## Exact Source Scope
- Meld: add _raise_non_resolvable_registration(Spell), a static cold helper returning NoReturn.
- ConduitMeld.meld and meld_existing_spell: check the native _resolvable slot immediately after lookup.
- SpellSpaceMeld.meld and meld_existing_spell: same policy and diagnostic.
- Update affected method/class contracts. Public facades already propagate the error unchanged.

## State, Failure and Ordering
No new fields, owner objects, locks, registries or cleanup. The immutable native slot is read directly
in the normal path; only the failure calls a helper. Refusal precedes validation skipping, request-scope
checks, execution hooks, existing-object return and codegen context acquisition.
Lookup helpers remain unchanged because introspection shares them. Successful True targets alone can
populate warm doors; the existing epoch/context invalidation remains authoritative.

## Validation
Use real books/conduits/spellspaces. Cover machine IDs, human names, class/frame and named binding;
automatic/dynamic posture; validation enabled/disabled; reuse-only and supplied existing objects;
repeated attempts, overrides/hooks and unchanged True warm reuse. Add a real notch transition where
the public transaction contract supports it. Do not fake a mutable capability on a Spell version.
<!-- END ENTRY: Concrete runtime doors and shared diagnostic -->
