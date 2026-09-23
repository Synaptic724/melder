# Pool reset and shared root-hook updates: investigation

## Scope
Reopened Conduit/Meld/SpellSpace pool work. Graduation is complete. This document proposes behavior;
it does not authorize implementation or reopen general Bind/Spell/Rift hook standardization.
Runtime source, permanent test suites and generated assets were not changed in this investigation.

## Source and runtime findings
The two initial content states both matter: no hooks, and an existing hook list. Separately, each
consumer can still inherit a shared map or hold a local override/copy. A local-modified flag answers
the second question only. Hook count cannot identify same-size replacements or owner pointer changes.

Four current-source probes recorded the following actual callbacks. A is the configured initial hook,
B is the later root hook. Empty means no callbacks. These are observed behavior, not desired contracts.

| Root starts with | Operation | Root Meld | Existing/fresh lesser | Existing/recycled root Space | Fresh root Space |
| --- | --- | --- | --- | --- | --- |
| None | Public register_conduit_hooks adds B | B | Empty | Empty | B |
| A | Public register_conduit_hooks adds B | A, B | A | A | A, B |
| None | Internal Meld setter installs B with create_local_hooks=False | B | Empty | Empty | B |
| A | Internal Meld setter installs B with create_local_hooks=False | B | A | A | B |

The public Conduit registration method always makes local runtime changes. The internal Meld setter's
False mode installs one reference; it does not publish a shared-root replacement. A False flag must not
be described as current tree-wide propagation. Before any update, an empty root's lineage seed is None
and each lesser Meld allocates its own empty map. Populated initial maps are shared by reference.

Six existing characterization cases also passed: lifecycle local shadow/fallback, local Meld copying,
lesser lease leakage, stale Spaces with empty/populated starts and partially applied mixed registration.
They deliberately reproduce current undesirable behavior, rather than testing an implemented repair.

Evidence:
- root_update_results.json and probe_root_updates.py
- existing_probes.log/xml
- src/melder/aether/conduit/conduit.py:334-395, 565-621, 1657-1711, 2269-2428
- src/melder/aether/conduit/meld/meld.py:228-281, 1264-1329
- src/melder/aether/conduit/spell_space/spell_space.py:166-208, 266-398
- src/melder/aether/conduit/spell_space/spell_space_pool.py:119-279

## Recommended ownership model
1. Give each normal root its own live Conduit and Meld baseline containers, including when empty.
   Initialize them with safe container copies of selected configuration; borrow callback objects.
   Shared frame configuration must remain frozen and unaffected by root-runtime edits. Other normal
   roots, including graduated ones, must not receive a different root's runtime changes.
2. Distinguish shared-root mutation, local mutation and internal reference installation. A shared
   update changes the live lineage baseline. A local update retains existing local semantics. Pool
   restoration/graduation attaches the appropriate reference without mutating its previous owner.
   Reinterpreting today's internal setter indiscriminately would risk changing the old root during
   graduation, because that route uses it to install the receiving Book's maps.
3. Keep shared baseline identity stable so already-inheriting scopes can see an initially empty map
   receive hooks and a populated map change. Use method-controlled event-list replacement, not raw
   user-container mutation. Shared configuration is input, never the mutable runtime baseline.
4. Preserve local isolation. Conduit lifecycle currently shadows per event; Meld localization copies
   the effective map. A pooled scope drops its local state at lease end and resumes inheritance.
   Do not silently unify those two existing local semantics as part of this repair.

This makes root-shared changes capable of reaching existing inheritors without walking the hierarchy
on every meld. Native effective hook-map guards already exist on warm doors. Exact publication and
in-flight semantics still need an implementation contract: preserving dictionary identity does not
make a clear-then-update sequence an atomic whole-registry replacement. Writer synchronization belongs
at mutation boundaries; do not promise operation-wide snapshots or add per-meld locks casually.

## Pool responsibilities
| Boundary | Responsibility |
| --- | --- |
| Lesser return | Dispose current-lease creations/Spaces, clear local lifecycle overlays and restore Meld to the live root baseline before idle publication. |
| Lesser acquire | Ensure fresh, prewarmed and reused shells select the same current lineage source. Root-local overlays remain separate from lineage baselines. |
| Space return | Dispose first, then release prior-lease local/inherited map references so idle Spaces cannot retain a temporary owner-local map. |
| Space acquire | Adopt the immediate owner's current effective Meld map; cover both acquire/prepare_object and acquire_untracked. |
| Nested Space pools | Returning a lesser cannot leave its old local map retained in idle Spaces; acquisition rebases them after owner reset. |
| Pool/root teardown | Release owned baseline containers and borrowed references after owned idle scopes are destroyed; never dispose callback objects. |

A fixed pool-construction snapshot conflicts with live root changes. If saved pool state is retained,
it must represent the live chosen source or have a deliberate refresh protocol. A dirty bool remains
useful for local lease cleanup, but cannot be the sole mechanism for inherited updates.

## Behavior choices to make explicit before code
- Recommended: root-shared edits affect already-active scopes still using that shared baseline, as
  well as future leases. Explicit local overrides retain their current isolation until cleared/recycled.
- Spaces use their immediate owner's effective source at acquisition. Changing an owner's choice of
  local versus shared source while a Space is already active is distinct from editing the contents of
  the shared root baseline; do not silently promise live source switching for that case.
- Define whether set replaces specified events or the complete selected map. Empty replacement must
  clear/mute or resume inheritance according to that explicit rule, not dictionary truthiness by accident.
- Preserve current lifecycle versus Meld exception policies and callback timing.
- Keep public root-shared writes distinct from internal reference binding. Do not mutate frozen policy
  or turn trusted reset/adoption calls into broadcast writes.

## Proposed implementation sequence
1. Agree shared/local mutation and replacement semantics using the scenarios above.
2. Add failing regressions for empty-to-hooks, same-size replacement, clear/re-add, local isolation,
   already-existing inheritors and independence of two normal roots sharing configuration.
3. Implement root-owned baselines and the requested Conduit setter/Meld registration methods; validate
   complete batches before mutation and track local divergence at those supported seams.
4. Repair lesser and both Space lease boundaries, including nested idle pools and reference release.
5. Qualify concurrency/publication and warm/no-hook compatibility, then measure actual lease/dispatch
   overhead. The earlier scalar-read benchmark is not an end-to-end performance result.

## Owner performance constraint
Hook mutations are rare. Keep validation, container copying and writer synchronization on those
mutation paths. Use simple per-runtime restoration flags at pool boundaries, with reference reset
only when required. Preserve existing scope locks and managed Space thread confinement; do not add
a lock, revision poll, copy or hierarchy scan to ordinary Meld execution.

The flag must also cover a Space acquiring its owner's temporary local map, even when the Space
does not call a mutation method. Mark that inherited divergence at acquisition so the same bool can
drive return-time restoration. Stable root baseline maps let shared updates flow without marking or
visiting descendants. Exact implementation and end-to-end costs remain unmeasured.

The existing graduation hook-initialization route must use the same new root-baseline ownership rule
when this is implemented. That is integration with its completed contract, not a return to the old
discarded-Book defect. Bind registries and registration semantics otherwise remain outside this slice.
