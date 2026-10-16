# Epic: managed_spell_quantity - a pooled Existence whose objects are leased from the root and given back explicitly

## Metadata
- Epic ID: EPIC-2026-10-14-managed_spell_quantity
- Status: blocked
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T00:28:29Z
- Updated: 2026-10-16T11:49:54Z
- Target Window: 2026-Q4
- Related Program/Initiative: EPIC-2026-10-05-melder_services_and_pools (the pooled-lifetime goal moved here);
  MelderOps Iris logger churn (priv_commandops TASK-2026-10-05-channel_logger_pooling)

## Problem / Opportunity
MelderOps builds one Iris ChannelLogger per object (about 40 classes). On melder 0.2.8226 a logger meld cost 74-82 us
to create and 6.4-6.7 us to clean up, while a measurement-only pool reused one in about 9 us (parent epic, MEASURE
2026-10-05). Melder has no lifetime that reuses an object across holders: `many` builds a fresh object every time,
and the six existing Existence members cache by scope, never by lease. Melder already pools its own kernel objects
(SpellSpacePool, ConduitPool), elastic since 0.2.8234, but offers nothing like it for user bindings.

The owner chose a seventh Existence member, `managed_spell_quantity`: its objects are built on demand, leased by a
meld or by injection into a constructor, given back explicitly through `ReleaseManagedSpell` (optionally reset) and
reused. The pool lives in the owning root's Creations until that root is torn down, and an ownership transfer
carries it like any other record.

## MRP Alignment (Most Reasonable Product)
One pool per managed spell version in the owning root's store; one way back (`ReleaseManagedSpell`, plus the lease's
`with`); the warm lease is an inline `deque.pop()` and the release an optional reset plus `append`; the elastic mode
reuses the kernel pools' stretch and decay (`AbstractElasticPool`, 0.2.8234) instead of a new retention scheme. The
structure - pools, the release registry, records, transfer - must be right; the objects handed out are the agents'
(src_architecture, "Runtime Model: Structure Is the Contract"). The six existing members do not change: their spell
ids, emitted executors and records stay byte-identical.

## Ticket Contract
- ENTRY_GATE: met 2026-10-15. The design is settled (Decision Log), the owner authorized the build ("implement it"),
  the seven stories are open and the architecture patch doc is written and linked. Each story's own gate is its
  component patch doc plus a patch-section -> implementation -> validation mapping note before its first `src/` edit.
- EXECUTION_BOUNDARY: the Existence enum, the resolution matrix and Phase 6 ScopeOrderingStrategy; Bind (four
  keywords, checks, fingerprint), Spell fields, SpellBinder and scan_bind; the new modules in
  `src/melder/aether/conduit/creations/` (`managed_spell_quantity.py`, `managed_spell_lease.py`,
  `release_managed_spell.py`), the exhaustion error and `ManagedSpellMode`; Creations (pool map, cleanup order,
  extract/restore) and the ConduitMeld / SpellSpaceMeld store readers; phase 9/10 instance classification, phase 10
  family discovery, the generalized manifest, site-plan lowering and the door compiler; `Conduit.managed_spell_meld`;
  TransferOfOwnership; the crystal record, restore/graft replay, RecordVersion and cache generation; package-root
  exports; docs, graph descriptors, README and release note. Excluded: everything under Non-Goals.
- DEPENDENCIES: AbstractElasticPool (0.2.8234); Creations holder records and holder-owned `many` children (0.2.8235,
  0.2.8238); the site-plan lowering and door compiler; transfer moves by default (0.2.8239).
- EXIT_GATE: all eight stories closed with green tests under `-X gil=0` and `-X gil=1`; an emission diff showing every
  non-managed executor byte-identical; benchmarks recorded with no regression on the existing meld shapes; system
  docs, graph, README and release note current; both rebuild `--check` runs print only OK; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST when a change would alter an existing member's behaviour, an existing spell
  id, existing record custody or the frame -> conduit -> Book lock order; BLOCKER when a seam cannot take the managed
  branch without one of those; CONFLICT when a story's finding contradicts this spec (fix the spec first).

## Goals (Outcomes)
- `Existence.managed_spell_quantity`, bound with four keyword options that the Spell keeps.
- Leases by direct meld, by injection into any constructor during a meld, and by `Conduit.managed_spell_meld`.
- One way back: `ReleaseManagedSpell` (`release`, `managed`, `release_all`, `describe`) and the lease's `with`.
- Three modes: `elastic` (reuse, never refuse), `limited_quantity` (refuse at N), `queue` (wait for a release, then
  refuse).
- An ownership transfer carries pools; root teardown disposes what the root's pools hold.
- Measured: a warm lease cycle well under a microsecond and no regression on existing meld paths.

## Non-Goals (Explicit Exclusions)
- No automatic return: nothing returns an object at scope cleanup, no GC hooks or finalizers, no generator leases.
- No record of objects that are out (no identity tracking): a lease that is never released is the agent's.
- No managed purge verb (owner, 2026-10-15); purge leaves managed records untouched.
- No behaviour change to unique, unique_per_conduit, many, unique_per_conduit_cluster, unique_per_conduit_lineage
  or unique_per_spell_space, and no new spell id for an existing binding.
- No release through Aether, no separate ManagedSpells handle, no mixin and no protocol member.
- No async conduits, service methods or signature-scan memo (EPIC-2026-10-05), and no MelderOps code.

## Scope Boundaries
- In scope: everything in the Build Specification below, its tests and benchmarks, and the documentation.
- Out of scope: MelderOps adoption (after a release that contains the member) and the Non-Goals.

## State Transition Event
- from_state: in_progress
- to_state: blocked
- transition_reason: S8 is done and notched 0.2.8248 (conjure wires the versions staged before it, cache generation
  21, `ManagedSpellLease` checked as built; the rebuild runs last, after these records), so every story's work has
  landed (S1-S6 and S8 notched, S7 documentation). The EXIT_GATE's remaining item is the owner's acceptance, a
  reserved decision. Unblock: the owner accepts S1-S8 or redirects. The board row reads `review`.
- prior: blocked -> in_progress (2026-10-16T09:30:00Z): the owner ruled on every open item (S8 builds the conjure
  wiring and cache generation 21; `ManagedSpellLease` stays as built and S8 checks that it works) and melder_1 landed
  0.2.8247 and handed back this lane's files, so S8 ran (DECISION note of that timestamp).
- prior: in_progress (build) -> blocked (2026-10-15T23:43:36Z): every story's work had landed (S1-S6 as
  0.2.8241-0.2.8246; S7 documentation, no notch); the owner's acceptance and the parked-stamp question remained.
- prior: in_progress (design iteration) -> in_progress (build) (2026-10-15): the owner authorized implementation
  ("implement it") and asked for one story per mechanic and an epic detailed enough to survive several
  compactions (Decision Log, 2026-10-15).

## Success Metrics
- A warm lease cycle (meld dispense plus release, resetless elastic binding) costs well under 1 us inside an emitted
  plan; the standalone probe measured 90-140 ns (Notes, MEASURE 2026-10-14T23:45:47Z). The parent epic's targets -
  about 5 us to acquire and about 1 us to return a ChannelLogger-like object, against 74-82 us for a fresh meld - hold.
- Release routing through `ReleaseManagedSpell` adds about 100 ns or less over calling the pool directly.
- A `limited_quantity` pool never has more than N objects alive under a free-threaded stress test; `queue` waiters are
  served by a release or raise at their timeout, never hang.
- Root teardown disposes every idle object and every recorded `many` child (weak-reference tests) and removes the
  root's pools from `ReleaseManagedSpell`.
- Existing behaviour unchanged: non-managed spell ids identical, non-managed emitted executors byte-identical, the
  full suite green in both GIL modes, existing meld benchmarks within noise.

## Build Specification
This section is the contract the stories implement. An UNKNOWN here is read in source by the named story and its
answer recorded (Decision Log or a Note) before anything is built on it. Ranges are 0.2.8240 locations.

### B1 Public surface
```text
Existence.managed_spell_quantity      seventh member, auto(); class spells only
ManagedSpellMode                      Enum: elastic | limited_quantity | queue (the member or its name)
Spellbook.bind / bind_inactive        new keyword-only options (also SpellBinder and scan_bind):
    managed_spell_mode=None             None -> elastic for a managed binding
    managed_spell_limit=None            see the mode table
    managed_spell_timeout_seconds=None  queue only, required there
    managed_spell_reset_methods=None    names of zero-argument methods run on every release, in order
ReleaseManagedSpell()                 the process singleton Aether creates and owns (like Aether's hosted roots)
ReleaseManagedSpell().release(obj, *, spell_id=None, conduit=None) -> None
ReleaseManagedSpell().managed(obj, *, spell_id=None, conduit=None) -> ManagedSpellLease
ReleaseManagedSpell().release_all(objects, *, spell_id=None, conduit=None) -> None
ReleaseManagedSpell().describe(cls) -> Tuple[Dict[str, Any], ...]
Conduit.managed_spell_meld(spell=None, *, spell_id=None, spellframe=None, binding_name=None, override=None)
    -> ManagedSpellLease                meld plus a lease; `with` releases on exit
ManagedSpellLease                     .object, .release() (idempotent), __enter__ -> object, __exit__ -> release
ManagedSpellExhaustedError            a MeldExecutionError: limited at its limit, queue at its timeout
```

| mode | `managed_spell_limit` | `managed_spell_timeout_seconds` | a miss (no idle object) |
| --- | --- | --- | --- |
| elastic (default) | most idle objects kept, int >= 1, default 256; min(20, limit) kept with no clock read | must be None | always builds; stretch and decay like the kernel pools |
| limited_quantity | required int >= 1: most objects alive at once | must be None | builds below the limit, else raises before building anything |
| queue | required int >= 1 | required, > 0 | builds below the limit, else waits for a release (which serves the waiter) up to the timeout, then raises |

- Disposal: the Spell's `disposal_method_names` run only when the pool destroys an object - an elastic trim, a raising
  reset, root teardown of idle objects - never on release.
- Bind refuses (in `Bind._bind_logic`): a `managed_spell_*` option on a non-managed binding (ValueError); a managed
  binding of a function, method, lambda or existing object (TypeError: class spells only); an unknown mode
  (ValueError); a limit that is a bool, not an int or < 1, or missing for limited_quantity / queue (TypeError /
  ValueError); a timeout on elastic or limited_quantity, missing on queue, or not a positive number (ValueError /
  TypeError); reset names that are not a list or tuple of str, or that do not name a callable on the class
  (TypeError / ValueError). Final texts live in the S2 component patch.
- Package root: `ManagedSpellMode`, `ReleaseManagedSpell`, `ManagedSpellLease` and `ManagedSpellExhaustedError` join
  the flat root next to `Existence` (the owner's root ruling of 2026-07-19: user-held surfaces, front-facing enums and
  user-catchable errors reach the flat facade). The lease joined in S4 (its DECISION note); recorded as build
  decisions for the owner's review (Decision Log, 2026-10-15).

### B2 ManagedSpellQuantity - the pool (S3)
- `src/melder/aether/conduit/creations/managed_spell_quantity.py`:
  `class ManagedSpellQuantity(AbstractElasticPool[Any])`, built only by `Creations.ensure_managed_quantity(spell)`.
- Sizes: elastic -> `baseline_idle=min(20, limit)`, `max_idle=limit` and the kernel pools' stretch, settle and decay
  (settled by S3, U5: Conduit builds both kernel pools with `baseline_idle=20, max_idle=256` and every other argument
  defaulted - stretch 0, settle 1800 s, decay 10% per 600 s - and the pool takes the same defaults); limited_quantity
  and queue -> `baseline_idle = max_idle = limit` (fixed capacity: nothing to trim while `count <= limit`).
- State: the base `_idle` deque (idle objects, newest last and warmest); `count` (int: objects built and alive, idle
  plus out); `_condition` (a Condition over the base `_lock`, for queue waits and notifies); `_children_by_object`
  (`id(obj)` -> the disposal-bearing `many` children recorded for that object) and `_orphaned_children` (records
  left by objects dropped while out, kept for teardown); descriptive fields (spell id, spell name, binding name,
  frame, owner conduit id, mode, limit, timeout, reset names, disposal names); a borrowed Spell behind the `spell`
  property, which raises once the pool is torn down (the registry's cold resolver reads it there, and ensuring the
  pool again re-points it at a Spell rebound under the same id).
- Warm paths: a lease is `_idle.pop()` emitted inline in the plan (no method call, no lock); `put_back(obj)` runs the
  reset names in order (outside every lock; `getattr` on a dynamic name), appends, calls the base
  `_rebalance_after_return()` when more than `baseline_idle` are idle, and in queue mode notifies under the condition.
- Cold paths (as built in S3): `reserve()` - elastic: `count += 1` under the lock and `_note_miss()`, returns None;
  limited_quantity: below the limit `count += 1`, returns None; at the limit returns an idle object released since the
  plan's empty pop, else raises ManagedSpellExhaustedError (so the refusal always means every object is out); queue:
  one deadline, then under the condition a free place -> `count += 1`, return None / an idle object -> return it /
  else wait the remaining time, raising at the deadline; a torn-down pool raises its torn-down RuntimeError (woken
  waiters included). `abandon(children, error)` - a failed build: `count -= 1`, notify, dispose the given children,
  their disposal failures added as notes on `error`. `adopt(obj, children)` - record children under `id(obj)`; a
  record already under that id (an object dropped while out) is kept as an orphan for teardown; adopting into a
  torn-down pool disposes the object and its children and raises the torn-down error. `destroy_object(obj)` (the base
  hook used by trims, raising resets and cleanup) - the disposal methods outside the lock, then the object's recorded
  children newest first; `count -= 1` (clamped at 0); notify. `create_object` and `acquire` raise RuntimeError (the
  plan builds, never the pool). `cleanup()` - under the condition drain the idle objects, swap the children maps for
  empty ones and wake every waiter; outside the lock dispose the idle objects newest first with their children, then
  the children recorded for objects still out, then the orphans; failures joined into one ExceptionGroup shaped like
  Creations' (one RuntimeError per failing method, chained); idempotent; the scalar fields stay as documented
  tombstones and the Spell is deleted. `describe()` - the base keys without `in_use_count`, plus identity, mode,
  limit, timeout, count, out count and children recorded.
- After cleanup `put_back` raises RuntimeError naming the spell (its root was torn down; the object is the caller's).
- No reference to an object that is out is kept (owner: "we don't care about identity").
- Settled by S3 (U6): `AbstractElasticPool.cleanup` marks cleaned, destroys the idle objects one by one under `_lock`
  and stops at the first raising destroy, keeping every field; the pool overrides `cleanup` (above) instead of
  reusing it. A trim destroys outside the lock and re-pools the rest when one destroy raises.

### B3 Creations integration (S3)
- `_managed_quantities: Dict[str, ManagedSpellQuantity]` beside `_creations`. Resolution reads `_creations` only, so
  lookups and purge never meet a pool; the live-creation probes read it through `get_managed_quantity(spell_id)`, a
  lock-free get.
- `ensure_managed_quantity(spell) -> ManagedSpellQuantity`: the pool under the spell id, or a new one from the Spell's
  options (map write under the store lock); registered with ReleaseManagedSpell outside the store lock (a store lock
  stays a leaf). Called by `Spell._add_owned_conduit` (spell.py:1558-1607) for managed spells: conjure stamping,
  post-conjure `bind` / `bind_inactive`, the transfer flip.
- `cleanup()` (creations.py:306-363): pools detach with the other maps and are disposed BEFORE the disposable registry
  (pooled objects hold the store's uniques, which registered first), each unregistered; their failures join the
  store's ExceptionGroup.
- `extract_spell_creations` adds a `{"scope": "managed", "disposable": False, "stored": pool}` row and gives the pool
  up (S4: unregister); `restore_spell_creations` takes it (S4: register), replacing a pool already under the id and
  cleaning the replaced one after the store lock, its failures raised as one ExceptionGroup once the restore
  completes (S4: unregister it) - the flip composes an empty pool for the active member before the move restores the
  moved one.
- Settled by S3 (U3): `reset_for_pool` (and `clear_all` through it) runs only on a lesser's store at pool return and a
  spellspace's store at exit, never on a root store, so neither meets a pool. (U4): `ConduitMeld._get_purge_creations`
  selects the caller's own store for a managed spell, where `Creations.purge` returns 0 before any lock;
  `SpellSpaceMeld.purge` keeps refusing it ("purge it from its authorized conduit"); both live-creation probes answer
  from the owner store's pool (`Meld._describe_managed_pool_status`: `is_live` when `count > 0`, `creation_count` the
  count, `storage_scope_kind` "managed_pool", `storage_owner_conduit_id` the owner root; no store or no pool -> 0).
  The Nexus static rooms treat managed like `many` (no stored object to hand out).
- Settled by S3 (U10), changed by S8 (0.2.8248): conjure stamps the Book's active spells and then every version
  parked in `_inactive_spells` with the owner stamp alone (`define_conduit_into_spells`); a post-conjure `bind` /
  `bind_inactive` stamps the new spell and a transfer the members it moves; `_apply_notch` stamps nothing. Until
  0.2.8248 a version parked before conjure had no owner store, and so no pool, until a later stamp; the S5 miss still
  assumes no pool exists (a stamp that raised at conjure is logged and leaves its version unstamped).

### B4 ReleaseManagedSpell and the lease (S4)
- `src/melder/aether/conduit/creations/release_managed_spell.py` (as built in S4; U11 settled): a process singleton
  with the hosted roots' shape (owner, 2026-10-15) - `_instance`, a class `_singleton_lock`, `_initialized`, a
  double-checked `__new__`, a once-only `__init__(*, aether=None)` under the lock that refuses a first construction
  without its host (ValueError, bookkeeping reset), a `cleanup()` that publishes empty maps as tombstones, keeps
  `_lock` and resets the bookkeeping, `_reset_singleton_for_tests()` (a half-built husk's AttributeError ignored, the
  bookkeeping cleared in a `finally`) and `_live_instance()` (the stores' teardown lookup; never constructs).
  `Aether.__init__` builds it last, after Nexus (`ReleaseManagedSpell(aether=self)`); `Aether.cleanup` cleans it
  right after the frames, whose stores unregister their pools first; `ReleaseManagedSpell()` returns the instance,
  and after a reset the next Aether builds a fresh one (a bare `ReleaseManagedSpell()` before it refuses). Like every
  hosted root it stays published when the frames' teardown raises (Aether resets only its own bookkeeping).
  Releasing is a call on this singleton, never an Aether verb (the 2026-10-13 ruling stands). The registry is
  instance state: `_pools_by_class: Dict[type, Tuple[ManagedSpellQuantity, ...]]` (the hot read) and
  `_registrations: Dict[int, Tuple[type, str]]` (`id(pool)` -> class, holding root id), republished whole
  (copy-on-write) under a leaf `_lock` held only to publish; every read is lock-free.
- `register(pool, *, root_conduit_id)` / `unregister(pool)` are called by Creations only, when a store takes or gives
  up a pool: ensure registers after its store lock; extract and cleanup unregister; restore unregisters a pool it
  replaces, registers the one it installs, then cleans the replaced one. `register` is idempotent, records the
  holding root (a pool's own `owner_conduit_id` is fixed at construction and keeps naming its first root after a
  move) and re-keys a rebind that brought another class object; `unregister` does nothing on a cleaned registry.
- `release(obj, *, spell_id=None, conduit=None)`: one dict get by `type(obj)` (the class object, identity-hashed); one
  pool and no filter -> `pool.put_back(obj)`. Otherwise the cold resolver: keep pools whose spell id equals `spell_id`
  and whose holding root is `conduit`'s root (a lesser names its root); when several remain, keep those whose version
  its index selects (cleanup-safe reads: `ManagedSpellQuantity._spell_unless_cleaned`,
  `Spell._spell_index_unless_cleaned`, `SpellIndex._is_selected_unless_cleaned`); exactly one must remain, else
  ValueError listing every candidate (spell id, binding, frame, root, active) and the keywords that pick one. A class
  with no pool -> ValueError (not a managed class in any live root). Release never needs a conduit. Measured (S4): a
  bound `release` adds about 50 ns over `put_back`; the `ReleaseManagedSpell()` call itself costs about 70 ns, as
  `Aether()` does, so hot loops bind it once.
- `managed(obj, ...)` -> `ManagedSpellLease(obj, pool)` resolved the same way; `release_all(objects, ...)` releases
  every object and then raises one ExceptionGroup of the failures; `describe(cls)` -> one dict per pool.
- `src/melder/aether/conduit/creations/managed_spell_lease.py`: `ManagedSpellLease` holds the object and its pool
  (borrowed), releases once (a second release does nothing), `__enter__` returns the object, `__exit__` releases even
  when the block raised and never suppresses. A class, never a generator (+600 ns measured for the generator form).
- Same class, several pools: two binding names, two roots or two frames -> ambiguity unless filtered; one index with
  several versions of the same class object (bind options changed) -> the active version's pool (a notch re-points
  it); a redefined class is a new class object and a separate key.

### B5 Bind options, Spell fields and the record (S2)
- `src/melder/aether/spellbook/existence/managed_spell_mode.py`: `ManagedSpellMode` (auto members `elastic`,
  `limited_quantity`, `queue`; `__str__` the bare name, as Existence).
- Spell keeps normalized values behind read-only properties: `managed_spell_mode`, `managed_spell_limit`,
  `managed_spell_timeout_seconds`, `managed_spell_reset_methods` (None / None / None / () on non-managed spells).
- Flow: `Spellbook.bind` (5392-5694) / `bind_inactive` (5093-5321) -> `Bind._bind_logic` (bind.py:571-820): validate
  and normalize -> `Bind.sha256_profile` (911-1022) -> the Spell constructor (spell.py:302-551).
- Fingerprint: one extra part, only for managed bindings, `managed:<mode>:<limit>:<timeout>:<reset names>`; every
  other spell id stays byte-identical (the `resolvable` precedent). Method bodies are not hashed, so a body-only
  rewrite keeps its id.
- `scan_bind` (scan.py:405) takes the four options as target options and refuses them as metadata keys; SpellBinder
  (spellbinder.py:14) takes the same keywords.
- The crystal records the four values; the restore engine and graft runner replay them through bind; RecordVersion
  4.1.0 -> 4.2.0 (record_version.py:84; "MINOR adds" fields).
- Settled by S2 (landed 0.2.8242; the S2 story's Notes): U1 - `Conduit.bind` / `bind_inactive` are facades and forward
  the four options. U2 - SpellCrystal captures them only for `managed_spell_quantity` (mode by name, limit, timeout,
  reset names as a list) and `describe()` adds the four keys only then; the static
  `SpellCrystal.managed_bind_options(payload)` gives the replay keywords ({} without a mode); RestoreEngine
  `_bind_one_active` / `_bind_one_staged` and GraftRunner `_bind_selected` / `_park_members` / `_merge_members` pass
  them. Normalization is `Bind._normalize_managed_options` (after the disposal names, before the fingerprint; also
  in `spell_id_inspector`); elastic's limit defaults to 256 and is hashed as 256. `ManagedSpellMode` is a
  TYPE_CHECKING import wherever it is only an annotation (owner, 2026-10-15); bind.py imports it at runtime because
  the normalizer uses it. `SpellBinder.as_managed_spell_quantity` is the fluent form; scan's reserved metadata keys
  are 28.

### B6 Classification (S1, S5)
- S1: `Existence.managed_spell_quantity = auto()` (existence.py:3-138); ResolutionStyleMatrix (44-491) - expected
  count 7, the member in the all-names and non-unique tuples, so the callable and existing-object families list it
  unsupported; SpellArtifactProcessor `_build_model_shell` (107-182) maps it to route family `"managed"`; Phase 6
  `scope_rank` (scope_ordering_strategy.py:31-145) gives it 0 with unique - a managed spell may depend on unique,
  managed and many; every holder may depend on it.
- S5: a managed site is per path like `many` (one lease per injection): the `_is_shared_existence` predicates of
  SpellOccurrenceInstanceProcessorStrategy (spell_occurrence_instance_processor_strategy.py:112-118) and
  SpellOccurrenceGraphAnalyzerStrategy (spell_occurrence_graph_analyzer_strategy.py:733-737) return False for it.
- S5: phase 10 discovery - the solo family (solo_codegen_plan_discovery_strategy.py:52-81) declines a model holding a
  managed spell, so the generalized family's site plan is the only lowering that dispenses; many_only already
  declines (not all-many).

### B7 Codegen (S5; as built in 0.2.8245, U7 and U8 settled)
- Four site kinds in SitePlanEmission (site_plan_lowering.py): shared (a slotted existence), `many`, and two managed
  kinds. A LEASING managed site has no winning override key on its own parameters: it is placed like a shared site
  (its own `_miss{i}` context, so its children build only on a miss) and feeds exactly one consumer, its own path's
  (the emission refuses another count with RuntimeError); the root may be one. A FRESH managed site has winning keys
  on its own parameters: it is built like a `many` step with the supplied values and never pooled, counted,
  registered or adopted - the caller's object.
- The lease is emitted right before its consumer's construction region (for a consumer with a miss, at the end of
  that miss's children, before its guard):
  ```text
      try:                                  # automatic owner, owner store set, pool present at emission:
          v{i} = pp{i}()                    #   pp{i} = pool._idle.pop and h{i} = pool, bound as plan constants
      except IndexError:
          v{i} = _miss{i}(meld, h{i}, <outer values>)
  ```
  Otherwise (a dynamic world, an unowned provider) the plan reads the pool per creation,
  `h{i} = spells[i]._owner_creations._managed_quantities[sid{i}]`, and an AttributeError or KeyError becomes
  `_raise_missing_managed_pool(spells[i])`: MeldExecutionError "Managed spell '<name>' has no pool to lease from: its
  owner root was torn down, or its owner store holds no pool for this version. Meld it through a live root that owns
  it." (S8, 0.2.8248; until then the message also named a version staged with bind_inactive before conjure and the
  remedy "stage the version after conjure").
- The miss: the unresolved-input check, `v{i} = h{i}.reserve()` (an idle object served to a queue waiter returns at
  once), `kids{i} = []` when disposal-bearing `many` children live inside, then `try:` the children, the site's own
  leases and its construction, `except BaseException as exc: h{i}.abandon(kids{i} or [], exc); raise`, then
  `h{i}.adopt(v{i}, kids{i})` when there are such children, `return v{i}`. A `many` child inside appends `(vK, dmK)`
  to `kids{i}` instead of `register_many`; shared children publish to their own stores as before.
- Lease return (F9, widened): from a consumer's first lease through its construction - for a shared consumer also
  its guard, recheck and publication - is one `try`; an exception returns every lease taken for that consumer
  (`_return_leases`: `put_back` each, a failing put-back added as a note on the exception) and re-raises. A shared
  consumer that loses its cold race returns its unused leases after its guard (`_return_unused_leases`: all tried,
  the failures raised as one ExceptionGroup). The three helpers are SitePlanRuntimeHelpers static methods, bound into
  a plan's namespace only when it leases.
- Overrides: a winning key on a consumer parameter fed by a managed site removes the site (no lease); winning keys on
  the managed site's own parameters make it fresh (above); deeper keys apply only when the site misses.
- Door (U7): route `"managed"` maps onto the existing `many` template objects in the four route tables (both fast
  bits), so `created` is True on every lease and a direct meld runs the activation hooks (the spell's and
  `on_meld_activation`) for a reused object too. No template is added or recompiled.
- Classification seams (U8): both `_is_shared_existence` predicates answer False for managed (B6); solo discovery
  declines a model holding one (B6); the generalized manifest's route-key whitelist takes "managed";
  `rows_contain_managed_step(rows)` makes `_install_specializing_door` keep the plain door. The lane plan's other
  existence branches are metadata the site plan never reads, and managed rows hydrate in the existing row shape.
- Cache generation 21, "managed_spell_lease_codegen" (S8, 0.2.8248; the owner reversed S5's decision on
  2026-10-16: a codegen change bumps the cache): rows and manifests of existing spells do not change and plans are
  emitted at hydration, so nothing required it, but bundles written before the managed codegen are now retired
  explicitly (each is cold once and rewritten at 21).
- `Conduit.managed_spell_meld` (conduit.py, after `meld`): resolves the target as `meld` does, refuses `spell` with
  `spell_id` and a spell of another existence (ValueError, nothing melded), reads the pool from the version's owner
  store (none -> the missing-pool error), melds the version by id and returns `ManagedSpellLease(obj, pool)`. With
  own-parameter overrides the object is fresh and the lease's release still gives it to the pool (Decision Log).
- Gate met: the emission capture over 4461 non-managed shapes, door bodies and harness worlds is identical before and
  after (the S5 story's MEASURE note); a warm cycle (meld plus release) measured 320 ns on an automatic root and
  742 ns on a dynamic one.

### B8 Ownership transfer (S6; as built in 0.2.8246, U9 settled)
- Rows, unchanged by S6 (S3 and S4 built them): `move_creations=True` (the default) - `_move_creations`
  (transfer_of_ownership.py:1508-1551) extracts every member's rows from the source store and restores them into
  the target, so the same pool object moves with its idle objects, recorded children and count, and the registry
  follows it (unregister at extract; register at restore, which replaces and cleans an empty pool a stamp composed).
  `move_creations=False` - `_teardown_creations` (1553-1586) takes the active member's rows (its pool among them)
  out of the source store and keeps them only for rollback; the old pool's idle objects stay undisposed and parked
  members' rows stay in the source store. Rollback (`_rollback_creations_move`, 1079-1104) puts the rows back.
- U9, settled by S6 (the story's FACT note of 2026-10-15T18:43:16Z): `_apply_notch` and `_reactivate_owned_spell`
  never re-stamp; a promoted version keeps the owner stamp it had. Until 0.2.8246 a transfer stamped only the active
  member and no rollback restored a stamp, so a parked version kept the source's store (after a notch on the target
  a managed meld raised the missing-pool error and a `unique` stored its object in the source's store) and a failed
  transfer left the active member on the target's store (a managed meld raised missing-pool, or leased from an
  empty pool left in the target; a `unique` built a second object there).
- The stamp follows the lineage both ways (S6). `_stamp_owner(spell, conduit, spellbook)` (1680-1725) stamps as
  conjure does: root id, name and store, dynamic flag, gate controller, the Book's caching posture. `_restamp(spell)`
  (1727-1776) registers the stamp-back to the source first, stamps onto the target and, for a managed version whose
  pool the target store did not hold, registers `_discard_composed_pool` (1778-1802) in a `finally`. The flip calls
  `_restamp` for the active member; `_migrate_inactive_members` (1588-1648) calls it, after its map rollback, for
  every moved parked member whose `_owner_creations` is set. A version never stamped moves as before (since 0.2.8248
  only one whose stamp raised at conjure).
- `Creations.discard_managed_quantity(spell_id, pool)` (creations.py:1200-1249) removes the pool only while it is
  the one under the id (identity check under the store lock), unregisters it after the lock, never cleans it (the
  caller does) and answers whether it removed it; a cleaned store raises its RuntimeError.
- Rollback order (registration reversed): the row rollbacks; each parked member (discard, stamp-back); the map
  rollback (`_rollback_inactive_members`); the active member (discard, stamp-back); `_rollback_spellbook_move`; the
  registry, contracts and validity. Rows go back before the stamps. A composed pool is empty when it is discarded
  (the lineage is disabled for the whole transfer), so nothing is disposed.
- Locks: the stamps run under both conduit locks and outside the Book locks, as the flip's stamp always did
  (conduit -> spell -> store leaf -> registry leaf); rollbacks hold no conduit lock; no new edge.
- After a no-move transfer a parked managed version has a pool in each root (the source keeps its old one with the
  parked rows); once that version is notched in on the target, a release by class finds two pools of the selected
  version and needs `conduit=` (a lease's own `release()` is unaffected).
- Built in S8 (0.2.8248; the owner ruled on 2026-10-16 on the S6 DECISION note's point 6): a version staged with
  `bind_inactive` before conjure was never stamped - conjure stamped `_spells` only and `_apply_notch` stamps nothing
  - so after a notch to it, its first meld raised "Spell has no configured CreationContextFactory." for every
  existence, and a managed consumer's per-creation read raised the missing-pool error. Conjure now stamps every
  parked version with the owner stamp alone, as a post-conjure `bind_inactive` does.
- Transfers are dynamic-only and dynamic plans read the pool per creation (B7), so a plan finds a moved pool through
  the target's store; no plan binds a pool that a transfer can move. A release racing a transfer can meet the gap
  between extract and restore and raises the not-managed ValueError for that call.

### B9 Lifecycle
| event | pools | idle objects | objects out | registry |
| --- | --- | --- | --- | --- |
| conjure, post-conjure bind | one per managed version in the owner root's store | none | none | registered |
| meld or injection | pop, else reserve and build | -1 or none | +1 | - |
| release | optional reset, append, trim above baseline, queue notify | +1 | -1 | - |
| notch, cleanup_spell | untouched (the old version's pool stays) | untouched | untouched | resolver prefers the active version |
| transfer, move (default) | every version's pool moves to the target store | move | the agents' | stays valid; names the target root |
| transfer, no move | active pool kept for rollback only; parked pools stay; the target's are fresh | stay undisposed | the agents' | old out, new in |
| transfer that fails | back where they were; a pool a stamp composed is discarded | untouched | the agents' | as before |
| root teardown | cleaned | disposed with their children | their recorded children disposed; the objects are the agents' | unregistered |
| lesser or spellspace end | never hold pools | - | - | - |
| crystallizer restore | rebuilt empty at conjure | none | none | registered |

### B10 Concurrency rules
- The hit and a resetless release below the baseline take no lock (`deque.pop` / `append` are atomic per object on
  3.14t). The pool lock (the base `_lock`) is a leaf held for `count`, the children map and condition waits only;
  resets, constructors and disposal never run under it.
- A queue wait can happen while the plan holds an enclosing door's root guard (children are built before a slotted
  site takes its own guard); the required timeout bounds it.
- The registry lock is a leaf held only to publish; Creations registers and unregisters outside its store lock.
- Pool disposal runs in `Creations.cleanup` outside the store lock; no new edge joins frame -> conduit -> Book.

### B11 Errors (drafts; final texts in the component patches)
- Limited: "Managed spell '<name>' (limited_quantity, limit <N>) has all <N> objects out. Release one with
  ReleaseManagedSpell.release(obj) before melding another, or bind it with a higher managed_spell_limit."
- Queue: "Managed spell '<name>' (queue, limit <N>) had no object free within <T> s. ..."
- Not managed: "<Type> is not a managed spell class in any live root: bind it with
  existence=Existence.managed_spell_quantity, or its root was torn down."
- Ambiguous: "<Type> is managed by <k> pools: <spell id / binding / frame / root per pool>. Pass spell_id=... or
  conduit=... to pick one."
- Torn down: "The pool of managed spell '<name>' was torn down with its root; the object is yours to dispose."

### B12 Tests and validation
- Environment (device VM): `. ~/.melder_env` (CPython 3.14.7 free-threaded); `export TMPDIR=/tmp/m0_mq/tmp`; run
  every suite twice, `python -X gil=0 -m pytest ...` and `python -X gil=1 -m pytest ...`. A device_bash call lasts
  at most 180 s (pass `timeout_ms=180000`; the default is 120 s) and kills its background jobs when it returns
  (nohup and setsid do not survive), so suites run in shards under 170 s each, logged under the lane's runs/.
  Measured: the spellbook unit tree is about 25 s, the top-level unit tests about 60 s, the asset rebuild about
  75 s. The rebuild unlinks generated payloads, so it needs delete permission on melder_private (granted for
  this session on 2026-10-15; a new session asks again).
- S1: tests/unit/melder/spellbook/test_resolution_style_matrix.py,
  tests/unit/melder/spellbook/spell_crafter/system/validation/test_scope_ordering_strategy.py, a route-family test.
- S2: bind option tests beside the existing bind tests, fingerprint byte-identity for every existing member, record
  round trip (restore and graft).
- S3: tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py (per mode: accounting, refusal, waits,
  timeouts, served-by-release, trims, resets, raising resets, adopt/abandon, cleanup aggregation),
  test_managed_spell_quantity_multithreaded.py (limit never exceeded, no hang), test_creations_managed_quantities.py.
- S4: tests/unit/melder/aether/conduit/creations/test_release_managed_spell.py and test_managed_spell_lease.py.
- S5 (as built): tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py (51:
  emitted shapes and runtime on real pools), tests/unit/melder/spellbook/spell_compiler/test_managed_dispense_seams.py
  and the discovery and specializer additions;
  tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py (23);
  tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py (7: two frames, two binding
  names, a dynamic late bind, a notch, a borrower, a lesser, a crystallizer restore).
- S6 (as built): tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_owner_stamps.py
  (19: the flip's stamp and stamp-back, the discard of a composed pool, parked members of every existence, a raising
  stamp, the rollback order), tests/unit/melder/aether/conduit/creations/test_creations_discard_managed_quantity.py
  (11) and tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py (12: move, releases after
  it, no move, parked versions notched in, failed transfers with and without a move, `unique` stamps).
- S8 (as built): tests/unit/melder/spellbook/test_spellbook_creation_system_parked_versions.py (9: the parked stamp's
  arguments in three postures, under the Book lock, no registration of a parked existing object, the resolution flag
  untouched, a raising stamp logged, a Book with nothing parked),
  tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py (27: six families staged
  before or after conjure, meld after a notch, not meldable by id before it, a staged existing object unregistered,
  a managed version's pool from conjure on), the cache-schema test at generation 21 and the lowering's two message
  assertions; `ManagedSpellLease` checked as built (probes/probe_s8_managed_spell_lease.py, 8 cases per GIL mode,
  and its five test files, 94 tests).
- Density: at least 20 tests per 100 LOC on the pool, the registry and the lowering (concurrency and lifecycle code),
  10 elsewhere; never claim coverage numbers.
- Rebuild, last: `python src/melder/_build_assets/_build_asset_runner.py` then `--check`;
  `python llm_support/_builder.py` then `--check` (`--include-untracked` while new files are untracked).

### B13 Resume after a compaction
1. REONBOARD, then read this epic's Build Specification and the newest Notes, then `attention_board.md`.
2. Open the active story (Stories, below; the board row routes to it) and its Context / Handoff Summary.
3. `GIT_OPTIONAL_LOCKS=0 git --no-optional-locks status --porcelain` and `cat src/melder/__version__.py` - another
  lane may have landed; a notch is taken from `__version__` at landing, never reserved.
4. Continue from the story's NEXT; record every finding in the story before the next tranche; keep this epic's
  Build Specification true (edit it when a story settles an UNKNOWN).

## Requirements (Functional + Non-Functional)
The Build Specification above is the requirement set; these lines index it. The earlier F1-F13 and their rulings
overlay are archived verbatim (Artifact Links).
- F1 Member and classification: B6. F2 Bind options and the record: B1, B5. F3 Pool: B2. F4 Store: B3.
- F5 Release and leases: B4. F6 Dispense, injection, overrides, failed-construction return: B7. F7 Transfer: B8.
- F8 Lifecycle: B9. F9 Ownership: the agent owns every lease; an object never released stays out and holds its place
  until root teardown; Melder returns an object itself only when it was dispensed into a construction that failed.
- N1 Thread safety: B10. N2 Performance: Success Metrics. N3 Documentation: AGENT_PURPOSE on every new public
  surface, system docs, graph, README, release note (S7). N4 Code rules: the synaptic_python_developer profile (no
  PEP 604 unions, no `__future__` annotations, no module-level constants, `__slots__`, cleanup deletes owned fields
  and tears the logger down last, value-only dataclasses, no `type: ignore` or `noqa`).

## Constraints / Assumptions
- Melder never supplies a Conduit to a constructor, and Conduit cannot be bound as a spell: release must not need one.
- The bind guard matches exact (module, qualname) pairs: the new internal classes join its manifest at the rebuild.
- `type(obj)` is the class object, hashed by identity: one dict get with no inspection.
- Free-threaded 3.14: `deque.pop` / `deque.append` are atomic per object; `x += 1` on an attribute is not, so every
  `count` update takes the pool lock.
- Every notch changes `__version__`, and the creation cache admits only its own release (generation 9): a cache
  generation bump costs one cold compile after an upgrade and never breaks a world.

## Dependencies / External References
- Seam ranges: Build Specification B2-B8 (0.2.8240; recheck with an AST span before editing).
- tickets/epics/2026-10-05_melder_services_and_pools_epic.md (the earlier discussion, 2026-10-11 to 2026-10-13)
- artifacts/managed_shell_spike_20261014/ (fable_0's probes; `probe_deque_holder.py` is the settled shape)
- artifacts/melder_object_pools_20261011/ (routing-cost and many-under-holder probes)
- system_docs/patches/completed/managed_spell_quantity_2026_10_15/ (this lane's patch docs, archived at S7)
- Prior art: Autofac pooled instances; .NET ObjectPool (a reset may refuse reuse); Apache Commons Pool; HikariCP

## Milestones (Track Progress)
- [x] Milestone 1: Design settled - the open questions answered and recorded in the Decision Log.
- [x] Milestone 2: Architecture patch doc written and linked; each story's component patch before its build.
- [x] Milestone 3: S1-S6 landed (one notch each) with green tests in both GIL modes.
- [x] Milestone 4: S7 - docs, graph, README, release note, benchmarks; rebuild checks OK.
- [ ] Milestone 5: MelderOps prototype (Iris loggers as a managed spell) measured against the 74-82 us meld - after a
      release, coordinated with the owner.
- [x] Milestone 6: S8 - the owner's 2026-10-16 follow-ups (parked versions wired at conjure, cache generation 21),
      landed as 0.2.8248 after melder_1's 0.2.8247.

## Stories (Required to Complete)
Implementation order; each story lands its own notch (S7 lands documentation only).
- [x] S1 STORY-2026-10-15-managed_existence_member - the member, the matrix, the route family, Phase 6 rank.
      Landed 0.2.8241. tickets/stories/completed/2026-10-15_managed_existence_member_story.md
- [x] S2 STORY-2026-10-15-managed_bind_options - ManagedSpellMode, the four keywords on every bind path, checks,
      Spell fields, fingerprint, crystal record and replay, RecordVersion 4.2.0.
      Landed 0.2.8242. tickets/stories/completed/2026-10-15_managed_bind_options_story.md
- [x] S3 STORY-2026-10-15-managed_quantity_pool - ManagedSpellQuantity, the exhaustion error, Creations integration,
      the store readers.
      Landed 0.2.8243. tickets/stories/completed/2026-10-15_managed_quantity_pool_story.md
- [x] S4 STORY-2026-10-15-release_managed_spell - the registry, release / managed / release_all / describe, the lease,
      package-root exports.
      Landed 0.2.8244. tickets/stories/completed/2026-10-15_release_managed_spell_story.md
- [x] S5 STORY-2026-10-15-managed_dispense_codegen - per-path classification, discovery, manifest, lowering, door,
      overrides, failed-construction return, specializer, `Conduit.managed_spell_meld`.
      Landed 0.2.8245. tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md
- [x] S6 STORY-2026-10-15-managed_ownership_transfer - pools through move, no move, rollback and notch; the owner
      stamp follows the lineage.
      Landed 0.2.8246. tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md
- [ ] S7 STORY-2026-10-15-managed_docs_release - system docs, graph, tests docs, README, release note, benchmarks.
      Work done 2026-10-15, no notch; waits on the owner's acceptance of the epic.
      tickets/stories/2026-10-15_managed_docs_release_story.md
- [ ] S8 STORY-2026-10-16-parked_versions_wired_at_conjure - conjure wires versions parked before it; cache generation
      21 (the owner's follow-ups of 2026-10-16); also checks `ManagedSpellLease` works. Landed 0.2.8248; waits on the
      owner's acceptance of the epic.
      tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-10-14-investigate_managed_shell_design (fable_0) - done 2026-10-14; the settled shape, seam map,
      numbers and plan are in this epic's Notes.
      tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md
- [x] Prerequisite: EPIC-2026-10-14-many_child_follows_holder (0.2.8235) and the slotted lane (0.2.8236-0.2.8240),
      turned in by owner directive on 2026-10-15.
- [x] Task: benchmark lease, release and the existing meld shapes before S5 and after S7 (probes in the spike folder).
      Done: S5's and S7's MEASURE notes (existing shapes within noise; the managed cycle 306-385 ns).
- [x] Task: keep the running release note's managed section current at every landing (one section, extended).
      Done: release_docs/next_version_release.md, the managed section and the packaging lines.

## Acceptance Criteria (Epic Done)
- Every story closed with its evidence, the success metrics measured, and the EXIT_GATE checks recorded.
- The owner accepts the build and the walkthrough.

## Risks / Mitigations
- A holder keeps using an object after releasing it, or releases it twice -> the caller's contract (identity is not
  tracked by ruling); the lease releases once and the `with` form cannot release twice.
- State leaks between holders without a reset -> the reset is an explicit bind choice, documented with the member.
- Leases never released exhaust limited and queue pools -> `describe(cls)` shows count and idle per pool; recycling is
  the agent's (owner, 2026-10-15).
- A queue wait under an enclosing build guard -> the timeout is required; stress tests race waits, releases and
  teardown.
- The pool or registry lock joins an existing chain -> both are leaves; resets, constructors and disposal run outside.
- A non-managed spell id, executor or record moves -> the fingerprint part is managed-only; the emission diff and the
  id byte-identity tests gate S2 and S5.
- A release racing a transfer of its spell meets the gap between extract and restore -> ValueError (not managed) for
  that call; recorded in the S6 component patch.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story notes.
- [ ] No `src/` edit before the story's component patch and mapping note exist.

## Validation / Test Approach
- Build Specification B12; each story's Validation section names its files and commands.

## Rollout / Adoption Plan
- Opt-in: a new Existence member and new keyword options; existing bindings, executors and records are untouched.
  MelderOps adopts after an owner-cut release that contains the member.

## Open Questions
- None open. Settled 2026-10-16 by the owner: conjure wires versions parked before it (S8); the review items
  stand as built, except the cache generation, which S8 bumps to 21; `ManagedSpellLease` stays as built (the package
  root, the `with` form) and S8 checks that it works (Decision Log). Settled earlier: U1-U11 (S2-S6).

## Decision Log
- 2026-10-16 (owner, chat with melder_0, answering the `ManagedSpellLease` question): "no these are all fine, fix
  bind_inactive, 1. is fine leave it as is but just do make sure it works fine" - `ManagedSpellLease` stays as built
  (at the package root, with its `with` form; melder_0's "hide it" pick is dropped) and S8 checks that it works; S8
  builds the conjure wiring now.
- 2026-10-16 (owner, chat with melder_0, after the walkthrough and the probe's answers): (1) "so really
  bind_inactive should behave the same before and after conjure like it should work right?" - conjure wires parked
  versions (S8); (2) activation hooks on every meld from the pool stand ("each iteration on it create the hook calls
  thats fine"); (3) "you can bump the cache because codegen also requires that you properly modify it" - cache
  generation 21 in S8, reversing S5's decision (2); (4) F9 as widened stands ("ok sure"); (5) override objects
  outside the count stand ("if someone wants to break their own spells its their choice, its not my problem to
  police behaviours"); (6) the no-move release ambiguity stands ("right now we're not in a spot where we care about
  this its fine"); (7) pools through a transfer stand; found bugs become tickets ("if you found more bugs just add
  tickets"). Open: the owner read `ManagedSpellLease` as a rename of `ReleaseManagedSpell` ("I believe I told you to
  use ReleaseManagedSpell its cleaner language"); it is the `with` helper - keep, hide from the root, or drop the
  `with` form.
- 2026-10-15 (melder_0, S6 build decisions inside the owner's go-ahead, open to the owner's review): (1) the owner
  stamp follows the lineage both ways - a transfer re-stamps every parked version that carries a stamp, and a failed
  transfer stamps every member back and discards the empty pools its stamps composed - because a stamp that names the
  wrong store is a record naming the wrong owner, for every existence (the probe's cases B, D, E, F and G); (2) rows
  are unchanged: a pool moves as the row S3 and S4 built; (3) `Creations.discard_managed_quantity(spell_id, pool)`
  joins the store verbs (identity-checked, unregisters, never cleans); (4) after a no-move transfer a parked managed
  version keeps its old pool in the source with its other rows, so once it is notched in on the target a release by
  class needs `conduit=`; (5) stamping versions staged before conjure is left to the owner (Open Questions).
- 2026-10-15 (melder_0, S5 build decisions inside the owner's go-ahead, open to the owner's review): (1) the
  `managed` door route reuses the `many` template objects, so `created` is True on every lease and a direct meld runs
  the activation hooks for reused objects too; (2) no cache generation 21 (plans are emitted at hydration and a notch
  makes the cache cold); (3) F9 widened: any failure between a consumer's first lease and its construction, its
  publication included, and a lost cold race give the leases back; (4) a leasing site feeds exactly one consumer
  (per path; the emission refuses another count); (5) `managed_spell_meld` with overrides on the managed spell's own
  parameters returns a lease on that fresh, uncounted object, and its release adds the object to the pool - under the
  trusted-release ruling (2026-10-13) a `limited_quantity` or `queue` pool can then hold more than its limit.
- 2026-10-15 (owner, chat with melder_0): `ReleaseManagedSpell` is a singleton like Aether - "ReleaseManagedSpell
  should be a singleton like Aether follow that same design, its owned and created by Aether it must be made there on
  init"; "it should also be cleaned up by Aether"; "it must also have a reset singleton feature too" (B4 rewritten).
  The `ManagedSpellMode` import stays TYPE_CHECKING-only ("use TYPECHECKING"): S2's runtime
  import and its extra signature test are withdrawn, and the scan_bind parity test reads the signature with
  FORWARDREF, as the typing policy says (src_architecture, Failure Modes).
- 2026-10-15 (melder_0, build decisions inside the owner's go-ahead, open to the owner's review): (1) four bind
  keywords - `managed_spell_mode`, `managed_spell_limit` (elastic: the idle cap; limited_quantity and queue: N),
  `managed_spell_timeout_seconds`, `managed_spell_reset_methods` - carry the settled shape's options, the elastic
  baseline fixed at min(20, limit); (2) pools sit in their own Creations map, are disposed before the disposable
  registry and travel as extract/restore rows, and the registry follows the store; (3) a managed site is per path (one
  lease per injection) and placed like a shared site (its own miss); (4) F9's failed-construction return stays (the
  2026-10-14 overlay left F9 standing); (5) winning override keys on a managed site's own parameters build a fresh
  object that is not pooled, counted or registered; (6) `ManagedSpellMode`, `ReleaseManagedSpell` and
  `ManagedSpellExhaustedError` join the package root beside `Existence`; (7) RecordVersion 4.2.0, a minor bump
  (additive fields); (8) the epic is rewritten as the build spec, its prior text archived verbatim
  (artifacts/managed_spell_quantity_20261015/epic_before_rewrite_20261015.md), where the design-iteration entries
  that later rulings replaced remain.
- 2026-10-15 (owner, chat with melder_0): implement it. The owner: "you can use the way my spellspace pool and
  conduit pool work as elastic and focus on that and understand it, you gotta add transfer of ownership for it
  too thats important and it'll be available for pool objects too you'd follow the same mechanics, you'd need to
  implement all the phases so make a story for each implementation mechanic and investigate everything as you go
  please go ahead and implement this"; `ReleaseManagedSpell` goes in `src/melder/aether/conduit/creations/` as
  its own module; "add more details to the epic take out shit you don't need then implement it please, make the
  epic as detailed as you can because will compact multiple times building this".
- 2026-10-15 (owner, chat with melder_0): object hygiene is the agent's, done with its own tools - "if you have
  tools to work around this stuff and you have codegen what the hell is the problem, you can easily see oh yeah
  look my conduit has extra stuff, and flag it for recycling". Read as: Melder keeps the structure right and
  visible (`ReleaseManagedSpell.describe(cls)`: mode, count, idle per pool); recycling stays with the agent.
- 2026-10-15 (owner, chat with melder_0): purge is not part of this design, and the build is fable_0's
  composition as it stands. The owner: "why are you bringing up purge, when we never talked about purge, thats
  not even needed our new design with fable_0 makes the most sense, ReleaseManagedSpell and how we composed it".
- 2026-10-15 (owner, chat with melder_0): the five follow-up points are not design questions - Melder polices its
  structure, not the objects it hands out. The owner: "overrides can still override the target if this pooled
  object is its resolved graph node for it", "purge can destroy the class if people want", "why are you trying to
  enforce a model that doesn't make sense" and "you've made the same tool 6 times and the newest version is the
  one you like, you then destroy the whole scope, you go ahead and save your blueprint and put it into another
  container". The readings are in the ASSUMPTION_CHALLENGE note of 2026-10-15T01:34:21Z; the settled shape stands.
- 2026-10-14 (final shape, fable_0 for the owner): the Spell keeps the managed options; `ManagedSpellQuantity(deque)`
  of idle objects in the root's Creations under the spell id, an int `count`, no references to out objects;
  `ReleaseManagedSpell` maps the class to `(holder, spell_id)` pairs, registered at conjure, removed at teardown;
  release = optional reset + append; nothing destroyed on notch or cleanup_spell; overrides allowed; the seven-point
  implementation plan and the seam map are in the Notes of this timestamp. The owner hands implementation to the next
  agent ("I'll get opus to do the rest").
- 2026-10-14 (owner, chat with fable_0): the holder is a `deque` of idle objects in the Creations object under the
  spell id - `ManagedSpellQuantity(deque)`, the elastic system built in optionally - composed from the Spell, which
  retains every managed requirement as bind options; no settings object, no composition frame, no identity tracking
  ("we don't care about identity"); release appends. Measured 3-4x cheaper than the spike's shell (elastic cycle
  140 ns through ReleaseManagedSpell, 90 ns through the holder; limited 124 / 82; queue 265 / 239) with the limited
  and queue checks still passing (task MEASURE/DECISION notes of this timestamp).
- 2026-10-14 (owner, chat with fable_0; ruling on the investigation task's four points): the out-record holds strong
  references (F9 as written: an unreleased object holds its place until the scope is torn down; no weak record);
  notch and cleanup_spell destroy nothing - the old version's shell and its objects stay until the scope is destroyed
  or purged; injection into any holder is a lease the holder keeps for its life (no Phase 6 rule); overrides on a
  managed site are allowed - the supplied object is used for that construction and no lease is taken (reverses
  default (g)); `ManagedShell` and `ManagedQuantity` are one class (the bind-time declaration and the per-root live
  shell). The owner's model: "sometimes you don't care about old objects ... you've made the same tool 6 times and the
  newest version is the one you like, you then destroy the whole scope"; objects that are out "maybe are still being
  used".
- 2026-10-14 (chat with fable_0): the simplest path - `ReleaseManagedSpell` is the one way back and hosts a
  `with`; a new `Conduit.managed_spell_meld("target")` is the meld-plus-release form; protocol and mixins
  dropped; the object is "managed in creations as a special interface": a shell in the Creations store, looked
  up by spell id like today, that pulls the object out in the mode's way or puts it back; the root owns it; a
  reset list at bind (`managed_spell_reset_methods=[]`); the three modes `limited_quantity`, `elastic`,
  `queue`; "we need the most minimal change here and the same features and keep it easy". fable_0 opened
  TASK-2026-10-14-investigate_managed_shell_design to investigate it with a VM spike ("see what happens").
- 2026-10-14: pools stay with root scopes - the root that owns the binding - and no narrower pool scope is offered for
  now. The owner: "I think we keep it to root scopes for now and leave it at that, its reasonable".
- 2026-10-14: the reset is optional; a pool without a declared reset returns objects as they are. The owner: "if a
  Spell Requires ReleaseManagedSpell to release it, and an optional reset method then what else do we need".
- 2026-10-14: a `many` dependency belongs to the object it was built for, so Phase 6 does not refuse one under a managed
  spell; the runtime must dispose it with that object. The owner: "if unique depends on a many with disposal it
  doesnt matter because it was built for that unique".
- 2026-10-14: a managed spell's own dependencies follow the lifetime rule of `unique`: it may depend on unique, not on
  narrower lifetimes. The owner: "it cannot depend on specific kinds of lifetimes make it similar to unique but it
  can depend on unique".
- 2026-10-13: no release through Aether ("I'm against using the aether to do it I object on that one"), no separate
  ManagedSpells handle, and no conduit required to release ("we don't want everything to require the conduit").
- 2026-10-13: injection is in: a meld of a holder whose constructor takes a managed spell dispenses a pooled object
  into it ("channel logger is injected during the meld ... the pool object gets dispensed").
- 2026-10-13: release is the common, trusted hand-back and Melder tracks no references ("its very symbolic we don't
  check we just trust"); the with statement is the shortcut.
- 2026-10-13: the user owns every lease: no automatic return when a scope cleans up, no yield, and an object never
  released holds its place until root teardown ("we cannot baby sit the user"). Purge deletes.
- 2026-10-12: leases are explicit - the `managed_spell` with statement and `release_managed_spell`, not purge.
- 2026-10-12: composition: pools live on the root conduit in a new Creations location; a meld creates from the pool;
  the mode is chosen per spell at bind (limited, elastic and a third, `queued` proposed); a reset named at bind runs on
  return; an object not released stays used until root teardown; deep changes are acceptable if other features are
  preserved.
- 2026-10-12: the member is named `managed_spell_quantity`; no SpellSpace-like manager object to meld through.
- 2026-10-12: the kernel pools' elastic retention was fixed first (landed 0.2.8234) and is the retention a managed pool
  reuses.
- Full owner quotes and the earlier history (pooled_spell, 2026-10-11): the Decision Log of EPIC-2026-10-05.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/managed_spell_quantity_20261015/ (this lane: the epic's text before the 2026-10-15 rewrite, verbatim;
    probes, runs, emission diffs, benchmarks and apply scripts)
  - artifacts/managed_shell_spike_20261014/ (fable_0's spike: `probe_deque_holder.py` is the settled shape; the
    captured-plan and door probes, logs)
  - artifacts/melder_object_pools_20261011/ (probes and runs, shared with EPIC-2026-10-05)
  - system_docs/patches/completed/managed_spell_quantity_2026_10_15/ (patch docs, promoted and archived at S7)
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the managed_spell_quantity Existence member, its pools and its release paths
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer) wrote the first revision (2026-10-14T00:28:29Z) and the
  early design notes (archived); fable_0 (synaptic_python_developer) settled the shape with the owner (Notes of
  2026-10-14T23:45:47Z); melder_0 (synaptic_python_developer) rewrote the ticket as the build spec on 2026-10-15 and
  implements it. Design decisions: the owner, in chat, as recorded in the Decision Log.
- Assigned implementer: melder_0 (synaptic_python_developer), by owner directive on 2026-10-15.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: fable_0 reviewed the design as of 2026-10-14T17:19:37Z (archived note 2026-10-14T22:15:12Z);
  the build has no independent reviewer yet.

## Notes
- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: THE SETTLED SHAPE (owner rulings of 2026-10-14 in chat with fable_0; implementation handed to the next
    agent by the owner: "add a ton of detailed notes to the epic, I'll get opus to do the rest").
    (1) `Existence.managed_spell_quantity`, a seventh `auto()` member; class spells only (the callable and
    existing-object families stay unique-only). (2) The
    Spell retains every managed requirement as bind options - the mode (`elastic` | `limited_quantity` | `queue`), the
    limit, the queue timeout, the elastic idle cap, and the optional `managed_spell_reset_methods` list - no settings
    object, no composition frame; they are hashed into the spell id for managed bindings only, so no existing id
    moves, and the crystal records them. (3) The holder is `ManagedSpellQuantity(deque)`: the deque holds the IDLE
    objects of one managed spell in one root; the mode and numbers are composed from the Spell when the root's owner
    store is stamped at conjure, and the holder lives in the root's Creations under the spell id as a new record
    shape beside the slotted object and the `many` list; `count` is an int of objects built and alive (limited and
    queue accounting), not a list - the holder keeps NO reference to any object it handed out ("we don't care about
    identity"); one leaf lock plus a Condition, used only on the cold paths (the limited check, the queue wait and
    notify, the elastic trim's count); the elastic system is built into the subclass optionally (trim the oldest idle
    above `max_idle` on append, defaults 20/256 like the kernel pools; the 0.2.8234 decay band only if idle memory
    ever matters). (4) Dispense is inlined in the emitted plan - `try: v = h.pop()` / `except IndexError:
    v = _miss(...)` - no method call, no lock (`deque.pop`/`append` are atomic per object on 3.14t); the miss:
    limited raises when
    `count >= limit`, queue waits `cond.wait_for(count < limit or idle, timeout)` then raises, elastic always builds;
    `count += 1`, then the site's children, then the object; a failed build takes `count` back and disposes the
    children it built. (5) `ReleaseManagedSpell`: a dict keyed by the managed class (`type(obj)` is the class object,
    identity-hashed, one dict get) whose value is the pair `(holder, spell_id)` - the holder for the release itself,
    the spell id as the key into the root's Creations for every cold path; root conduits register their pairs at
    conjure (and a post-conjure bind, and the transfer flip) and unregister at teardown; `release(obj)` runs the reset
    names registered at bind, if any, then `append` - "that's how you clean it up and return it and that's it";
    `release(obj, target)` with the meld-style target when the same class has two pairs (two binding names in one
    frame, or the same id in two frames under per-frame ids); the bare call raises an ambiguity then. Helpers on the
    class are welcome: `managed(obj)` (a small `__enter__`/`__exit__` class, never a generator), `release_all(...)`,
    `describe(cls)`. (6) `Conduit.managed_spell_meld("target")`: meld plus the lease class whose `__exit__` releases
    through the dispensing holder. (7) Nothing is destroyed on notch or cleanup_spell: the old version's holder and
    its objects stay until the scope is destroyed or purged (0.2.8219's "product left alive in its slot" applies);
    `purge(instance)` disposes that object and takes `count` down; `purge_all` disposes the idle objects; root teardown
    disposes the idle objects and drops the registry pair (out objects are the user's - no references are kept, so
    they are not Melder's to destroy; F8's "and out objects" clause is withdrawn). (8) Overrides on a managed site are
    allowed: the key-set plan skips the site, the supplied object is used, no lease is taken (reverses default (g)).
    Injection into any holder is a lease that holder keeps for its life; no Phase 6 rule (managed ranks with
    `unique`: it depends only on `unique`, anyone may depend on it). A managed object's disposal-bearing `many`
    children: a side map id(object) -> children, written only at build and only when there are any, read only when
    that object is destroyed (trim, purge) - never on the warm path. (9) A reset that raises: the object is not
    appended; it is disposed, `count` goes down, the error propagates (owner default (b)). (10) Cache generation 21
    retires executors emitted before managed sites; RecordVersion moves for the recorded options.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md:356-460
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:28-104
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_deque_holder_run1.txt:1-7
  IMPACT: Requirements F3, F5, F6, F7, F8 and F9 of this epic read with these rulings (next note); the measured
    warm cycle is three to five warm `unique` reads.
  NEXT: the implementation plan (PLAN note below) and the seam map (FACT note below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: WHICH REQUIREMENT LINES THE RULINGS SUPERSEDE (read F1-F13 and the open questions with this). F2: the
    options live on the Spell (plain bind keywords), the ManagedQuantity working names are dropped; the class merge
    the owner asked for is "no second object at all". F3: the pool is the `deque` holder in the root's Creations
    under the spell id, not a new ConduitCreations location; it holds idle objects and `count`, no record of out
    objects. F5: the release core checks nothing - no "out from this pool" test, no double or foreign refusal; the
    reset is optional and its return value is ignored; a raising reset destroys the object and raises. F6: one way
    back, `ReleaseManagedSpell` (mixin and protocol member dropped), plus the `with`. F7: the index maps the class to
    `(holder, spell_id)` pairs; registered at conjure, removed at teardown. F8: root teardown destroys IDLE objects
    only (no references to out objects exist); purge of one object destroys it; the elastic trim destroys idle
    objects; disposal runs only on destroy. F9 stands as written. F11: overrides allowed (Q6 answered: allow). F12:
    inspection is `describe(cls)` - mode, count, idle; no outstanding-object listing (no references). Open questions:
    Q1 reset optional, return ignored, raise destroys; Q2 a release after its root was torn down raises plainly (the
    pair is gone); Q3 purge with no instance destroys the idle objects, out objects come back as usual; Q4 queue
    stays, timeout required; Q5 managed depends only on unique, anyone may depend on it, `many` children follow the
    object; Q6 allowed; Q7 names: `ManagedSpellQuantity`, `ReleaseManagedSpell`, `managed_spell_reset_methods`,
    `Conduit.managed_spell_meld`; no `conduit.release_managed_spell`; Q8 root scopes; Q9 elastic 20/256 at bind,
    limited and queue keep what they built; Q10 no held-too-long warning; Q11 one way to declare the reset (bind).
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:99-128
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-258
  - tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md:356-460
  IMPACT: Nothing in F1-F13 needs rewriting by hand; this note is the overlay the implementer applies.
  NEXT: the seam map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: THE SEAM MAP, read on the 0.2.8238 working copy (every range opened, not searched). (a) The enum:
    `existence.py:60-117`, six `auto()` members, `__str__` returns the bare name; the seventh is additive.
    (b) The resolution matrix: `resolution_style_matrix.py:108-165` - `EXPECTED_EXISTENCE_COUNT = 6`,
    `ALL_EXISTENCE_NAMES`, `NON_UNIQUE_EXISTENCE_NAMES` and the family policy (class_based supports all; callable
    and existing-object families are unique-only and list the non-unique names as unsupported) - add the member to
    all three tuples and the count; `validate()` refuses an unclassified name. (c) The route family:
    `spell_artifact_processor.py:118-146` maps Existence to `route_family` and raises on an unknown member - add
    `"managed"`; the manifests whitelist it: `strategies/many_only/manifest/many_only_manifest.py:196-214` and
    `strategies/generalized/manifest/generalized_manifest.py:72-90`. (d) The door templates:
    `shared_assets/creation_runtime_door_compiler.py:498-865`, one `(route, lane)` template per existence; the
    `unique` templates at 602-629 (no overrides) and 796-821 (hooks) are the model: the managed template reads the
    holder from `_owner_creations._creations.get(_spell_id)`, inlines `try: creation = holder.pop() / except
    IndexError:` and calls the plan's miss; the warm lane of `Conduit.meld` (`conduit.py:4878-4938`) calls the
    emitted door and never reads a store, so it does not change. (e) The lowering: `site_plan_lowering.py:1331-1470`
    - `_emit_context` places shared sites and `many` steps, `_owner_store_constant` (S9) binds an automatic unique
    site's store as `c{i}`, `_emit_shared_hit` emits the read/miss pair, `_emit_miss` emits the children-first miss;
    a managed site is a third shape: bind the holder as `h{i}` under the S9 condition (automatic owner, stamped
    store), emit the inline pop, and a miss that reserves (`count`) before the children. (f) The store:
    `creations.py` - record shapes and locks 10-120; `_dispose_disposable_registry` 470-560 and `_dispose_entry`
    576; `purge` 1082 and `_detach_purge_entries` 1188; `extract_spell_creations` 1302-1376 and
    `restore_spell_creations` 1377-1470 - each dispatches by isinstance on the three shapes today; the holder is
    the fourth and gets an explicit branch in all five. (g) Ownership stamping: `Spell._add_owned_conduit`
    (`spell.py:1558-1606`) is called at conjure (`spellbook_creation_system.py:1350-1375`), at a post-conjure
    `bind_inactive` (`spellbook.py:5255-5290`) and `bind` (5590-5620), and at the transfer flip
    (`transfer_of_ownership.py:1470-1505`), after which `_move_creations` (1506-1545) extracts and restores the
    spell's records per lineage member - compose the holder and register the pair here; the holder is the same object
    after a move. (h) The doors outside the store: `conduit_meld.py:843-1086` and `spellspace_meld.py:783-1027`
    (live-creation probes, purge resolution, existing lookups) need the holder branch. (i) Phase 6:
    `scope_ordering_strategy.py:80-121`, the `scope_rank` dict; managed = 0 with unique. (j) Bind:
    `Spellbook.bind` 5400-5450 (keywords) and 5540-5545 (non-hook kwargs flow into `spell.metadata`, which the
    fingerprint does NOT hash); `Bind._bind_logic` 571-640 and the `disposal_method_names` flow 464-570 are the
    model for the reset names; `Bind.sha256_profile` 911-1010 hashes spellframe, names, existence, disposal names
    and resolvable - add the managed options there with a default that leaves every non-managed hash byte-identical
    (the `resolvable` precedent). (k) Cache: `caching_system.py:190-212`, generation 20 is current; add 21.
    (l) Records: `record_version.py:84` CURRENT 4.1.0; the spell crystal must carry the options.
    (m) Notch and disposal leave products alone: `_apply_notch` (`spellbook.py:3824-3965`) parks the outgoing
    version and tears down its creation context only; `_dispose_spell` (4325-4420) cleans the Spell.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/existence.py:60-117
  - src/melder/aether/spellbook/resolution_style_matrix.py:108-165
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:118-146
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:196-214
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:72-90
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-865
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1470
  - src/melder/aether/conduit/conduit.py:4878-4938
  - src/melder/aether/conduit/creations/creations.py:10-120
  - src/melder/aether/conduit/creations/creations.py:470-620
  - src/melder/aether/conduit/creations/creations.py:1082-1206
  - src/melder/aether/conduit/creations/creations.py:1302-1470
  - src/melder/aether/spellbook/spell.py:1558-1606
  - src/melder/aether/spellbook/spellbook_creation_system.py:1350-1375
  - src/melder/aether/spellbook/spellbook.py:5255-5290
  - src/melder/aether/spellbook/spellbook.py:5590-5620
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1470-1545
  - src/melder/aether/conduit/meld/conduit_meld.py:843-1086
  - src/melder/aether/conduit/meld/spellspace_meld.py:783-1027
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - src/melder/aether/spellbook/spellbook.py:5400-5450
  - src/melder/aether/spellbook/bind/bind.py:464-640
  - src/melder/aether/spellbook/bind/bind.py:880-1010
  - src/melder/utilities/caching_system/caching_system.py:190-212
  - src/melder/crystallizer/persistence/record_version.py:84-85
  - src/melder/aether/spellbook/spellbook.py:3824-3965
  IMPACT: Every edit point is named with its model; the only UNKNOWN left is which crystal fields carry the options
    (`spell_crystal.py` and the restore engine's bind replay were not opened for this).
  NEXT: the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: THE NUMBERS (VM, CPython 3.14.7t, `-X gil=0`, caching off; the probes and logs are in the artifacts
    folder). Reference: a warm `unique` site read 30 ns; `Manager()` construction 70 ns; a whole
    `conduit.meld("Worker")` 337 ns; a fresh Iris logger meld on MelderOps 74-82 us (parent epic). The owner's deque
    holder, acquire + release per cycle, one idle object: elastic 140 ns through `ReleaseManagedSpell` / 90 ns
    through the known holder (with a declared `reset()` 215 / 149); limited_quantity(4) 124 / 82; queue(4, 1.0 s)
    265 / 239. The spike's earlier `ManagedShell` (entries, weakrefs, a locked warm path) cost 505 / 407, 484 / 389
    and 567 / 461 for the same modes, and inside a real emitted plan 715 ns per Worker creation against 166 ns
    plain; a lock-free variant of it saved only 115-145 ns per cycle and lost the teardown invariants - both are
    reference only now. Stress: limited(3) never exceeds 3 under 8 threads; queue(1, 0.25 s) waits then raises at
    its timeout; a waiter is served by a release (the same object, no build). The `contextlib.contextmanager` form
    of the `with` costs about 600 ns more than a plain class - emit a class. Rerun: `python -X gil=0
    <artifacts>/probe_deque_holder.py` (standalone), `probe_plan_shape.py` and `probe_plan_capture.py` (need
    `tests/experimentation` and the repo on the path, cwd anywhere; they build a world through the certification
    harness and capture the emitted plan).
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_deque_holder_run1.txt:1-7
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_door_modes_run2.txt:1-4
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_shape_run1.txt:1-11
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_modes_run2.txt:1-19
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_cost_variants_run1.txt:1-8
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_capture_worker_source.txt:1-23
  IMPACT: Success metric 1 (about 5 us to acquire, about 1 us to return) is met by 30x; metric 2 (routing about
    100 ns) by the singleton's +50 ns; the benchmark task of this epic can reuse the probes.
  NEXT: the plan.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: IMPLEMENTATION ORDER AND TESTS (one lane, one writer per file; each `src/` change notches 0.0001 and adds
    its release-note entry; assets rebuilt last). 1. Enum, matrix, route family and manifest whitelists (seams a-c);
    unit: `ResolutionStyleMatrix.validate()` green with seven members, the processor maps the member. 2. Bind
    options on the Spell, the fingerprint (managed only), the crystal fields and RecordVersion; unit: a non-managed
    binding's id is byte-identical before and after, a managed binding's id changes with its mode/limit/timeout/
    reset names, record and restore round-trip the options. 3. `ManagedSpellQuantity(deque)` and the Creations
    composition at `_add_owned_conduit`, the five readers' branch, purge semantics (one object; idle on purge_all),
    teardown disposes idle; unit per mode: count accounting, limited raise, queue wait/timeout/served-by-release,
    elastic trim at max_idle, reset order and the raising reset; stress: limited never exceeds N under threads.
    4. `ReleaseManagedSpell` (register at the three stamping points and the transfer, unregister at teardown; the
    pair; the ambiguity rule and the target form), the lease class, `Conduit.managed_spell_meld`; unit: routing,
    ambiguity, release after teardown raises plainly; component: `with` releases on exit. 5. The door templates and
    the lowering site shape (the inline pop, the reserve-first miss, children before the object, failure path);
    component: a direct meld dispenses and reuses, injection into a `many` holder and into a `unique` holder, an
    override skips the site, a `many` child with disposal dies with its managed object on trim/purge, a transfer
    moves the holder and releases keep working, a notch leaves the old holder in place; integration: two roots in
    one frame with the same class under two binding names (ambiguity, target), per-frame ids with one id in two
    frames, crystallizer record/restore of a managed world. 6. Phase 6 rank entry; unit: managed may depend on
    unique only, any holder may depend on managed. 7. Cache generation 21; unit: an old-generation bundle is cold.
    8. Docs: src_architecture (boundary list, the meld sequence, operational invariants, failure modes, code map),
    src_components (Creations, Meld doors, Bind, the lowering, Phase 6), tests docs, graph descriptors, the README's
    Existence section, the running release note; `AGENT_PURPOSE` on every new public surface. Benchmarks: the
    probes above as the before/after; no regression on the existing meld paths (the harness's five shapes).
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:160-200
  - context_compass/special_instructions/agent_contribution_guide.md:1-97
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:28-104
  IMPACT: The stories of this epic can be cut along steps 1-2, 3-4, 5, 6-7 and 8.
  NEXT: the owner assigns the implementer; TASK-2026-10-14-investigate_managed_shell_design closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:16:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner reassigned this epic to melder_0 (chat 2026-10-15: "go ahead and take on the new epic for creating
    the new existence type fable should have done a good job explaining it go read all that please"), the next
    agent fable_0's handoff names. melder_1 keeps EPIC-2026-10-14-slotted_lifetime_ownership_fixes, whose rebuild
    and acceptance are still open on files this epic also changes (creations.py, site_plan_lowering.py,
    transfer_of_ownership.py, conduit.py): this lane writes no `src/` file until that lane has rebuilt and released
    them. The seam check, the patch docs and the stories touch no shared file. The codex_bridge listing failed
    ("Codex app tool request failed") and melder_1 and fable_0 are Claude sessions the bridge does not reach, so
    this ticket and its board row are the coordination record.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:547-552
  - context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:393-450
  - context_compass/artifact_board.md:105-105
  - context_compass/mailbox_board.md:96-98
  IMPACT: One writer for this ticket and its board row; no `src/` overlap with melder_1's open lane.
  NEXT: The owner rules on the DECISION_REQUEST below; meanwhile check the seam map against the 0.2.8240 tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:18:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: fable_0's seam map (read at 0.2.8238) still locates every seam on the 0.2.8240 tree. Definition spans from
    the syntax tree: site_plan_lowering.py `_emit_context` 1331-1361, `_emit_many` 1363-1393,
    `_owner_store_constant` 1396-1419, `_emit_shared_hit` 1421-1443, `_emit_miss` 1445-1513; creations.py record
    shapes 10-111, purge 1082-1186, extract/restore 1302-1474; spell.py `_add_owned_conduit` 1558-1607; Phase 6
    `scope_rank` 80-87; bind.py `_bind_logic` 571-820 and `sha256_profile` 911-1022; the cache generation history
    190-211; RecordVersion CURRENT 84. One drift: 0.2.8239 moved transfer_of_ownership.py's flip to 1383-1510 and
    `_move_creations` to 1512-1555 (cited 1470-1505 and 1506-1545). These are locations, not behaviour: each body
    is read whole before its patch doc. src/, release_docs/, llm_support/ and system_docs/ are clean against HEAD
    7fc8dd48e (committed 2026-10-15T00:14:03Z) at 0.2.8240; whether melder_1's rebuild ran before it is UNKNOWN.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1513
  - src/melder/aether/conduit/creations/creations.py:10-111
  - src/melder/aether/conduit/creations/creations.py:1082-1474
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1555
  - src/melder/__version__.py:12-12
  IMPACT: The seam map needs no rework before the patch docs; the two transfer citations take their new ranges.
  NEXT: On the owner's answers, read each seam body whole and write the patch docs, architecture first.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T01:34:21Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: The owner rejected the DECISION_REQUEST of 2026-10-15T00:16:35Z (chat 2026-10-15): points 2-5 policed
    objects Melder hands out, which the runtime model rules out - agents iterate, keep the newest version and destroy
    the whole scope. Read under it, nothing is left open. (1) Two different classes are two types, so each routes to
    its own pool. One class object bound twice is one key with two spell ids (the fingerprint hashes the class shape
    plus the bind options, and bind refuses only an equal id), and the active version's pool takes its releases (a
    notch re-points it): same class, same code. (2) A release after its root ended is the agent's business. (3) Root
    teardown disposes everything the root recorded, the pooled objects' recorded `many` children included. (4) An
    override replaces the pooled node when the pooled object is the resolved node, no lease; one aimed at the pooled
    object's own inputs builds that object fresh for that construction, no lease (melder_0's reading of "overrides
    allowed"). (5) Purge disposes what it targets; a purged idle object leaves the queue. From the fingerprint:
    method bodies are not hashed, so a body-only rewrite keeps its spell id and, rebound after cleanup_spell, meets
    the old pool, as a slotted replacement meets its old slot today (0.2.8219).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:522-547
  - src/melder/aether/spellbook/bind/bind.py:961-1022
  - src/melder/aether/spellbook/spellbook.py:5226-5241
  - src/melder/aether/spellbook/spellbook.py:5270-5285
  IMPACT: Milestone 1 is met: the settled shape of 2026-10-14T23:45:47Z stands with these readings.
  NEXT: On the owner's go-ahead, read each seam body whole and write the patch docs, architecture first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T01:37:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Scope narrowed by the owner (chat 2026-10-15): purge is not part of this design ("we never talked about
    purge, thats not even needed"), and the build is fable_0's composition as recorded: the Existence member, the
    bind options on the Spell, `ManagedSpellQuantity(deque)` in the root's Creations, the inline pop and the
    reserve-first miss, `ReleaseManagedSpell` keyed by class to `(holder, spell_id)` with the optional reset then
    `append`, `Conduit.managed_spell_meld`, and scope teardown disposing what the root holds. Withdrawn: the
    settled shape's `purge(instance)` / `purge_all` lines and point (5) of the 2026-10-15T01:34:21Z note. The store's
    purge reader only has to leave a managed record untouched; the patch docs state how.
  EVIDENCE: context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:558-611
  IMPACT: No managed purge verb is built; the rest of the settled shape is unchanged.
  NEXT: On the owner's go-ahead, write the patch docs from the settled shape, architecture first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T08:51:04Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The owner authorized implementation (Decision Log, 2026-10-15 "implement it"). Tranche order: (1) read the
    kernel elastic pools whole (AbstractElasticPool, SpellSpacePool, ConduitPool) - the elastic mode reuses their
    retention mechanics; (2) read the transfer path's creation moves whole (TransferOfOwnership, Creations
    extract/restore) - a transfer carries a managed pool and its idle objects the same way; (3) archive the
    superseded epic text verbatim under artifacts/managed_spell_quantity_20261015/ and rewrite the epic as the full
    build spec; (4) one story per implementation mechanic; (5) patch docs, then each story red tests -> src -> green ->
    notch -> release note, rebuild last. `ReleaseManagedSpell` lives in src/melder/aether/conduit/creations/.
  EVIDENCE: context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1-60
  IMPACT: The lane moves from design to build; every finding lands here before the next tranche.
  NEXT: Read abstract_elastic_pool.py, spell_space_pool.py and conduit_pool.py whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T08:52:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The kernel elastic pools, read whole on 0.2.8240. `AbstractElasticPool` keeps idle objects in `_idle`
    (a deque set once at init; `cleanup()` destroys them and clears it, never replaces it); a hit is
    `_idle.pop()` (newest, warmest); a miss builds and calls `_note_miss()`, which only stamps the pressure clock
    (settle 1800 s, lock-free). A return appends and stops when at most `baseline_idle` are idle (no clock, no
    lock); above that `_rebalance_after_return()` reads the clock and, under `_lock` (a leaf RLock held for counter
    and deque work only), stretches `target_idle` to the observed idle count while a miss is recent (capped at
    `max_idle`), else decays it 10% per 600 s toward the baseline, detaches the surplus oldest first and destroys
    it outside the lock through `destroy_object` (a raising destroy re-pools the rest). `max_idle == baseline_idle`
    is a fixed-capacity pool: a return above the baseline evicts the oldest, no clock, no lock. Objects out are
    not reclaimed by `cleanup()`. ConduitPool and SpellSpacePool are the model subclasses: their own fast paths
    pop or `_note_miss()` and let the caller build (ConduitPool returns None on a miss), release appends and
    rebalances above the baseline; Conduit builds both at baseline 20 / max 256.
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:123-264
  - src/melder/utilities/general_base/abstract_elastic_pool.py:328-378
  - src/melder/utilities/general_base/abstract_elastic_pool.py:449-599
  - src/melder/aether/conduit/conduit_pool.py:108-165
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:188-307
  IMPACT: `ManagedSpellQuantity` subclasses `AbstractElasticPool` (owner: elastic works like these pools): elastic
    is baseline 20 / max 256 with the same stretch and decay; limited_quantity and queue are fixed-capacity at N
    (nothing to trim; the count gate refuses or waits). The plan's warm path pops the holder's `_idle` deque, and
    `destroy_object` runs the Spell's disposal methods plus the object's recorded `many` children.
  NEXT: Read Creations (record shapes, cleanup, extract/restore) and the transfer creation moves whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T08:55:25Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Creations and the transfer path, read whole on 0.2.8240. `Creations` keeps `_creations` (the live object or
    `many` list per spell id, the only map resolution reads), `_disposable_creations` (cleanup-only: an
    `(object, methods)` tuple, a `ManyDisposalBucket` or a `HolderDisposalEntry`), `_slot_guards` and a leaf
    `_lock`. `cleanup()` detaches both maps under the lock, disposes the disposable registry newest-first (a
    dependency registers before its dependent, so insertion order is creation order), then deletes its fields and
    keeps `_lock` as a tombstone. `extract_spell_creations` / `restore_spell_creations` move one spell id's rows
    (`scope` unique or many, `stored`, `disposal_methods`, `children`); restore replaces what the id held. Transfer
    `execute()`: under both conduit locks `_flip_registry_and_spellbooks` stamps the ACTIVE member on the target
    (`_add_owned_conduit` with the target's store) and `_migrate_inactive_members` moves parked members without
    re-stamping them; then `_move_creations` extracts and restores every member id (its rollback re-extracts the
    target and restores the source) or, with `move_creations=False`, `_teardown_creations` extracts the active
    member's rows and keeps them only for rollback. Lineage spells skip both.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:118-296
  - src/melder/aether/conduit/creations/creations.py:306-363
  - src/melder/aether/conduit/creations/creations.py:489-542
  - src/melder/aether/conduit/creations/creations.py:1302-1474
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:367-507
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1079-1104
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1470-1590
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1592-1636
  IMPACT: Design decisions for the build: (1) pools get their own map in Creations, `_managed_quantities[spell_id]`,
    so no reader of `_creations` (lookups, live probes, purge) can mistake a pool for an object; (2) Creations
    disposes its pools before the disposable registry, because a pool is created at conjure, before the uniques its
    objects hold, and reverse insertion order would close those uniques first; (3) extract/restore carry a
    `managed` row holding the same pool object, so a transfer moves the pool with its idle objects, and the
    ReleaseManagedSpell registry follows the store (a store registers a pool it takes, unregisters one it gives
    up); (4) the Spell keeps a borrowed reference to its pool, so dispensing does not depend on `_owner_creations`,
    which the flip re-stamps for the active member only. UNKNOWN: whether a notch re-stamps a parked member's owner
    store after a transfer (check `_apply_notch` in the transfer story).
  NEXT: Archive the epic verbatim, rewrite it as the build spec and open one story per mechanic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T09:25:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The epic is rewritten as the build spec at the owner's request ("add more details to the epic take out shit
    oyu don't need then implement it please, make the epic as detailed as you can because will compact multiple times
    building this"). The full prior text is archived verbatim: 1036 lines, sha256
    e4eae89827ea1f67fed7d18228278eea0f57db3d412e1a58e0d03c3050493a75, equal to the live file when copied.
    Taken out of the live ticket: requirements F1-F13 and their overlay (now Build
    Specification B1-B11), the eleven answered open questions, the STORY-TBD list, the design-iteration Decision Log
    entries later rulings replaced, melder_1's design notes of 2026-10-14 (00:28:29Z to 17:19:37Z), fable_0's review
    and spike notes of 22:15:12Z and 23:07:01Z, and melder_0's rejected DECISION_REQUEST of 2026-10-15T00:16:35Z.
    Line citations into this epic made before this note resolve against the archive (same text, same line numbers).
  EVIDENCE: context_compass/artifacts/managed_spell_quantity_20261015/epic_before_rewrite_20261015.md:1-1036
  IMPACT: One live spec to build from after every compaction; the history stays retrievable.
  NEXT: Write the architecture patch doc and open the seven stories.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T09:25:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The codegen seams, read whole on 0.2.8240. (1) SitePlanEmission places every kept step at the plan's top
    level or inside one shared site's `_miss{i}`; "shared" is every existence but `many` (`_shared`). A shared site
    emits its store read (or the S9 bound store) and a miss that builds the children placed inside it, takes the
    slot guard (unique: the Spell lock), rechecks, constructs, publishes and adopts its disposal-bearing children; a
    `many` step constructs and registers its disposal in the store of the context it lives in. (2) Per-path instance
    keys come from `_is_shared_existence` in the occurrence instance processor and the occurrence graph analyzer, both
    `existence is not Existence.many`. (3) The family is chosen by phase 10 discovery: solo for exactly one visible
    spell without a collection socket, many_only for two or more visible spells that are all `many`, generalized
    otherwise; the generalized family runs the site plan. (4) Doors are one template per (route, lane), compiled at
    import from `_build_no_overrides_lines` / `_build_with_overrides_lines`; the `many` door only calls the plan (or
    `_execute_with_overrides`); the route key comes from `_build_model_shell`, which raises for an unknown member.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:731-1666
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:112-118
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:733-737
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py:52-81
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py:52-95
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:1-1229
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:107-182
  IMPACT: Build Specification B6/B7: a managed site is a third site kind (placed like a shared site, keyed per path,
    dispensed instead of read), the solo family declines managed models, and the managed door has the `many` shape.
  NEXT: The architecture patch doc, then the stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T10:11:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S1 landed as 0.2.8241: the member (appended last; values 1-6 unchanged), the matrix (count 7, class spells
    only), route family "managed", Phase 6 rank 0. Tests red then green in both GIL modes; the spellbook unit tree,
    the top-level unit tests and the existence and scope-ordering integration suites pass. Two operating facts for
    every later story: a device_bash call kills its background jobs when it returns (run suites in shards under 170
    s), and the asset rebuild unlinks payloads, so it needs the delete permission the owner granted this session.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_existence_member_story.md:1-260
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s1_rebuild_assets_check.txt:1-4
  IMPACT: S2 can bind the member; B12 records the shard rule and the rebuild permission.
  NEXT: S2 - read the bind chain and the crystal sites whole.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T12:31:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S2 landed as 0.2.8242: `ManagedSpellMode`, the four bind options on every bind path with their refusals,
    the Spell fields, the managed-only fingerprint part, the crystal capture and the five replays, RecordVersion
    4.2.0. Green in both GIL modes on the new files and on the unit, component and integration trees (the
    crystallizer integration tree in shards). Validation caught a hidden public-surface regression of the first cut -
    the TYPE_CHECKING-only enum import made `inspect.signature` raise NameError on Spellbook.bind and four other
    bind methods - fixed with a runtime import and pinned by a guard test (B5).
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_bind_options_story.md:1-385
  - release_docs/next_version_release.md:308-366
  IMPACT: S3 composes the pool from the Spell's fields; the record already carries them for restore.
  NEXT: S3 - read the pool base, Creations and the Meld store readers whole; the component patch; red tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T12:37:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner stopped the lane ("stop and explain") over S2's runtime import of ManagedSpellMode. That import
    and the new test file tests/unit/melder/spellbook/test_bind_verbs_value_format_signatures.py contradict the
    documented typing policy: src_architecture's Failure Modes accepts a VALUE-format NameError on TYPE_CHECKING-only
    names as "not a defect to patch per call site". The policy-consistent fix of the parity-test failure is to read
    `scan_bind` with FORWARDREF in that test, as the same test already reads Spellbook.bind. Options put to the
    owner: revert (TYPE_CHECKING import back in the five modules, delete the new test file, FORWARDREF in the parity
    test, drop the release-note sentence, fold into 0.2.8242 and rebuild again) - recommended; keep the import and
    drop the test; keep both. Nothing is committed; the 0.2.8242 rebuild checks printed OK before the stop.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1981-1985
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:294-312
  - context_compass/tickets/stories/completed/2026-10-15_managed_bind_options_story.md:277-303
  IMPACT: S3 waits for the owner's answer; no file changes until then.
  NEXT: Apply the owner's choice, then start S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T12:41:10Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner answered the DECISION_REQUEST of 2026-10-15T12:37:16Z: use TYPE_CHECKING for `ManagedSpellMode`
    (revert the runtime import, delete the extra signature test, FORWARDREF in the parity test, inside 0.2.8242,
    rebuild again), and `ReleaseManagedSpell` becomes a singleton like Aether, created and owned by Aether at init
    (B1 and B4 rewritten; U11 opened for S4).
  EVIDENCE: context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:186-210
  IMPACT: The lane is unblocked; S4's registry is instance state on an Aether-owned singleton.
  NEXT: Apply the revert, validate, rebuild; then S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T14:05:52Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S3 landed as 0.2.8243: `ManagedSpellQuantity(AbstractElasticPool)` (sizes per mode, reserve, put_back with
    resets outside every lock, abandon / adopt / destroy_object with id-keyed children records, a cleanup that drains
    under the lock and disposes outside it), `ManagedSpellExhaustedError`, the Creations pool map (ensure and get,
    pools cleaned before the disposable registry, the `managed` extract/restore row, purge 0), owner stamping in
    `Spell._add_owned_conduit`, the probes' "managed_pool" answer and the static rooms. Green in both GIL modes on the
    new tests and on the unit, component and integration trees; the crystallizer integration tree ran a smoke shard
    only (S3 changes no crystallizer code). U3-U6 and U10 are settled in B2 and B3 with the as-built behaviour.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_quantity_pool_story.md:1-348
  - release_docs/next_version_release.md:365-387
  IMPACT: S4 registers pools at the four points where a store takes or gives one up (ensure, extract, restore,
    cleanup) and reads a pool's Spell only through `spell`; S5's miss relies on `reserve` serving an idle object
    before it refuses, and must not assume a pool exists for an unstamped version.
  NEXT: Rebuild and check for 0.2.8243, then S4 (U11 first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T15:39:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S4 landed as 0.2.8244: `ReleaseManagedSpell`, a hosted-root singleton Aether builds last and cleans after
    the frames, keyed by class with copy-on-write maps and a lock-free release (one dict get, then `put_back`); the
    cold resolver (spell id, holding root, the selected version, precise ValueErrors); `managed`, `release_all`,
    `describe`; `ManagedSpellLease`; the Creations register/unregister calls; four package-root exports. Green in
    both GIL modes on the new tests and on the whole tree (unit, component, integration including all 279
    crystallizer integration ids, the experimentation trees). Routing: a bound release +50 ns over `put_back`; the
    `ReleaseManagedSpell()` call +70 ns, as `Aether()`. U11 is settled in B4; B1 lists the lease.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_release_managed_spell_story.md:1-349
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_validation_index.md:1-54
  - release_docs/next_version_release.md:308-420
  IMPACT: S5's `Conduit.managed_spell_meld` returns the lease and its emitted plans lease from the pools the registry
    routes back to; S6's moves keep the holding root right through extract and restore.
  NEXT: Rebuild and check for 0.2.8244, then S5 - read the codegen seams of B7 whole (U7, U8), the component patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T18:15:07Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S5 landed as 0.2.8245: meld and injection lease from the pools through the emitted plans - leasing and fresh
    managed sites, the inline pop (a plan constant on automatic roots, a per-creation read elsewhere), the
    reserve-first miss with children recorded with the object, the widened F9 return, the door rows on the many
    templates, the seams (per-path predicates, solo decline, manifest key, specializer decline) and
    `Conduit.managed_spell_meld`. Green in both GIL modes on the 51 lowering tests, the seam, discovery and
    specializer tests, 23 component and 7 integration tests and the whole tree; every non-managed emitted plan
    byte-identical (4461 entries); a warm cycle (meld plus release) 320 ns automatic, 742 ns dynamic. U7 and U8 are
    settled in B7; the pre-conjure staging gap is in B8.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md:1-572
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_validation_index.md:1-51
  - release_docs/next_version_release.md:308-458
  IMPACT: S6 moves pools the plans now lease from; transfers are dynamic-only and dynamic plans read the pool per
    creation, so a moved pool is found through the target's store.
  NEXT: Rebuild and check for 0.2.8245, then S6 - read TransferOfOwnership's creation moves and `_apply_notch` (U9).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T21:00:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S6 landed as 0.2.8246: the owner stamp follows an ownership transfer's lineage both ways. The flip and
    `_migrate_inactive_members` stamp through `_restamp` (the stamp-back registered first, a composed pool's discard
    in a `finally`); `Creations.discard_managed_quantity` takes back an empty pool a stamp composed; rows are
    unchanged (S3, S4). U9 is settled: a notch never re-stamps, so the stamp has to follow the transfer - for every
    existence, `unique` included. Red then green in both GIL modes (42 tests: 19 stamp, 11 discard, 12 integration),
    the probe's B, D, E, F and G fixed and A, C unchanged, the whole tree green in both modes. Stamping versions
    staged before conjure stays with the owner (Open Questions).
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md:1-346
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_validation_index.md:1-81
  - release_docs/next_version_release.md:299-310
  - release_docs/next_version_release.md:469-482
  IMPACT: Every mechanic of the build has landed (S1-S6, Milestone 3); S7 documents it, promotes the patches and
    records the benchmarks.
  NEXT: Rebuild and check for 0.2.8246, then S7 - read its story and the patch lane, then the system docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T23:43:36Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The build is ready for the owner's acceptance. S1-S6 landed as 0.2.8241-0.2.8246, one notch each, red then
    green in both GIL modes, rebuilt and checked at each landing; S7 documented the member without a notch: the
    existing meld shapes and scope cycles stay within noise against 0.2.8240 (ratios 0.960-1.033, both modes) and a
    managed warm cycle costs 306-385 ns; src_architecture, src_components and the two tests docs carry the lane and
    score B (83, 83, 83, 77); the graph authors the five new modules and re-accepts the 22 nodes the lane moved; the
    README, the docs site (curriculum, scopes guide, glossary, API selection) and the release note describe it; the
    patch lane is archived. EXIT_GATE: tests green per story, every non-managed emitted plan byte-identical (4461
    shapes, S5), benchmarks recorded, docs and graph current, rebuild checks next (S7, last); the owner's acceptance
    is the one item left. For the owner: (1) DECISION_REQUEST - should conjure stamp versions staged with
    `bind_inactive` before it, so such a version can be notched in? Today its first meld fails for every existence
    (Open Questions); (2) the build decisions open to review (Decision Log, S4-S6): the lease exported at the root, the
    `managed` door rows on the `many` templates (`created` is True and activation hooks run on every lease), no cache
    generation 21, F9 widened to any failure before a consumer's construction ends, `managed_spell_meld` with
    own-parameter overrides pooling an uncounted object (a limited or queue pool can then exceed its limit), a release
    by class after a no-move transfer needing `conduit=`, a restore cleaning the pool it replaced; (3) found in S7 and
    fixed: the README's disposal sentence (stale since 0.2.80), docs/api.toml missing S4's four root exports (the site
    build refused them since 0.2.8244), two stale src_architecture claims; (4) found, not changed: the
    architecture_and_design set (stamped as verified against 0.1.2) still lists six members; the graph backlog from
    before the lane (144 stale, 9 unsemantic, 5 retired; 8 of the stale in this lane's classes); the extractor's census
    treats an empty stamp as unverified and writes indent=1 while the walker's accept writes indent=2;
    `generalized_cache_runtime_rows_SCRATCH.py`, a 35-byte marker tracked in src since 6d0568f2e, ships in the wheel;
    the build-asset payload modules' graph descriptors lag the final rebuild by one pass (mechanical tier only);
    melder_1's meld_contract_scan waits on the owner to hand over four `register_index` call sites in this lane's files
    (spellbook.py twice, transfer_of_ownership.py twice) and five test doubles - S7 touched none of them; codex_bridge
    has failed on every try, so tickets and the board are the coordination record.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:152-176
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:383-420
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:421-472
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:497-546
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:554-558
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:560-576
  - release_docs/next_version_release.md:321-486
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_cache_runtime_rows_SCRATCH.py:1-1
  IMPACT: Nothing in the build is open on the implementer's side once the rebuild checks pass; the epic and S7 close
    on the owner's acceptance, and the parked-stamp question is the owner's to rule on (it changes every existence).
  NEXT: The owner accepts S1-S7 and the build decisions, rules on stamping parked versions, or redirects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T00:21:04Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The owner asked what the open questions mean (chat, 2026-10-16); a probe on 0.2.8246 (dynamic world for
    the notch, gil=0) shows each one. (1) A version bound with `bind_inactive` before conjure is never stamped -
    conjure stamps the active versions only (`define_conduit_into_spells` walks `_spells`) and a notch stamps
    nothing - so after a notch its first meld raises RuntimeError "Spell has no configured CreationContextFactory."
    for unique, unique_per_conduit, many and managed alike; the same version bound after conjure melds in all four,
    and so does the pre-conjure one when conjure also stamps parked versions (a probe-only patch: one loop over
    `_inactive_spells`). New: `bind_inactive`'s own comment says pre-conjure parked spells "are wired at conjure
    like pre-conjure active spells", which conjure does not do, so the gap contradicts the code's stated intent.
    (2) An activation hook on a managed spell runs on every lease: one object leased twice, built once, the hook
    called twice (the `managed` door rows are the `many` templates, which report every object as created).
    (4) A consumer whose own constructor raises after its managed dependency was leased gives the lease back
    (count 1, idle 1); a sibling dependency that raises before the lease leaves nothing leased. (5) limited_quantity
    with limit 2: `managed_spell_meld` with an override on the managed class's own parameter builds an uncounted
    third object while two are out; releasing it trims a counted one (`count` 2 -> 1 with 2 alive), repeated cycles
    drive `count` to 0, and then 4 objects were out at once - up to twice the limit.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_owner_questions.py:1-249
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/owner_questions_gil0.txt:1-30
  - src/melder/aether/spellbook/spellbook_creation_system.py:1332-1382
  - src/melder/aether/spellbook/spellbook.py:5292-5306
  - src/melder/aether/spellbook/spell.py:1661-1717
  - src/melder/aether/spellbook/spell.py:1044-1086
  - src/melder/aether/conduit/meld/conduit_meld.py:714-717
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:1175-1238
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:548-606
  - src/melder/aether/conduit/conduit.py:5067-5179
  IMPACT: Question 1 reads as a defect against the code's own comment, fixed by one loop at conjure; question 5's
    drift breaks the limit a limited or queue pool promises and the `count` that `describe()` reports, so the owner
    may want it fixed rather than accepted. Questions 2 and 4 behave as the build decisions describe.
  NEXT: The owner rules on the stamping fix and the review items, or accepts the build as it stands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T00:21:04Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: melder_1's three questions (relayed by the owner in chat, 2026-10-16; its task
    TASK-2026-10-15-make_meld_state_checks_follow_spell_state) are answered yes. (1) melder_1 makes its own edits
    in this lane's files for its landing - the `resolvable=` keyword on the four `register_index` calls (spellbook.py
    bind and notch, transfer_of_ownership.py transfer and rollback) and the five test doubles - so its fix is one
    change set with one notch; melder_0 leaves those files untouched until melder_1 reports its landing. (2) melder_1
    adds its own `##` section to the running release note, takes the next notch (read `__version__` at landing) and
    runs the rebuild last; nothing in this lane needs another rebuild. (3) src_architecture, src_components, the tests
    docs, their indexes and the graph are free now: S7's edits are finished. Any change the owner approves for this
    lane (the parked-version stamp, the review items) lands after melder_1's and notches above it.
  EVIDENCE:
  - context_compass/attention_board.md:198-198
  - context_compass/artifact_board.md:100-100
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:588-603
  IMPACT: melder_1's fix lands without a custody conflict, and the two lanes notch in order.
  NEXT: The owner relays this answer to melder_1 (its chat, or the mailbox as M0-175 if the owner asks melder_0 to).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T00:53:23Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner ruled on every open item (chat, 2026-10-16; Decision Log). Conjure must wire versions parked before
    it, and the cache generation moves to 21 - both in S8 (STORY-2026-10-16-parked_versions_wired_at_conjure, blocked
    until melder_1 reports its landing). Activation hooks on every meld from the pool, F9 as widened, override objects
    outside the count, the no-move release ambiguity and the pools' handling through a transfer stand as built. The
    found bugs became four backlog tasks: the scratch marker in `src/`, the architecture_and_design lifetimes, the
    graph's stale prose, the graph tools' census and indent. Still open: the owner read `ManagedSpellLease` as a rename
    of `ReleaseManagedSpell`; it is the `with` helper, and the owner picks keep, hide it from the package root
    (melder_0's pick) or drop the `with` form.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md:1-190
  - context_compass/tickets/tasks/backlog/2026-10-16_remove_scratch_marker_from_src_task.md:1-147
  - context_compass/tickets/tasks/backlog/2026-10-16_refresh_architecture_and_design_lifetimes_task.md:1-145
  - context_compass/tickets/tasks/backlog/2026-10-16_verify_graph_semantics_backlog_task.md:1-140
  - context_compass/tickets/tasks/backlog/2026-10-16_align_graph_tool_stamp_census_and_indent_task.md:1-146
  IMPACT: The epic's remaining work is S8 and the owner's acceptance; S7 closes with the epic.
  NEXT: On melder_1's landing report, start S8 with its first task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T09:30:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner closed the last open item (chat, 2026-10-16: "no these are all fine, fix bind_inactive, 1. is fine
    leave it as is but just do make sure it works fine"): `ManagedSpellLease` stays as built - at the package root,
    with its `with` form - and S8 checks that it works. S8's entry gate holds: melder_1 landed meld_contract_scan as
    0.2.8247 (the four `register_index` calls in this lane's files, five test doubles, its release-note section, the
    notch, the system docs and a rebuild with both checks OK) and handed those files back, so S8 notches above it
    (0.2.8248 unless another lane lands first). The epic moves blocked -> in_progress until S8 lands.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:1039-1057
  - context_compass/tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md:51-61
  IMPACT: Nothing is open for the owner but accepting the epic after S8; no change to the lease is planned.
  NEXT: S8's first task - read the post-conjure `bind_inactive` branch, `_apply_notch`, `define_conduit_into_spells`
    and the restore engine's staged replay whole; settle U12.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T11:45:48Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The build is ready for the owner's acceptance again: S8 is done and notched 0.2.8248. Conjure stamps every
    version parked with `bind_inactive` before it with the owner stamp alone, so such a version melds after a notch
    for every existence (the owner's "bind_inactive should behave the same before and after conjure"); cache
    generation 21 retires bundles written before the managed codegen; the missing-pool message drops the pre-conjure
    cause; `ManagedSpellLease` works as built (the owner kept it). Red then green, the whole tree green in both GIL
    modes, the system docs, graph and release note carry it - the note's example was run in both modes and its first
    draft corrected: a fresh world refuses `bind_inactive` before its first `conjure(dynamic=True)`, so staging before
    conjure happens in a Book joining a world already settled dynamic - and the patch lane is archived. Found in S8
    and parked as a draft: no public call returns a staged version's Spell for `notch_spell`, so the README's
    stage-notch-meld sketch cannot run as written; the owner picks its shape. Custody: once the 0.2.8248 rebuild
    passes, this lane's files are free for melder_1's rule-2 landing. For the owner: accept S1-S8 (with the review
    items as ruled on 2026-10-16) or redirect.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md:158-464
  - context_compass/tickets/tasks/backlog/2026-10-16_public_notch_target_for_staged_versions_task.md:1-189
  - release_docs/next_version_release.md:533-579
  - src/melder/__version__.py:12-12
  IMPACT: Nothing is open on the implementer's side once the rebuild checks pass; S7, S8 and the epic close on the
    owner's acceptance.
  NEXT: Rebuild and check for 0.2.8248, then report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (2026-10-16T00:03:22Z, the owner report)
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
- Scope: build `Existence.managed_spell_quantity` end to end (Build Specification B1-B12) in eight stories, one notch
  per landed story, rebuild last; S8 carried the owner's follow-ups of 2026-10-16.
- Controlling decisions: the Decision Log (owner rulings 2026-10-12 to 2026-10-16; melder_0's build decisions of
  2026-10-15 - the S4 story's DECISION note: the lease on the root, the holding root; the S5 and S6 build decisions -
  which the owner kept on 2026-10-16, except the cache generation, which S8 moved to 21). The objects handed out are
  the agents'; Melder keeps the structure right.
- Source revision: 0.2.8248 (S8). S1 0.2.8241 (the member, the matrix, route family "managed", Phase 6 rank 0); S2
  0.2.8242 (the four bind options, Spell fields, the managed-only id part, record 4.2.0 and replay); S3 0.2.8243 (the
  pool, the exhaustion error, the Creations pool map, owner stamping, the probes, purge 0); S4 0.2.8244
  (`ReleaseManagedSpell`, the lease, the Creations register/unregister calls, the root exports); S5 0.2.8245 (leases
  through the emitted plans and doors, `Conduit.managed_spell_meld`); S6 0.2.8246 (the owner stamp follows a
  transfer's lineage both ways); melder_1's 0.2.8247 between them; S8 0.2.8248 (conjure wires the versions staged
  before it; cache generation 21).
- Done: Milestones 1-4 and 6; S1-S6 landed and closed (tickets/stories/completed/); S7's work (no notch) and S8's
  (0.2.8248), both in review; U1-U12 settled (B2-B8; U12 in the S8 story).
- Remaining: the owner's acceptance of the epic, which closes S7, S8 and the epic (the 0.2.8248 rebuild ran last and
  both checks print only OK); Milestone 5 (the MelderOps prototype) after a release, with the owner.
- Found and parked: five backlog tasks - the scratch marker in `src/`, the architecture_and_design lifetimes, the
  graph's stale prose, the graph tools' census and indent (2026-10-16T00:53:23Z), and a public notch target for
  staged versions (S8, a draft waiting on the owner's choice of shape).
- Limits: codex_bridge cannot reach Codex desktop (every try; last at 2026-10-16T11:33Z), so the tickets and the board
  row are the coordination record; hosted CI runs and coverage are the owner's (Not run).
- Owners: melder_0 builds; the owner accepts. melder_1's rule-2 task waits on the owner's approval of D1-D5; this
  lane's files (spellbook.py among them) are free for it: the 0.2.8248 rebuild passed.
- Next 1-3 actions: the owner accepts or redirects; on acceptance close S7, S8 and the epic (completion summaries,
  completed/, board anchors, artifact dispositions).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
