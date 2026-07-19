# Task: Safe Fast Meld Signature Door (Spec)

## Metadata
- Task ID: TASK-2026-06-12-safe-fast-meld-signature-door
- Status: spec_review
- Owner: user
- Created: 2026-06-12
- Depends on:
  - `2026-06-09_return_to_meld_hotpath_frontdoor_task.md` (unsafe experiment + measurements)
  - Landed Tier 1/2 meld-door optimizations (CounterSwitch `fast_state` mirror,
    inlined pool-get, direct executor dispatch, `SafeLogger.is_attached` gate)

## Purpose
Productionize the `meld_experiment` branch idea: after one full normal meld has
"understood" a request signature, memoize that understanding as a guarded
zero-arg closure in a plain per-door dict, so later identical requests skip
front-door decision work entirely. Slow first request, fast forever, zero
staleness window.

Measured context (experiment branch, harness):
- unsafe closure floor: ~334-365 ns warm
- normal warm pre-Tier-1: ~507-584 ns
- target for the safe lane: ~390-420 ns warm (guards cost ~50-70 ns)
- cold path is below the executor boundary and is out of scope here

## Scope
In scope:
- `ConduitMeld` and `SpellSpaceMeld` no-hooks, no-override, non-dynamic lane.
- One plain dict per door instance: `spell_id -> guarded closure`.
- One door-local monotonic change counter (CounterSwitch-style append-only,
  with int mirror for readers).

Out of scope (structurally excluded, not deferred):
- Dynamic-mode conduits (gates, links, mutation overrides, ownership transfer,
  `upgrade_to_normal` all live there).
- Hook-enabled spells and doors with meld hooks (fall through to normal lane).
- Caller-supplied `spell_override` payloads (normal lane).
- Spell-compiler / emitted-executor changes (separate lane, separate owner).

## Design

### Key strategy
- String spell-id input: the id string IS the dict key. No key construction.
- Object/name/frame input: reuse the existing `_input_resolution_cache`
  (signature tuple -> spell_id), then hit the door dict by spell_id.
  Two dict reads; no `hex(id(obj))` anywhere load-bearing (id-reuse hazard
  from the experiment is removed).
- Success-only insertion: an entry exists only after one full normal meld
  resolved and executed for that signature. Failed resolutions raise and never
  insert. This bounds dict cardinality by the spellbook registry by
  construction (bound spells x alias forms). No cap, no eviction.

### Build (first request per signature)
Run the normal full meld path. After success, hydrate one closure capturing:
- `executor = creation_context._no_overrides_executor` (live object, per-call
  identity guarded; never refreshed in place)
- `creations` (chosen once by bind-time-immutable existence:
  spellspace-local vs owner-conduit vs caller-conduit store)
- `captured_context = creation_context`
- `captured_door_count = door_change_counter.fast_state`
- borrowed refs: `spell`, `spellbook` (both alive in registries regardless;
  no added lifetime)

Build preconditions (checked once, not per call):
- door `_dynamic_environment` is False
- `requires_spellspace_request` rejected on the conduit door (bind-time
  immutable, so build-time check suffices)

### Guard ladder (per hit, all plain loads)
```
closure = door_dict.get(spell_id)            # miss -> normal lane + rebuild
1. spell._creation_context_switch.fast_state >= 2
2. spell._creation_context is captured_context
3. not spellbook._spellbook_validation_required
4. not spell.resolution_required
5. not spell._hooks_enabled
6. door_change_counter.fast_state == captured_door_count
-> return executor(creations)[0]
any guard False -> normal full meld, then replace the entry in place
```
Guards 1-5 are live slot reads maintained by existing chokepoints; no new
bookkeeping is required for them. Guard 6 is the only new signal.

### Invalidation matrix (what flips each guard)
| Change event | Chokepoint | Guard tripped |
|---|---|---|
| Context replaced (phase-5 rebuild x4, stamp_ownership, spell cleanup, transfer) | `Spell._cleanup_creation_context()` | 1 and 2 |
| Risk/validation state change | `RiskManager._refresh_spellbook_flag` -> `_set_spellbook_validation_required` | 3 |
| Deferred resolution required again | `resolution_required` writers | 4 |
| Spell hooks attached/detached | `_hooks_enabled` recompute | 5 |
| Door meld hooks installed (`set_meld_hooks`) | door change counter bump + eager `dict.clear()` | 6 |
| Door cleanup | `Meld.cleanup()` -> `del` dict and counter | n/a (gone) |

Mutation overrides: `apply_mutation_override` requires a dynamic runtime
environment and raises otherwise. Non-dynamic doors therefore can never see a
non-None `_mutation_override` on owned spells, and non-dynamic conduits cannot
link, so contracted dynamic spells cannot appear either. Excluded by posture;
tested (see matrix), not guarded.

### Change counter
SUPERSEDED AT IMPLEMENTATION (2026-06-12): the door-local change counter was
dropped. Rationale: the meld-hooks map is stored by reference and can be
mutated in place without any `set_meld_hooks` call, so the hooks guard must be
a live `not self._meld_hooks` read regardless - and that live read also covers
map replacement, which was the only event the counter guarded. Every remaining
door-level mutation path (`upgrade_to_normal` creations rewiring,
`create_new_preset_spellbook`) is dynamic-mode-only and therefore outside the
lane's build posture. Net: zero new signals, zero bump-site discipline, one
fewer invariant to maintain. The original counter design below is retained for
the record:
- writer: `deque.append(None)` + int mirror write (same pattern as the landed
  `fast_state` mirror)
- reader: one int slot load
- never reset; closures are self-describing via the captured count, so there
  is no "safe again" flip-back race that a resettable bool would have.
- every bump site also calls `door_dict.clear()` so door-level invalidation is
  eager and owner-driven, not discovered lazily.

Implementation note: entries are stored as plain
`(spell, captured_context, creations_store)` tuples with the guard ladder
inlined in each door's `meld()` (no closure call frame), and the guard
evaluation plus the executor-slot read are wrapped in a narrowly-scoped
`except AttributeError` so a cleaned spell/switch/context reads as a guard
miss and falls through to the normal lane's canonical error behavior. The
executor call itself is outside that try block so user-code AttributeErrors
propagate unchanged and can never cause double construction.

REVISED AT FIRST MEASUREMENT (2026-06-12): the original entry shape captured
`creation_context._no_overrides_executor` at build time. A compiler-lane
change (generalized hydrator) landed concurrently and made the executor slots
SELF-REPLACING: contexts start with cold delegating doors and hot-swap the
hydrated executors into the context slots on first execution. A captured
executor reference therefore pinned the cold-door wrapper (profile evidence:
`_cold_no_overrides_door` called once per no-hooks meld, 4069/4069, plus
per-call `_hydrate_once` checks and `_swap_hot_doors` double slot-writes).
Fix: the entry no longer stores the executor; the fast lane re-reads
`captured_context._no_overrides_executor` per hit (one extra slot load),
which both honors hot swaps and removes the only retained-executor lifetime
edge. The self-replacing-slot contract is now documented on
`CreationContext`.

### Concurrency (free-threaded 3.14)
- dict get/set are atomic per-op; racing first-builds converge last-write-wins
  with one wasted build (same philosophy as executor_code_cache, no lock).
- All guard reads are atomic slot loads. Publication ordering holds because
  context assignment precedes switch advance at every publish site (factory
  leader, build_and_bind, load_cached).

### Why no exec/codegen here
The fast lane has exactly one shape after hydration (existence routing is
resolved at build time), so an emitted door would execute the same loads as a
hand-written closure. The experiment's plain lambda already demonstrated the
closure floor. exec stays available if guard shapes ever diverge per family.

## Retention / memory contract
- Dict cardinality bounded by registry (success-only insertion). No cap.
- Stale entries (invalidated, never re-requested) pin only: old context shell,
  old door closures, executor namespace rows. They cannot pin user instances:
  the orphaned-Creations-store scenario requires ownership transfer or
  upgrade_to_normal, both dynamic-only, both outside this lane's posture.
  This exclusion is a load-bearing wall: extending the lane to dynamic mode
  requires redoing the retention analysis from zero.
- Eager release points (owner-driven): guard-miss in-place replacement,
  `dict.clear()` on door counter bump, `del` in `Meld.cleanup()`.
- Pooled budget: up to ~20 lesser doors + ~20 spellspace doors per root
  conduit retain dicts while pooled (a feature: warm doors survive recycling
  because pooled `Creations` object identity persists across
  `reset_for_pool`). Budget ~= 40 x registry-bounded entries x ~300 B.
- Free-threaded note: replaced closures are deferred-RC objects and reclaim on
  the next GC cycle; GC is left to flow normally per project policy.

## Test matrix (all required before any door code merges)
Invalidation (one per chokepoint; assert fast lane rebuilds and result stays
correct):
1. phase-5 structural rebuild replaces context -> guards 1/2 trip
2. `stamp_ownership` re-stamp -> guards 1/2 trip
3. RiskManager flips validation required True -> guard 3 trips; flipping back
   False re-enables after rebuild
4. `resolution_required` set True -> guard 4 trips
5. spell hook attach -> guard 5 trips; detach re-enables
6. `set_meld_hooks` on door -> counter bump + dict cleared
7. spell cleanup -> guards 1/2 trip; entry replaced on next request resolves
   or raises per normal-lane contract

Exclusion walls:
8. `apply_mutation_override` raises in non-dynamic environment (regression
   pin for the posture exclusion)
9. conduit door still rejects `requires_spellspace_request` spells on the
   fast lane build path

Retention:
10. invalidate entry, never re-request: after `dict.clear()` on door bump (or
    door cleanup), old context/closure graph is collectable (weakref probe)
11. pooled spellspace recycle keeps captured `Creations` identity valid and
    the warm entry serving correct per-scope instances across reuse
12. `Meld.cleanup()` deletes dict + counter; post-cleanup fast-lane access
    fails fast

Equivalence:
13. for each existence route (unique, unique_per_conduit,
    unique_per_spell_space, many, cluster, lineage): fast-lane result is
    `is`-identical to normal-lane result under reuse semantics
14. first-call (build) result identical to normal meld result

Performance (user-run, harness):
15. extend `test_targeted_lesser_spellspace_meld_cycle_harness.py` with a
    "safe cached" row beside normal and unsafe rows; acceptance: warm within
    ~60 ns of the unsafe row, zero correctness deltas

## Open decisions (need explicit user call)
1. Door-dict location: one dict on `Meld` base (shared slot definition, as in
   the experiment) vs per-concrete-door. Recommendation: base slot, exactly
   like the experiment branch.
2. Public surface: internal-only fast lane wired inside `meld()` (transparent
   to callers) vs an explicit opt-in method. Recommendation: transparent
   inside `meld()` so existing callers benefit; no public API change.
3. Whether guard 3 (validation flag) should short-circuit before the dict get
   (saves nothing measurable; keep ladder order as listed).

## Rollout
1. Land the door change counter + tests 1-12 against the normal lane first
   (they pin existing chokepoint behavior even before the fast lane exists).
2. Land the fast lane behind the guards.
3. User runs harness row (test 15) + full gauntlet for before/after.
4. Compiler-agent lane (shared-owner lock path, executor self-time) proceeds
   independently; numbers re-baselined after both land.

## Revision: meld_id removed; positional `spell` seat adopted (2026-06-12)
A `meld_id(spell_id, /)` minimal-arity public entry was briefly added to all
five meld surfaces (Meld base, ConduitMeld, SpellSpaceMeld, Conduit,
SpellSpace) to eliminate keyword-marshaling cost on the warm id-string call.
User rejected the second public resolution method as API bifurcation
("meld and meld_id is not a good thing"), so it was removed the same day in
favor of option (c): `meld(...)` keeps a single public surface, with the
signature reordered so `spell` is the only positional parameter and
`spell_name` is demoted to keyword-only. `meld(spell_id)` is now the
supported minimal-arity warm call shape; it enters the same fast-door lane.
Break profile: positional `meld("logical_name")` callers change meaning
(spell_name -> spell_id lookup; loud KeyError). Repo sweep found zero
positional callers in src/ and benchmarks/; four test files carry positional
callers and are queued for the test-fix lane (codex). The meld_id component
tests were converted in place to positional-meld contract tests, not
deleted. Performance of the new shape: Not run.
