# Pool hook repair: source review

Updated: 2026-09-22T16:52:18Z
Ticket: TASK-2026-09-22-add-local-hook-setters-and-tracking

## Delivered behavior

- Lesser conduits discard temporary Meld callbacks after disposal and before returning to the pool.
- Manual, managed and prewarmed SpellSpaces release temporary hook maps before idle publication.
  Acquisition selects the immediate owner's current effective hooks when that owner is localized.
- Each normal root owns stable runtime maps copied from configuration, including empty maps.
  Explicit shared updates reach scopes still borrowing those maps. Local copies remain isolated.
- Graduation attaches fresh root baselines to the conduit and retained SpellSpaces. Later pool
  returns cannot restore the old root's map. Bind ownership and the independent empty Book remain.
- Permanent Space cleanup retires its owned Meld, releasing its baseline/effective callback references.

## Controls

```python
# Append locally. Other scopes keep their own hook selection.
conduit.register_conduit_hooks({"on_meld_pre_resolve": callback})

# Replace the supplied Meld family on this conduit.
conduit.set_conduit_hooks({"on_meld_pre_resolve": replacement})

# Publish a shared update from the normal root.
root.set_conduit_hooks({"on_meld_pre_resolve": replacement}, create_local_hooks=False)

# Clear that shared family; existing inheritors observe the empty baseline.
root.set_conduit_hooks({"on_meld_pre_resolve": []}, create_local_hooks=False)
```

Registration defaults to create_local_hooks=True and overwrite=False. Conduit setting defaults
to overwrite=True and replaces only the supplied families: lifecycle and/or Meld. Empty setting
selects both. Existing lifecycle semantics remain event shadow/fallback; empty local lifecycle
replacement reveals the baseline. Empty local Meld replacement mutes its effective map until reset.

Meld.register_meld_hooks provides equivalent additive/replacement controls for its own family.
Shared publication is normal-root-only. The older internal set_meld_hooks reference mode still
installs a reference without broadcasting; pool/graduation baseline attachment is a separate helper.

## Performance and concurrency

Ordinary ConduitMeld and SpellSpaceMeld execution files are byte-identical to their pre-change hashes.
Unchanged lesser return adds one bool read. Unchanged Space acquisition/return each adds one bool read.
Only changed scopes take their existing Meld lock to restore a reference and clear the bool.

Writers validate complete batches before mutation and use existing locks. Shared dictionaries retain
identity; event lists are replaced. Local copying takes a shallow mapping snapshot before copying lists
because a root writer may edit the source concurrently. These costs are confined to rare mutation.

Root updates preserve existing per-event visibility, not an atomic snapshot spanning an entire meld
or both hook families. Active Spaces keep their selected source if the owner switches local/shared
maps; the next acquisition selects the current owner. Direct external map/list mutation is unsupported,
and local mutation must finish before the scope is handed back to its pool.

Seven repeats of 20,000 warmed empty cycles, one thread, Python 3.14.7 free-threaded, GIL disabled:

| Pool cycle | Initial hooks | Before ns | After ns | Change |
| --- | --- | ---: | ---: | ---: |
| Lesser | Empty | 1313.915 | 1332.870 | +1.4% |
| Manual Space | Empty | 680.160 | 710.160 | +4.4% |
| Managed Space | Empty | 404.655 | 446.375 | +10.3% |
| Lesser | Seeded | 1623.665 | 1678.195 | +3.4% |
| Manual Space | Seeded | 668.110 | 706.390 | +5.7% |
| Managed Space | Seeded | 403.685 | 443.265 | +9.8% |

These microbenchmarks exclude setup, construction work and application callbacks. They measure
pool boundaries, not full application throughput or contention. Raw samples are retained in the
before/after JSON reports; the managed empty cycle has the largest relative increase.

## Verification

- Final affected run: 2102 passed, two pre-existing owner-deferred shared-context investigation skips.
- 73 new parameterized cases: 21 pool regressions, 46 control/lifecycle/concurrency cases and six
  automatic-mode warm-door cases. The first 17 pool cases failed before repair; four additional
  prewarm cases reproduced its separate bypass before that repair.
- Automatic warm-door checks prove shared/local add and clear take the hook lane when necessary,
  then recover the existing fast lane without recompilation or cache reset.
- New test-module Ruff checks and fatal syntax/name checks for all touched runtime/test files pass.
- Scoped whitespace check passes. No coverage measurement was run.
- Both concrete Meld files, source version 0.2.45 and all 26 held packaged assets match their baselines.

Evidence: final.log/xml, lint.log, preservation.json, pool_before.json and pool_after.json in this folder.

## Source map

- src/melder/aether/conduit/conduit.py:549-579 — lesser return restoration.
- src/melder/aether/conduit/conduit.py:1108-1157 — prewarm idle restoration.
- src/melder/aether/conduit/conduit.py:1654-1838 — root ownership, diagnostic and public controls.
- src/melder/aether/conduit/meld/meld.py:1273-1483 — baseline/adoption/reset and mutation controls.
- src/melder/aether/conduit/spell_space/spell_space.py:305-410 — manual/managed/permanent cleanup.
- src/melder/aether/conduit/spell_space/spell_space_pool.py:146-211 — current-owner adoption.
- src/melder/aether/spellbook/spellbook.py:6797-6828 — graduation baseline rebinding.

## Review boundary

The source and tests are ready for review. Generated/build assets remain held. Canonical map/descriptor
promotion and packaged generation remain the follow-up after approval; the active patch records the
complete behavior delta meanwhile. No version bump, Bind change or broader hook standardization.
