# Normal conjure and the separate existing-conduit route

## Owner rulings
- The NEW PRIVATE CONJURE METHOD BELONGS TO SPELLBOOK. Conduit is the supplied target and the
  public upgrade entry; it does not own a second conjure/adoption orchestrator.
- Keep normal conjure separate. Duplication is acceptable; correctness and explicit organization
  take priority over a generalized route, bypass booleans or branching throughout normal conjure.
- Create a new empty Book. No existing Book, definitions, indexes or implicit contracts transfer.
- Preserve the existing Conduit object/id and its creation store; creation retention is separate
  from definition visibility. Initialize configuration and hooks as an ordinary new Book would.
- Optional configuration uses ordinary local/default/frame-wide selection.

## Current normal call chain (source verified)

| Stage | Source owner and behavior |
| --- | --- |
| Public admission | Spellbook.conjure starts CONJURE on the Book identity, then settles/inherits the frame mode. |
| Book window | _conjure_within_transaction_window takes the Book lock, enforces one conjure, checks recorded configuration discipline and spell ID integrity. |
| Orchestration | Constructs one SpellbookCreationSystem, calls its conjure and cleans that helper in finally. |
| Configuration | _prepare_spellbook_for_conjure validates/freezes unlocked config, binds frame/shared policy and runs structural phases. |
| Cache classification | _build_conjure_cache_state compares only this Book's eligible live IDs with its cache. |
| Resolution identity | _prepare_resolution_for_conjure unconditionally mints a new ID, then runs resolution phases using it. |
| Resolution/policy gates | Enforces the non-cache-hit resolution verdict and normal frame/policy eligibility. |
| Pre hook | Fetches selected Book configuration events and invokes on_conduit_pre_created with no arguments. |
| Allocation | _build_conduit resolves name/config/frame/gate controller and constructs Conduit in normal state. |
| Constructor side effects | Conduit establishes stores/Meld/pools/ward, registers its root and Book spell ownership, refreshes identity and emits its Conduit twin. |
| Activation | _activate_conjured_conduit sets Book._conjured and Book._conduit, refreshes Book identity, clears pending keys and invokes activation. |
| Owner/publication tail | Stamps this Book's own spells, handles ordinary cache staging/emission, publishes Nexus state, registers RiskManager and invokes post. |
| Return/unwind | Returns the new Conduit; cleans the one-run helper and ends the admitted Book transaction. |

Key consequences:
- Reusing a Conduit requires reusing its ID BEFORE phases. Skipping only allocation leaves resolution
  scoped to an unrelated freshly generated ID.
- The normal constructor does more than allocate. Its root registration, new Book ownership mapping,
  normal pool/ward/gate wiring and record emission must be provided by the Book-owned adoption route.
- Setting Book._conjured or assigning Book._conduit alone bypasses normal activation and publication.
- Existing upgrade's copy of the old root's resolution state is inappropriate for an empty Book.
  Use resolution results from the new Book under the preserved target ID.
- Empty Books still traverse the normal phase orchestration. Full cache hit requires a nonempty
  live spell set; an old cache does not create registrations in the new empty Book.
- define_conduit_into_spells iterates only the new Book's local registry; it does not migrate old spells.

## Dedicated Spellbook route to implement
1. Conduit.upgrade_to_normal remains the public initiation point, supplying its own reference, name
   and optional configuration. Spellbook owns creation/preparation of the fresh Book and conjuring
   that Book against the supplied target.
2. Add a separately named private Spellbook conjure route. Preserve its own explicit admission,
   single-conjure checks and error flow; do not modify public conjure into a flag-driven multiplexer.
3. Reuse suitable existing configuration, structural-phase, cache, policy and hook helpers directly.
   Run resolution through run_resolution_phases_for_conduit with the existing target ID rather than
   calling the helper whose contract is to mint a fresh ID.
4. At the materialization stage, the Book-owned route adopts the supplied target in place. It must
   establish independent normal ownership, detach old lineage ownership, replace Book/map references
   and hook policy, reset lookup caches, refresh affected Space runtimes and retain creations.
   Do not rerun Conduit.__init__ or allocate another Conduit.
5. Use the common activation/publication helpers where valid, including Book identity, hooks,
   risk registration and Nexus publication. Explicitly preserve Conduit and Book record emission.
6. Return the supplied object from the private route. Public upgrade may keep its existing None
   return contract; no second scope becomes visible.

The exact private helper split should follow these ownership boundaries. The whole conjure
orchestration remains in Spellbook/the existing Book-owned creation machinery, never in a new
Conduit method. Do not force deduplication with the ordinary path.

## Required correctness qualifications
- Normal CONJURE admission currently claims only the new Book. Its strategy explicitly assumes the
  Conduit does not yet exist; it does not protect a live lesser. The adoption path needs explicit
  target lifecycle/gate protection using existing mechanisms, with tested failure release.
- Validate configuration, name/collision, hooks and current graduation admission before irreversible
  topology changes. Existing ward conversion is childless-only and must fail before a state flip.
- A failed new-Book setup must leave the original runtime usable and release only newly owned state.
- Reset both input-resolution and fast-meld-door caches when changing Book lookup ownership.
  Leaving an old fast-door reference can still execute a formerly visible spell.
- SpacePool retains ConduitMeld, and existing/idle Spaces retain separate SpellSpaceMeld aliases;
  replacing only Conduit._spellbook does not migrate those runtime references.
- Current shared-config adoption sets _configuration_locked. The normal prepare helper skips freeze
  in that case, although freeze is the Book-twin producer. Verify explicit new-Book emission for the
  adoption route rather than assuming a constructor skip records the new Book.
- Preserve lifecycle hook arguments/order: pre(), activation(target), post(target). Existing
  lifecycle callback failures are logged/suppressed by the existing dispatcher.
- No callback serialization, normal meld hot-path changes or build-asset generation.

## Tests
- Private conjure returns the exact supplied Conduit and preserves its ID/Creations.
- No second Conduit allocation/registration; new Book's public conduit property targets that object.
- New Book owns no previous spell definitions; old IDs fail lookup after upgrade.
- New binds and all hook changes stay independent, including local/shared configuration.
- Both cleanup orders preserve the other independent normal root and its own bindings.
- Fresh/pooled Space requests see the new Book and cannot use stale lookup caches.
- Wrong configuration, duplicate root name and unsupported target shape fail before partial adoption.
- Normal public conjure phase/hook/registration behavior remains covered unchanged.
- Recorder-active local/shared config captures the new Book and preserved Conduit identity.

## Required source rereads
- src/melder/aether/spellbook/spellbook.py:6494-6745
- src/melder/aether/spellbook/spellbook_creation_system.py:132-347
- src/melder/aether/spellbook/spellbook_creation_system.py:349-487
- src/melder/aether/spellbook/spellbook_creation_system.py:822-1018
- src/melder/aether/spellbook/spellbook_creation_system.py:1104-1316
- src/melder/aether/spellbook/spellbook_creation_system.py:1359-1540
- src/melder/aether/spellbook/spellbook_creation_system.py:1708-1787
- src/melder/aether/spellbook/spellbook_creation_system.py:1852-1939
- src/melder/aether/conduit/conduit.py:295-466
- src/melder/aether/conduit/conduit.py:1366-1384
- src/melder/aether/conduit/conduit.py:1961-2140
- src/melder/aether/aetheric_frame/aetheric_frame.py:340-409
- src/melder/aether/spellbook/spellbook.py:5745-5784
- src/melder/aether/spellbook/spellbook.py:6060-6085
- src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/conjure_transaction_strategy.py:22-158
- src/melder/aether/conduit/meld/meld.py:228-362
- src/melder/aether/conduit/spell_space/spell_space.py:166-208
- src/melder/aether/conduit/spell_space/spell_space_pool.py:119-279

Before coding the target protection, read the relevant CreationGate/CreationGateController method
bodies (not only their signatures) and their existing callers. No claim that this protection has
been implemented or qualified is made by this trace.

## Status
Source trace and owner-corrected plan only. No runtime edits or new test execution in this pass.
