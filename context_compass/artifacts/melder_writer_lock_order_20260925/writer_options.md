# Writer lock-order options: store RLock vs unique Spell._lock

Date: 2026-09-25. Author: melder_0. Task: tickets/tasks/2026-09-25_verify_native_writer_lock_order_task.md.
Status: strategy discussion for owner decision. No production source changed. Reproduction: Not run.

## 1. Objective

Remove the store-lock / Spell-lock inversion from every creation, registration and purge path, without
weakening get-or-create-once for shared lifetimes and without adding cost to warm reuse.

## 2. Constraints

- Shared lifetimes construct at most once per store entry (current contract; duplicate construction is
  a semantic change, not a fix).
- Warm reuse keeps its unlocked first lookup; no new lock on the hit path.
- User constructors and disposal never run under a store lock (already true for disposal).
- Creations stays the only live-object/disposal registry; Meld keeps scope selection and authority.
- Must hold on free-threaded 3.14t and GIL builds.

## 3. Known facts (source, 2026-09-25; ticket notes carry full ranges)

- Unique creation (root door and dependency step) and unique purge both take Spell._lock, then the
  store lock. That order is consistent with itself.
- The outlier: per-conduit, lineage and cluster ROOT doors hold the store RLock across the whole inner
  executor, with and without overrides. Their unique dependency steps then request Spell._lock. That
  is store -> Spell, the reverse order.
- On a normal root R the per-conduit store, the lineage store (also for R's lessers), every owned unique
  Spell's owner store, and the cluster store when R leads are ONE ConduitCreations object.
- Disposal-bearing `many` steps register through add_many_creations, which takes the caller store lock.
  A unique root door holds Spell._lock while that happens. Validation permits unique -> many.

Cycles (lock order from source; none reproduced in this lane):

| # | Thread A (holds -> waits) | Thread B (holds -> waits) | Needs purge? |
| --- | --- | --- | --- |
| 1 | per-conduit root on R: R.store -> U._lock | purge(U): U._lock -> R.store | yes |
| 2 | lineage root on R or a lesser of R: R.store -> U._lock | purge(U) | yes |
| 3 | cluster root, leader R: R.store -> U._lock | purge(U) | yes |
| 4 | per-conduit/lineage root on R: R.store -> U._lock | first meld(U): U._lock -> R.store (U's own check/register) | NO |
| 4b | same as 4 | meld(U) whose plan registers a disposal-bearing many into R.store under U._lock | NO |

Row 4 REPRODUCED 2026-09-25 (meld_only_lock_probe.py, CPython 3.14.7, instrumented refusal): two
ordinary first-time melds deadlock, no purge and no disposal method needed. Row 4b is source-derived.
That rules out any purge-only fix.

## 4. Unknowns (must be audited before implementation)

- Lock use in TransferOfOwnership, upgrade_to_normal rebinding, pool return/prewarm, SpellSpace pool,
  conduit cleanup cascade, cluster election quiesce, extract/restore. Any of them may hold a store lock
  while taking a Spell lock.
- Spell._lock is multipurpose (ownership wiring, meld-time structural phases). Whether structural
  phases under Spell._lock can reach a store lock is not established.
- Whether one SpellSpace may be used from several threads (decides if Space stores join the matrix).
- Whether validation admits unique -> many -> unique_per_conduit (ScopeOrderingStrategy checks direct
  edges only). If admitted, a unique root's plan takes R.store in a per-conduit step: another row-4 path.
- Nested melds from inside user constructors while creation locks are held (existing hazard; the
  current code does not define it either).

## 5. Options

A. Reorder purge to store -> Spell. REJECTED: unique creation keeps Spell -> store, so purge would then
   invert against unique creation, and row 4 remains.

B. Drop the store lock around shared-root construction and accept racing construction (loser discarded).
   REJECTED as a fix: changes once-only construction; user constructors with side effects run twice.

C. Per-entry creation locks; store locks become leaves. (Recommended first step.)
   - Every shared entry (store, spell_id) gets a stable RLock. Unique keeps Spell._lock as its entry
     lock (or gains a dedicated one if the audit shows Spell._lock is unsafe to share).
   - Root doors and per-conduit/lineage/cluster/space steps hold the ENTRY lock across construction and
     take the store lock only to observe and to publish. The store lock is never held while acquiring any
     other lock.
   - Purge takes the target's entry lock, then the store lock only to detach. Disposal stays outside.
   - Entry locks live for the store's lifetime (never deleted on purge), bounding memory to spells per
     store and removing the retire-while-waiters problem.
   - Deadlock-freedom argument: non-leaf locks are entry locks, held root -> one provider at a time,
     always consumer before provider. The dependency graph is acyclic (validated), so no two threads can
     request entry locks in opposite orders. Store locks are leaves. Proof obligation: the section-4 audit.
   - Cost: warm hit path unchanged; cold path adds one entry-lock lookup (precreated at conjure where
     the store exists, lazily under the store lock for pooled lessers and spaces).

D. The joint alpha claim protocol (nonblocking try-acquire, release-all-before-wait, retry selection).
   - Needed when a compact prelude holds claims for SEVERAL shared sites at once: sibling claims then have
     no DAG order, so either a global total order (sort by stable key) or try/release is required.
   - Carries open items the proposal names itself: claim-record lifetime, fairness/starvation, reentrancy,
     per-call allocation on the claim path.
   - Builds on C's lock split; it does not replace it.

E. Give `unique` its own store per owning root (raised by the owner, 2026-09-25).
   - Root cause stated plainly: `unique` and `unique_per_conduit` are different lifetimes, yet a normal
     root keeps both in ONE ConduitCreations (Spell._owner_creations IS conduit._creations), so they
     share one store lock. That shared lock is the meeting point of rows 1-3.
   - Move `unique` entries to a second store owned by the same root; Spell._owner_creations points at
     it; purge authority unchanged. Unique doors, dependency steps and purge already address
     `_owner_creations`, so the emitted code keeps its shape.
   - Closes rows 1-3: the per-conduit/lineage/cluster root holds its own store lock, while the unique
     step and purge use Spell._lock plus the unique store. No shared lock, so no cycle.
   - Closes row 4 as well: the unique's own check/register moves to the unique store.
   - Does NOT close row 4b: a unique build still holds Spell._lock while a disposal-bearing `many`
     registers into the caller's store. Separately, a frame-wide unique holding a `many` whose disposal
     belongs to one caller conduit looks like a lifetime mismatch in its own right (UNKNOWN; check).
   - Audit before choosing: existing-object registration, ownership transfer, upgrade_to_normal,
     crystallizer replay, cleanup cascade order (per-conduit entries before unique entries).

## 6. Tradeoffs

| | C: entry locks | D: claim protocol |
| --- | --- | --- |
| Fixes rows 1-4 | yes, given the audit | yes, given the audit |
| Independent of the compact-graph work | yes | no (prelude-shaped) |
| New concepts | one lock family | claims, retries, coordinator, retirement |
| Fairness | standard lock semantics | unqualified (starvation possible under contention) |
| Warm path | unchanged | unchanged if hits skip claims (proposal intent) |
| Future compact prelude | reuses C's entry locks; add a total order for siblings | native fit |

## 7. Recommendation

Ship C as the correctness fix, ahead of and independent from the override optimization, then let the
compact prelude acquire C's entry locks in a global total order (or adopt D's try/release if measurements
show contention). This is the proposal's implementation step 2, cut down to what correctness needs and
decoupled from steps 3-7.

Before any code: run the section-4 audit, write system_docs/patches/active/<patch_id>/ architecture and
component patches (Creations, runtime door compiler, generalized compilers both lanes), and lock the four
cycle rows as deterministic regression tests (wrapped locks with timeouts, as native_lock_probe.py does),
run on CPython 3.14 and 3.14t.

Update after option E and the row-4 probe: E closes every REPRODUCED cycle (rows 1, 2 and 4). It leaves
row 4b, which is source-derived. Probe 4b in isolation before choosing: if 4b reproduces, E needs a
companion rule for `many` registration under a unique build, or C is the fix.

## 8. Decision needed from the owner

1. Treat the inversion as its own correctness fix (option C) before the optimization, or fold it into
   the joint alpha implementation?
2. Unique entry lock: keep Spell._lock, or introduce a dedicated creation lock (decided after the audit)?

## 9. Revised design under owner constraints (2026-09-25, supersedes sections 5-8 where they differ)

Owner constraints:
- Do NOT restrict composition. Any graph users can express today stays legal, including
  unique -> many -> unique_per_conduit. No validator tightening as a fix.
- SpellSpaces may be shared between threads. No thread-confinement shortcut for spaces.
- Implicit and kept: shared lifetimes construct at most once per entry; warm hits stay unlocked.

Root cause restated (owner question "why lock a dict?"): single dict/list operations are already atomic
in CPython (GIL and free-threaded). The Creations RLock does three compound jobs: (1) build-once for
shared lifetimes, held across the whole build including user code and other locks; (2) keeping
_creations/_disposable_creations paired; (3) atomic detach for cleanup/purge. Only job 1 deadlocks.

### Idea A (recommended): per-entry build guards; store locks become leaves

1. Every shared entry (store, spell_id) gets its own build guard (RLock), kept in a small table on the
   store, created lazily with setdefault under the leaf lock, never deleted before store cleanup (bounded
   by spells per store; no retire-while-waiters problem). Applies to unique, lineage, cluster,
   unique_per_conduit and unique_per_spell_space alike. `many` gets no guard.
2. A door or plan step: unlocked get (warm hit, unchanged) -> acquire the entry guard -> recheck ->
   build (dependencies are built by later steps under THEIR guards) -> publish under the leaf lock ->
   release the guard.
3. The store lock ("leaf") only wraps dict reads/writes: publish, many disposal append, detach. It is
   never held while acquiring anything else and never around user code.
4. Purge: entry guard -> leaf lock detach -> release both -> dispose. Waits for an in-flight build of
   the same entry, exactly as unique purge waits on Spell._lock today.
5. unique's guard moves off the multipurpose Spell._lock (validation, context rebuild, mutation) to the
   owner store's entry table, so all shared lifetimes use one mechanism.

Why it cannot deadlock WITHOUT restricting composition: a thread only waits for a guard while holding
guards of entries that transitively DEPEND on the awaited one (consumer before provider). A wait cycle
between threads would therefore require a dependency cycle, which is already invalid (and is infinite
recursion even single-threaded). Existence ranks play no part, so unique -> many -> per_conduit, shared
SpellSpaces, lessers and nested melds from constructors are all covered. Store locks never nest.

Required details:
- Publish after cleanup: an in-flight build may finish after its store was detached. Publish must
  recheck the cleaned flag under the leaf lock and dispose/raise instead of writing into a dead store
  (today the store lock held across the build prevents this; the guard design must restate it).
- Reentrancy: RLock keeps same-thread nested melds working as today.
- Cold-path cost: one table lookup plus one guard per shared construction; warm path unchanged.
- Maps directly onto the 7 DEADLOCK_CASES: each flips because no thread holds a store lock while waiting.

### Idea A - exact mechanics (owner asked "what exactly are we guarding?")

The guarded thing is a SLOT: one (store, spell_id) pair whose lifetime promises at most one object.
The guard protects one transition, "slot empty -> exactly one constructor call -> every requester gets
that object". It does not protect the dict. `many` has no slot (a new object per meld), so nothing to guard.

| Existence | Slot = spell_id in this store | Who contends for the slot |
| --- | --- | --- |
| unique | owning root's store | every conduit/space that reaches the spell |
| unique_per_conduit_lineage | lineage root's store | root and all lessers of that lineage |
| unique_per_conduit_cluster | elected leader's store | all cluster members |
| unique_per_conduit | the calling conduit's store | threads using that conduit |
| unique_per_spell_space | the space's store | threads sharing that space |
| many | none | nobody (disposal append only) |

Door or plan step for a slotted existence:

    creation = store._creations.get(spell_id)          # warm hit, unchanged, no lock
    if creation is not None: return creation
    with store.slot_guard(spell_id):                    # only requesters of THIS slot wait
        creation = store._creations.get(spell_id)      # recheck
        if creation is not None: return creation
        instance = build()                              # dependency steps take THEIR slot guards
        store.publish(spell_id, instance, disposal)     # leaf: store lock, check cleaned, write both dicts
    return instance

`many` step: build; if disposal-bearing, store.append_many(spell_id, instance, disposal) under the leaf lock.
slot_guard: get from a per-store dict of RLocks; on miss create via setdefault under the leaf lock; kept
until store cleanup. Purge: slot guard -> leaf detach -> release -> dispose. Store cleanup: leaf lock,
mark cleaned, detach dicts; a build that publishes afterwards sees `cleaned` and disposes/raises.
Behaviour change to note: DIFFERENT slots in one store can now build in parallel (today the whole store
serializes); same-slot requesters still wait and still get one object.

### Idea B (stopgap only): one creation lock per root tree (or per frame)
Serialize all shared-lifetime construction behind a single reentrant lock. Trivially deadlock-free
(one lock) and small to ship. Cost: cold construction across the whole tree serializes, including slow
user constructors; bad for the free-threaded target. Useful only as an emergency patch before Idea A.

### Idea C (complementary, not a fix alone): separate root-based storage from scope storage
Give a root distinct stores for root-based lifetimes (unique, lineage, cluster-as-leader) and for its own
scope (per-conduit, many disposal). Cleaner ownership and matches the owner's root/scope split, but with
store locks still held across builds, unique -> many -> per_conduit and disposal registration still
deadlock. Worth doing only together with Idea A, if at all.

### Rejected
- Tightening the validator (owner rejected: restricts composition).
- Optimistic build-then-publish with loser discarded (breaks build-once; user side effects run twice).
- Reordering purge alone (does not touch the meld-only rows).
- The joint-alpha try/release claim protocol as the first step: only needed if a compact prelude must
  hold claims for several sibling sites at once; Idea A's guards are what it would claim.

### Audit before implementing Idea A (UNKNOWN today)
Meld's own RLock scope; Spell._lock users that could run while a store lock is held; transfer of
ownership; upgrade_to_normal rebinding; pool return and prewarm; cluster election quiesce; extract/
restore; shared-SpellSpace pool paths (reset_for_pool_unlocked assumes confinement); where a unique
built through a SpellSpace registers its disposal many.

### New regression case to add
unique -> many -> unique_per_conduit (composition the owner keeps legal): a per-conduit root holding the
store vs a first unique build whose plan reaches a per-conduit step on the same conduit. Predicted to
deadlock today; must pass under Idea A.
