# Pool hook baselines and root publication

## Scope and accepted behavior
Repair Conduit/Meld/SpellSpace hook lifetime across pooling, and implement explicit shared root
updates. Normal roots own stable native lifecycle/Meld dictionaries copied from selected configuration,
including empty dictionaries. Lessers inherit the root baselines; Spaces capture the immediate owner's
effective Meld hooks. Other normal roots sharing frozen configuration remain independent.

## Interfaces
- Conduit.register_conduit_hooks gains create_local_hooks=True and overwrite=False.
- Conduit.set_conduit_hooks supplies the replacement form, create_local_hooks=True, overwrite=True.
  Nonempty input selects the supplied hook families; empty replacement selects both families.
- Meld.register_meld_hooks provides validated additive/replacement updates with the same flags.
  Shared updates (False) require a normal-root ConduitMeld and update its stable baseline in place.
- Meld.set_meld_hooks retains its internal reference-install semantics when False. It records
  divergence from the baseline; pool/graduation baseline adoption has a separate private seam.
- Observational modification state is bool-based. Do not introduce revision polling or per-meld locks.

## Invariants
Local lifecycle hooks keep existing per-event shadowing/fallback. Local Meld updates copy the effective
map and remain isolated. Shared updates switch the initiating root back to the shared source for the
selected family; other localized consumers keep their own copies. Readers retain existing per-event
dispatch semantics: no whole-operation or multi-family atomic-snapshot guarantee is introduced.

Writers validate whole batches before mutation, serialize on existing locks and publish new event
lists. Shared dictionary identity remains stable. Whole replacement can expose the existing per-event
update progression to concurrent readers; callbacks are never invoked while publishing hooks.

Pool return disposes first, then resets changed state before idle publication. Spaces borrowing a
temporary owner-local map are marked for reset even if they never mutate their own hooks. Root-shared
contents update through existing references without walking descendants.

Graduation initializes new root-owned hook baselines and updates every retained Meld baseline pointer.
No old Book, map or root ownership may be reintroduced when those Spaces later return to their pool.

## Migration / rollback / non-goals
Baseline benchmark -> red regressions -> source initialization/mutation/reset -> compatibility and
cost checks -> source review. Rollback reverts this bounded source/test change without touching Bind
registries, graph compilation or generated assets. No new callback IDs, persistence scheme, arbitrary
raw-list tracking, active-scope source-switch broadcasts, or broad hook standardization.

## Ticket owner
TASK-2026-09-22-add-local-hook-setters-and-tracking owns this approved implementation tranche.
