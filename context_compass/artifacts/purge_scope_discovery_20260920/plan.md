# Purge discovery and implementation plan

- Ticket: TASK-2026-09-20-discover-purge-scope-ownership
- Epic: EPIC-2026-09-19-scope-aware-creation-purge
- Agent: updater_0
- Updated: 2026-09-20T21:43:07Z
- Status: discovery complete; implementation not started

## Owner's final direction

Purge mirrors meld's targeting and scope mechanics for creation removal:

```text
Conduit.purge(...) or SpellSpace.purge(...)
    -> Meld resolves the actual Spell using existing selectors
    -> Spell.existence + actual caller determine authority and target store
    -> target_creations.purge(spell)
```

Extend Creations with a dedicated purge operation. Do not use extract_spell_creations, transfer
payloads or restore helpers. Retain the Spell, binding, compiled plans and scope object.

The owner explicitly settled lineage-root-only authority and strictly local SpellSpace purge.
SpellSpace is not a conduit, even when its owner is the root or elected cluster leader.

## Authority and storage matrix

| Existence | Store used by current generated execution | Authorized purge caller |
| --- | --- | --- |
| many via Conduit | Calling Meld's _conduit_creations, when disposal tracking exists | That conduit, root or lesser |
| many via SpellSpace | Calling Meld's _spellspace_creations, when disposal tracking exists | That exact SpellSpace |
| unique_per_spell_space | _spellspace_creations | That exact SpellSpace; no conduit or ambient-scope fallback |
| unique_per_conduit | _conduit_creations | That exact conduit; SpellSpace cannot act for it |
| unique_per_conduit_lineage | _root_creations | The lineage root itself |
| unique_per_conduit_cluster | _cluster_creations.resolved_store() | The elected leader itself |
| unique | Resolved Spell._owner_creations | The Spellbook's owning/root conduit recorded on the Spell |

The meaningful identity is Meld._conduit_id. A lesser's _resolution_conduit_id is its compilation
root and must not confer purge authority. Creations.owner_conduit_id identifies the conduit owning
the chosen store. For unique, also use the resolved Spell's live owner information. For cluster,
the elected store owner may differ from the binding owner; requiring both would refuse valid purges.

The SpellSpace branch must terminate at its own store. It cannot fall through into conduit routing.
The actual door/store supplies scope; there is no caller-supplied owner id to trust.

Evidence:
- src/melder/aether/conduit/meld/meld.py:163-295
- src/melder/aether/conduit/conduit.py:309-405
- src/melder/aether/conduit/spell_space/spell_space.py:169-212
- src/melder/aether/conduit/conduit_cluster.py:637-692
- src/melder/aether/spellbook/spell.py:1392-1441
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-870
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:763-815

## Implementation sequence

### 1. Add the native Creations operation

Proposed internal signature: purge(spell: Spell) -> int.

- Use spell.spell_id as the key and spell.existence to distinguish one singleton from a many bucket.
  Do not guess multiplicity from the returned object's Python type: an application object can be a list.
- Detach that key from both _creations and _disposable_creations using the existing writer locks.
- Apply the established disposal metadata to detached objects. Many entries dispose newest-first;
  each object's method names run in their established order.
- Reuse _attempt_cleanup and the existing error-aggregation contract. Attempt other detached objects
  after one object fails, then raise an ExceptionGroup. Removed entries stay removed after a failure.
- Finish detachment and release synchronization before invoking user cleanup callbacks. Do not
  restore disposed objects or remove any replacement entries created after the detach.
- Preserve the store, its id/owner, unrelated keys, borrowed disposal-name lists and pool state.
- Proposed return: number of removed creations, zero for an empty matching slot. A targeted many
  purge removes the retained bucket for this Spell; selecting one particular instance is not added.

This is a native operation over Creations. No transfer-row construction or extraction helper is needed.

### 2. Add shared Meld purge orchestration

- Reuse _resolve_spell and its existing id/name/type/frame/binding selection machinery.
- Inspect the resolved Spell and the concrete Meld's existing store references.
- Apply the authority matrix before removing or disposing anything.
- Call the authorized store's dedicated purge operation with the Spell itself.
- Give wrong-scope/root refusals a clear error identifying the target and required calling scope.
- Do not enter meld execution, create a context, run constructors, perform dependency compilation,
  or add permission/lookup fallbacks over global registries.

Ordinary lookup failures remain lookup failures. The discovery found an elected leader can hold
an instance while lacking a borrowing link for its definition; such a leader cannot select that
Spell through normal meld lookup either. Owner's simplification keeps the same selection boundary.

### 3. Add the two public facades

Mirror the public meld selectors on Conduit and SpellSpace:
purge(spell=None, *, spell_id=None, spellframe=None, binding_name=None).

- Positional strings remain logical SpellNames; SHA identities use spell_id.
- Retain mutual-exclusion and cleaned-scope checks.
- Forward to the scope's existing Meld object.
- Conduit supports its local and authorized broader stores.
- SpellSpace supports only its own Creations. Its caller kind remains explicit through the existing
  SpellSpaceMeld instance/_spellspace_creations reference.
- Purge does not exit a managed scope, change the thread stack, recycle a shell or clean its Meld.

Expected production edit surface:
- src/melder/aether/conduit/creations/creations.py
- src/melder/aether/conduit/meld/meld.py
- src/melder/aether/conduit/conduit.py
- src/melder/aether/conduit/spell_space/spell_space.py

ConduitMeld/SpellSpaceMeld only need separate edits if placing a scope-specific helper there is clearer.
No new scope registry, compiler stage, instance wrapper or runtime cache layer is required by this plan.

### 4. Qualify behavior, document and regenerate assets

Build regressions for the exact authority/removal matrix before finishing implementation. Update
the relevant component descriptions, source descriptors and public API documentation; regenerate
their indexes and existing build assets after the code change. Keep the ordinary meld path unchanged.

## Existing lifecycle rules the implementation must preserve

- Managed many objects are tracked only when disposal methods exist. Untracked many objects are
  caller-held references; purge cannot enumerate them and must not add new per-meld tracking.
- Root and generated dependency executors read live stores. Warm Meld caches hold Spell/context/epoch,
  not returned instances. Clearing a store does not require recompiling those plans.
- Singleton creation locking differs: unique root execution uses Spell._lock; conduit, space,
  lineage and cluster root execution use their store lock. Generated shared dependency paths can
  take Spell then store locks. The unique purge detach must coordinate with that same writer lock
  as well as the store lock; passing the Spell gives Creations the required information.
- Keep removal atomic for the two registries, but do not promise that another thread or object
  relinquishes a reference it already obtained. An in-flight many constructor can register a new
  instance after the detach. Whole-application draining is not part of this operation.
- Concurrent ownership transfer, election, notch and scope retirement require their existing
  coordination/lifecycle contracts. Do not introduce new hot-path gates to turn purge into a
  universal transaction system. Verify lock ordering and topology stability in the focused tests.
- Existing consumers keep their injected references. Purge targets one Spell's retained creations;
  it does not recursively rebuild consumers or clear their dependencies.
- Existing supplied objects have a second, authoritative reference in Spell.user_created_object.
  Store removal does not withdraw that reference: subsequent meld still returns the same object.
  Keep purge's Creations-only meaning explicit; do not redesign supplied-object ownership here or
  promise fresh reconstruction for supplied objects.
- A pooled SpellSpace retains its id, store and Meld. Managed scopes are thread-confined; direct
  manual scopes already support sharing. Purge must not impose a new active-thread-stack requirement.
- Lesser recycle clears local state; upgrade retains the local store and changes root/facade wiring.
  Use live owners each time rather than saving purge-specific owner data across those transitions.
- Transfer changes unique ownership/store, while lineage instances remain in their resolving roots.
  Ownership checks must follow the live Spell after a completed transfer.

Evidence:
- src/melder/aether/conduit/creations/creations.py:154-551
- src/melder/aether/conduit/meld/conduit_meld.py:242-415
- src/melder/aether/conduit/meld/spellspace_meld.py:562-632
- src/melder/aether/conduit/spell_space/spell_space_pool.py:145-279
- src/melder/aether/conduit/conduit.py:533-621
- src/melder/aether/conduit/conduit.py:1960-2140
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:361-435
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1374-1572
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:77-237
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:871-1145

## Regression matrix for implementation

1. For every row in the authority table: authorized removal, wrong-caller refusal and unrelated
   scope preservation. Include a cluster leader distinct from the binding owner and lessers
   whose resolution id equals the root while their caller id does not.
2. Singletons, many buckets and legitimate list/dict/falsey singleton values; missing entries,
   repeat purge, disposal order, multiple disposal methods, failures and no duplicate later cleanup.
3. Root/lesser/manual SpellSpace/nested managed SpellSpace calls, direct shared SpellSpace calls,
   pool reuse and lesser upgrade. Purge leaves the same usable scope/store/context alive.
4. Same warm context, fresh subsequent factory instance; both generated dependency and direct-root
   execution, hooks/overrides, automatic/dynamic modes and cached executor hydration.
5. Existing dependent retains its original reference; unrelated parent/dependency stores survive.
   Supplied-object reference behavior remains explicit and separate from factory reconstruction.
6. Deterministic barriers around registration versus removal, simultaneous purges, disposal failure,
   and replacement registration. Check live/disposal map coherence and no stale deletion of replacements.
7. Completed transfer/election/notch followed by purge uses current ownership/selection. No fallback
   to invisible or parked definitions merely because an old store key exists.

Existing suites to extend or reuse:
- tests/unit/melder/aether/conduit/creations/test_creations.py
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py
- tests/unit/melder/aether/conduit/creations/test_creations_many_first_use_atomicity_regression.py
- tests/component/melder/aether/conduit/test_conduit_component_creations.py
- tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py
- tests/integration/melder/conduit/test_conduit_integration_lineage_isolation.py
- tests/integration/melder/conduit/test_conduit_integration_cluster_isolation.py
- tests/experimentation/test_spellspace_cross_thread_scope_experiment.py

## Executed discovery evidence

38 passed, 2 deselected in 0.80s using the existing .venv_new through uv --no-sync --offline,
with Python -X gil=0. Sixteen new characterization cases exercise existing behavior; twenty-two
existing scope/component/integration cases supply baseline evidence. The two deselections are
existing extract/restore cases, unrelated to the requested native purge implementation.

The characterization deliberately calls existing clear_all on isolated stores. It proves current
store/context behavior; it is not a purge implementation or proof that purge authorization works.

The first executable run had one missing-link fixture failure. That condition is now an explicit
unlinked characterization beside the linked recreation case; both pass. An earlier uv startup
failed on the user-cache ACL and was retried using a task-local cache without syncing dependencies.

- test_store_characterization.py
- characterization_final.log
- characterization.xml
- characterization_retry.log (initial missing-link observation)
- characterization.log (initial uv cache-access failure)

No performance benchmark, full suite, purge API or runtime change was performed in this discovery.

## Re-entry reading order

Start with this plan and the task's latest notes. Architecture and component indexes were verified
against current document hashes during discovery. Relevant component slices:
Conduit Runtime; Creations and SpellSpace; Meld Resolution Runtime; ConduitWard and Contracts;
ConduitCluster Auto-Sharing; SpellSpace Thread State; SpellCompiler and Validation Pipeline.

Then read the exact source methods cited above and the complete implementation units to be edited.
The source graph/index is navigation only. Several current docstrings and component passages still
describe active-stack/versioned SpellSpace checks or route all shared modes to the spell owner;
those descriptions disagree with the source and must not drive the purge implementation.
