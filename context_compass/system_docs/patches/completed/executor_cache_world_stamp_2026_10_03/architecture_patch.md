# Architecture patch: an executor-cache full hit requires the world stamp

- Patch id: executor_cache_world_stamp_2026_10_03
- Status: promoted and archived (was the entry gate for TASK-2026-10-03-require-world-stamp-for-executor-cache-full-hit)
- Owner: fable_0
- Created: 2026-10-03T20:43:11Z

<!-- BEGIN ENTRY: "Executor cache world stamp: objective, non-goals, invariants" -->
## Objective
The conduit creation-cache bundle records the world its executor payloads were compiled in - the structural
tier's world stamp (sha256 over the sorted pool ids, the frame posture and the sorted borrowed ids) - as one
envelope field written at staging, and the executor tier admits a full hit only when the live world carries the
same stamp. A world that differs only by an existing creation or a non-resolvable definition - ids the executor
tier never counts, because such spells carry no payload - no longer replays a consumer's executor compiled when
nothing provided one of its parameters: it recompiles phases 8-11 for every eligible spell and re-stages the
bundle under the new stamp, exactly as a missing live spell does. The two cache tiers become coherent: a world
the structural tier reruns is a world the executor tier recompiles.

## Non-goals
- The structural tier: its per-row stamp, key and replay rule are reused unchanged.
- A per-spell resolution fingerprint (a finer key than the world): a second keying scheme beside the structural
  rows; not needed, since the mixed path already recompiles the whole eligible set.
- The Autofac-strict matching rule (owner: not wanted); the rebind-after-first-meld defect (its own lane).

## Invariants
- A full hit requires, as before, every live payload-eligible spell cached, and now the recorded stamp equal to
  the live stamp. All payloads matched under a different stamp is a mixed path (recompile and re-stage), not a
  full hit; no payload matched is still a full miss.
- The stamp is written at staging, after every live payload is re-staged, so a bundle on disk never carries a
  stamp newer than its payloads; a stamp that changed is persisted even when no payload byte changed.
- A bundle without the field (hand-made) carries "" and never full-hits: the rule fails closed.
- Repeat worlds are byte-for-byte full hits: same pool ids, posture and borrowed ids give the same stamp, so the
  bundle file is not rewritten (the existing restage and structural-capture contracts hold).
- A world that only removed a spell is a changed world: it recompiles once (mixed) and full-hits afterwards.
  The former "stale surplus cache still full hits" contract is retired on purpose: a surplus id means the
  world changed, which is the hole the defect lived in.

## Interface deltas
- Public API: none. Behaviour: the reproduced defect (a bare existing Service added beside a Worker whose
  cached executor was compiled with service unresolved) resolves after the fix; its inverse (provider removed)
  raises UnresolvedInputError instead of running a plan that names a spell outside the world.
- Private: envelope field `world_stamp: str`; `CachingSystem.world_stamp` (property) and
  `set_world_stamp(stamp) -> bool` (changed); `_build_conjure_cache_state` returns `world_stamp` and
  `world_matches`; cache generation 19 (`executor_world_stamp`).

## Migration order
1. `CachingSystem`: the envelope field (empty store, optional on load as a str, always written), the property
   and the setter under the instance lock, generation 19.
2. `SpellbookCreationSystem._build_conjure_cache_state`: compute the live stamp when caching is enabled and
   fold `world_matches` into the full-hit rule; `_stage_spell_payloads_at_conjure_end`: record the stamp after
   re-staging and flag the emit when it changed.
3. Tests: unit (classification, staging, envelope), the schema-history pin, the integration contract re-pinned,
   one component regression file (red before, green after).
4. Docs (component Spellbook Core, architecture invariant and handoff), release note, notch, assets last.

## Rollback
Drop `world_matches` from the full-hit rule; keep the field and the generation.

## Ticket coverage matrix
| patch section | ticket | validation |
| --- | --- | --- |
| envelope field, property, setter, generation 19 | TASK-2026-10-03-require-world-stamp-for-executor-cache-full-hit | caching-system unit tests, history pin |
| full-hit rule, staging write | same | cache runtime unit tests, component regression, integration re-pin |
<!-- END ENTRY: "Executor cache world stamp: objective, non-goals, invariants" -->
