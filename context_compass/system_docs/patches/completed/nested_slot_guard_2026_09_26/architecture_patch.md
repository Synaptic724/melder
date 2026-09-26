# architecture_patch

## Metadata
- Patch ID: nested_slot_guard_2026_09_26
- Status: draft
- Owner: user (implementation: melder_2)
- Created: 2026-09-26T21:48:30Z
- Ticket: tickets/tasks/2026-09-26_remove_nested_slot_guard_take_task.md

## Objective
A first build through a creation-context door takes its slot's build lock twice today: the route door takes the
store's slot guard, then the normal site plan it calls takes the same RLock again in the root site's miss. The
second take is a re-entrant acquisition by the thread that already holds the lock, so it excludes nothing. For
the two per-scope routes built on every request or space cycle (unique_per_conduit and spellspace roots), the
normal plan stops taking it. About 0.3 us per gauntlet worker cycle on the VM (-4%).

## Non-goals
- No lock is removed from the door, from any non-root site, from override key-set plans or from unique,
  lineage, cluster or many roots.
- No change to who may meld into a spellspace, to purge, to cleanup or to the creation cache.
- No public API, error text or persisted format change.

## Changed Components
- SpellCompiler and Validation Pipeline (code): SitePlanLowering.emit, SitePlanEmission (root-site miss),
  SitePlanOverrideRuntime (normal plan), generalized_hydrator._build_site_plan_runtime.
- Meld Resolution Runtime and Creations and SpellSpace (documentation only): their lock-discipline text says
  doors and plan steps both hold the build lock; it gains the door-held root case.

## Invariants
- I1 (build once): a door-called first build holds the root's slot guard from the door's recheck through the
  root's publication. The guard object is the same one the plan would have taken: both read the root's store
  from the same meld attribute (_conduit_creations, _spellspace_creations), each assigned once in Meld.__init__,
  with no user code between the two reads.
- I2 (same-thread recheck): the root site still rechecks its store after its children are built, so a nested
  same-thread meld that published the root during a child's constructor is returned, not overwritten.
- I3 (eligibility): the root guard is dropped only in normal mode and only for (door route, root existence) in
  {("unique_per_conduit", unique_per_conduit), ("spellspace", unique_per_spell_space)}. Every other combination,
  and any caller that passes no door route, keeps the guard.
- I4 (callers): every caller of the normal plan holds the root's guard: the no-overrides hooks and instance
  doors, the override door's dispatcher fallbacks (overrides None, or a key set with no winner) and the opt-in
  specializer's deopt, which runs inside a door compiled for the same route.
- I5 (unchanged): lock order (build lock first, store lock as a leaf, consumer before provider), purge waiting
  for an in-flight build of the same slot, the cleaned-store refusal, and the hook lanes' exact created flag.

## Interface Deltas
- SitePlanLowering.emit and SitePlanEmission: new keyword door_route_key: Optional[str] = None.
- SitePlanOverrideRuntime.__init__: new keyword door_route_key: Optional[str] = None, used for the normal plan
  only.
- All internal (MELDER KERNEL); the defaults keep today's behaviour.

## Migration Order
1. Patch docs (this folder). 2. Emission, runtime and hydrator edits on the VM copy with docstrings. 3. New
unit and integration tests. 4. Suites on 3.14t (PYTHON_GIL=0 and 1) and the GIL build; 30k soak; VM A/B.
5. Byte-identical device apply; 0.2.73 notch and release entry. 6. Canonical docs, indexes, graph, assets.

## Rollback
- Revert the three files. Emitted plans live only in the in-process code cache; the manifests do not encode the
  lock shape, and the version notch cold-resets persisted creation caches either way.

## Ticket Coverage Matrix
| section | implementation | validation |
| --- | --- | --- |
| I1, I3 | SitePlanEmission root-site miss, eligibility rule | unit: door-held root takes no guard; other roots and no-route callers keep it |
| I2 | recheck kept in the root miss | unit: root published during a child build is returned; integration: nested same-thread override meld |
| I4 | hydrator passes its route key; runtime passes it to the normal plan only | unit: override plans keep the root guard; review of the call sites |
| I5 | no other emission change | integration: concurrent first melds build once, created hooks fire once; lock-order deadlock suite; purge suite |
