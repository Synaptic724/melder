# Story: release_managed_spell - the class-keyed registry, the lease and the package-root exports

- Completed: 2026-10-15T15:39:41Z
- Summary: landed 0.2.8244 - `ReleaseManagedSpell` (the Aether-owned singleton: register/unregister following the
  root stores, the lock-free class-keyed release and the cold resolver, `managed`, `release_all`, `describe`),
  `ManagedSpellLease`, the Creations register/unregister calls, the cleanup-safe reads they need, four package-root
  exports. Whole tree green in both GIL modes. Release-note section "`Existence.managed_spell_quantity`: objects
  leased from a root-owned pool and released back" extended.

## Metadata
- Story ID: STORY-2026-10-15-release_managed_spell
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/2026-10-14_managed_spell_quantity_epic.md); story 4 of 7
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T09:29:51Z
- Updated: 2026-10-15T15:39:41Z

## User Narrative
As an agent holding a managed object, I want one call that gives it back - `ReleaseManagedSpell.release(obj)` -
without a conduit, plus a lease whose `with` block releases it, so that returning objects is as cheap as using them.

## Value / MRP Alignment
One way back (owner, 2026-10-14): a dict get by class and the pool's put_back. The registry follows the stores so it
holds exactly the live pools, and the cold resolver handles a class managed by several pools with a precise error.

## Ticket Contract
- ENTRY_GATE: S3 closed;
  system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md written and
  linked; the mapping note recorded.
- EXECUTION_BOUNDARY: src/melder/aether/conduit/creations/release_managed_spell.py (new),
  src/melder/aether/conduit/creations/managed_spell_lease.py (new), src/melder/aether/conduit/creations/creations.py
  (register on take, unregister on give-up), src/melder/aether/aether.py (constructs, owns and cleans the
  singleton), src/melder/aether/conduit/creations/managed_spell_quantity.py (`managed_class`),
  src/melder/aether/spellbook/bind/spell_index.py (a cleanup-safe selected-version probe for the resolver),
  src/melder/__init__.py (exports and its workflow map); their tests, tests/unit/melder/test_package_public_surface.py.
- DEPENDENCIES: S3 (pools and Creations).
- EXIT_GATE: its tests green under `-X gil=0` and `-X gil=1`; the touched modules' existing suites green; one notch
  taken from `__version__` at landing with the running release note's managed section extended; the epic's Build
  Specification updated with what this story settled; story closed (completed folder, board sync)
- FAILURE_ESCALATION: DECISION_REQUEST if a change would alter an existing member's behaviour, an existing spell id or
  record, or the frame -> conduit -> Book lock order; CONFLICT when the source contradicts the epic's Build
  Specification (fix the spec first); BLOCKER when a gate cannot be met

## Requirements (Functional)
- B4 as written: `ReleaseManagedSpell` is a singleton like Aether, created and owned by Aether at init, cleaned up
  by Aether, with Aether's reset-singleton feature (owner, 2026-10-15); register/unregister, release with the
  fast path and the cold resolver, managed, release_all,
  describe, ManagedSpellLease.
- Root exports: ManagedSpellMode, ReleaseManagedSpell, ManagedSpellExhaustedError.

## Requirements (Non-Functional)
- Release routing about 100 ns or less over the pool call (measured).
- The registry lock a leaf held only to publish; lock-free reads.

## Scope Boundaries
- In scope: the registry, the lease, the Creations calls, the exports.
- Out of scope: `Conduit.managed_spell_meld` (S5, after dispensing exists).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes and the whole tree green in
  both modes; routing measured; notched 0.2.8244 (delegated routine closure under the owner's go-ahead).
- prior: ready -> in_progress (2026-10-15T14:16:58Z): S3 landed and closed (0.2.8243); S4 started with U11.

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity Build Specification B1, B4.

## Tasks (Implementation Checklist)
- [x] Component patch and mapping note.
- [x] Red tests: routing, filters, ambiguity, not managed, lease, describe, release_all aggregation,
      register/unregister following the store.
- [x] Implement; green in both GIL modes.
- [x] Notch, release note, epic spec update, close, board sync.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- A single-pool class releases with one dict get and put_back.
- Several pools: active-version preference, filters by spell id and conduit, the ambiguity text.
- Creations take/give-up keeps the registry equal to the live pools.

## Validation / Test Plan
- tests/unit/melder/aether/conduit/creations/test_release_managed_spell.py and test_managed_spell_lease.py; a
  routing-cost probe; both GIL modes.

## UX / API / Data Notes
- Public: ReleaseManagedSpell, ManagedSpellLease (module import), root exports.

## Risks / Mitigations
- A release racing a transfer's extract/restore -> not-managed for that call (S6 records it).

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No `src/` edit before the component patch and the mapping note exist.

## Open Questions
- None open.

## Decision Log
- 2026-10-15 (melder_0): root exports beside Existence (epic Decision Log).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_release_managed_spell.md
  - artifacts/managed_spell_quantity_20261015/ (this story's runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: patch docs promoted and archived at S7; artifacts retained

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - ReleaseManagedSpell and ManagedSpellLease
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, design, implementation and tests of this story;
  created 2026-10-15T09:29:51Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-15T09:29:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened ready behind S3. Model: fable_0's ReleaseManagedSpellSimple (class -> pools, one dict get) with the
    2026-10-15 rulings: the active version's pool takes a same-class release; a release after teardown is the agent's.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:28-104
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:186-205
  IMPACT: Fixes the registry shape before S3's Creations hooks.
  NEXT: Start after S3 closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T14:16:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U11 read in source on 0.2.8243. Aether is a class-level double-checked singleton (`_instance`, a class
    `_lock`, `_initialized`); `__init__` builds the hosted roots once under that lock in a fixed order - Crystallizer,
    AetherUtilitySystem, LoadGate, the aetheric Mediator, MutationResearch, Nexus - and rolls its bookkeeping back on
    failure; `cleanup()` tears down the gate, the plane, the frames, then Crystallizer, MutationResearch, the
    configuration, Nexus and the utility system, and resets `_instance`/`_initialized` in a `finally`. Each hosted root
    repeats the shape: `_instance`, a class lock (`_singleton_lock` or `_lock`), `_initialized`, a once-only `__init__`
    under it, a `cleanup()` that resets the singleton bookkeeping at its end, and a classmethod
    `_reset_singleton_for_tests()` that cleans the instance (tolerating a half-built husk) and clears the bookkeeping
    in a `finally`. Nexus refuses a first construction without its host (`ValueError`, bookkeeping reset); Aether
    passes `aether=self`. Fixtures reset Aether, whose cleanup cleans what it hosts. Also read: the resolver's inputs -
    `Spell._spell_index_unless_cleaned`, `SpellIndex.selected_spell_id` (a lock-free read of a field `cleanup` deletes,
    so a racing cleanup surfaces AttributeError), the root id a lesser carries (`Conduit._root_conduit_id`, the root's
    own id on a root), and the package root (a deliberate flat facade by owner ruling 2026-07-19; the no-export-wiring
    law holds below it).
  EVIDENCE:
  - src/melder/aether/aether.py:116-390
  - src/melder/aether/aether_utility_system.py:63-175
  - src/melder/nexus/nexus.py:134-380
  - src/melder/nexus/nexus.py:516-549
  - src/melder/aether/spellbook/spell.py:907-937
  - src/melder/aether/spellbook/bind/spell_index.py:118-165
  - src/melder/aether/spellbook/bind/spell_index.py:323-357
  - src/melder/__init__.py:1-271
  - context_compass/system_docs/patches/active/melder_init_composition_2026_07_19/architecture_patch.md:6-38
  IMPACT: ReleaseManagedSpell copies the hosted-root shape and requires its host on first construction (`aether=`);
    Aether builds it last and cleans it right after the frames, whose stores unregister their pools first. The
    resolver needs a cleanup-safe selected-version probe on SpellIndex. The root exports follow the root ruling
    (user-held surfaces, front-facing enums and user-catchable errors reach it), so the lease joins the three names
    the epic listed.
  NEXT: Write the S4 component and code-description patches and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T14:18:05Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch-section -> implementation -> validation mapping (read after the architecture patch). Singleton shape
    -> `ReleaseManagedSpell.__new__` / `__init__(aether=)` / `cleanup` / `_reset_singleton_for_tests` /
    `_live_instance`, built last in `Aether.__init__` and cleaned after the frames -> unit: one instance, the Aether
    owns it, a bare first construction is refused, cleanup and reset clear it, a cleaned registry refuses. Registry
    state and register/unregister -> copy-on-write maps under the leaf lock -> unit: idempotent, re-key on a changed
    class, holding root on restore, unregister after cleanup does nothing. release / the cold resolver / managed /
    release_all / describe -> unit: the fast path and every branch and text. The lease -> `ManagedSpellLease` ->
    test_managed_spell_lease.py. Creations hooks -> ensure registers, extract and cleanup unregister, restore swaps ->
    Creations unit tests. `managed_class` and `SpellIndex._is_selected_unless_cleaned` -> unit. Root exports ->
    `melder/__init__.py` -> the public-surface suite. Concurrency -> a multithreaded file. Integration -> a real
    Spellbook (conjure and post-conjure bind register, teardown empties the registry, releases by class, spell id and
    conduit). A routing-cost probe. Red first, both GIL modes.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:1-106
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md:1-82
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_release_managed_spell.md:1-46
  IMPACT: The S4 patch gate is met: both patches exist, are linked, and every section maps to code and a test.
  NEXT: Write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T14:51:40Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S4 as built on the working copy (0.2.8243, not yet notched), re-read after the compaction.
    `ReleaseManagedSpell(Cleanable)` has the hosted-root shape: a double-checked `__new__`; a once-only
    `__init__(*, aether=None)` under `_singleton_lock` that refuses a first construction without its host
    (ValueError, bookkeeping cleared); `cleanup()` publishes empty maps as tombstones, keeps `_lock` and resets
    `_instance`/`_initialized`; `_reset_singleton_for_tests()` ignores a husk's AttributeError and clears the
    bookkeeping in a `finally`; `_live_instance()` serves the stores' teardown. State: `_pools_by_class` (class ->
    tuple of pools) and `_registrations` (`id(pool)` -> class, holding root id), copy-on-write under the leaf `_lock`,
    read lock-free. `register(pool, *, root_conduit_id)` is idempotent, only moves the root on a restore into another
    root and re-keys a rebind that brought another class; `unregister` does nothing on a cleaned registry.
    `release` / `managed`: one dict get by `type(obj)`; one pool and no filter -> `put_back` / the lease; else
    `_resolve_pool` (cleaned, filter types, the conduit's root, then spell id and holding root, then the version its
    index selects; not-managed, ambiguity and no-match ValueErrors). `release_all` attempts every object, then one
    ExceptionGroup; `describe(cls)` adds `holding_conduit_id` and `active_version` to each pool snapshot.
    `ManagedSpellLease` releases once (released even when the put-back raises) and `__exit__` never suppresses.
    Aether builds the registry last (after Nexus) and cleans it right after the frames. Creations registers at
    ensure (after the store lock), unregisters at extract and cleanup, and on restore unregisters the replaced pool,
    registers the installed one, then cleans the replaced one. Supporting reads: `ManagedSpellQuantity.managed_class`,
    `_spell_unless_cleaned` (the Spell is deleted under the pool lock now) and `SpellIndex._is_selected_unless_cleaned`.
    The package root exports ReleaseManagedSpell, ManagedSpellLease, ManagedSpellMode and ManagedSpellExhaustedError.
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:100-261
  - src/melder/aether/conduit/creations/release_managed_spell.py:263-349
  - src/melder/aether/conduit/creations/release_managed_spell.py:351-507
  - src/melder/aether/conduit/creations/release_managed_spell.py:509-680
  - src/melder/aether/conduit/creations/managed_spell_lease.py:11-161
  - src/melder/aether/conduit/creations/creations.py:324-397
  - src/melder/aether/conduit/creations/creations.py:1116-1249
  - src/melder/aether/conduit/creations/creations.py:1476-1697
  - src/melder/aether/aether.py:140-266
  - src/melder/aether/aether.py:268-361
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:198-313
  - src/melder/aether/spellbook/bind/spell_index.py:358-388
  - src/melder/__init__.py:77-95
  - src/melder/__init__.py:210-284
  IMPACT: B4 holds as specified, with the two additions in the DECISION below. S5's `Conduit.managed_spell_meld`
    returns this lease; S6's moves keep the registry right through extract and restore.
  NEXT: Run the component and integration shards in both GIL modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T14:51:40Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Build decisions inside the owner's go-ahead, open to the owner's review. (1) The lease joins the package
    root beside the three names B1 listed: the root is the deliberate flat facade (owner ruling 2026-07-19) and the
    lease is a user-held surface. (2) `register` takes `root_conduit_id` and the registry records each pool's holding
    root, because a pool's own `owner_conduit_id` is fixed at construction and keeps naming its first root after a
    move; the `conduit=` filter and `describe` read the holding root. (3) `cleanup` publishes empty maps instead of
    deleting them, so a lock-free release racing teardown misses and raises the cleaned error from the cold path.
    (4) The pool deletes its Spell under its lock and offers `_spell_unless_cleaned`, and SpellIndex gained
    `_is_selected_unless_cleaned`, so the resolver's active-version read never raises under a racing teardown.
    (5) A failed frame teardown leaves the registry published, as it leaves every hosted root: Aether's cleanup
    resets only its own bookkeeping (BUG-149) and the next Aether adopts the live registry.
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:176-207
  - src/melder/aether/conduit/creations/release_managed_spell.py:263-311
  - src/melder/aether/conduit/creations/release_managed_spell.py:577-640
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:130-196
  - src/melder/aether/aether.py:300-361
  - context_compass/system_docs/patches/active/melder_init_composition_2026_07_19/architecture_patch.md:6-38
  IMPACT: B1 lists four root exports and B4 the holding root (epic update at closure). S6 owns whether a moved pool's
    `owner_conduit_id` (its `describe()` key) should follow the move; the registry is right either way.
  NEXT: Run the component and integration shards in both GIL modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T15:36:48Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S4 validated on the device VM (CPython 3.14.7t, every suite under `-X gil=0` and `-X gil=1`). Red first:
    5 import errors, 8 failed, 88 passed. Green, each mode: the new and changed tests 197 passed; unit aether +
    spellbook 6874 passed; unit rest 2508 passed, 3 skipped, 7 xfailed; component spellbook 819 passed; component
    rest 1545 passed, 23 skipped, 1 xfailed; integration aether 785 passed, 5 xfailed; integration conduit, spellbook,
    mutation_research and live_sim 1003 passed, 2 skipped, 1 xfailed, 2 xpassed; integration multithreading 54
    passed; integration crystallizer 276 passed, 3 xfailed (all 279 ids, through the resumable shard runner, because
    the Aether lifecycle changed); experimentation, experiments and tests/tests 250 passed, 4 skipped. The only
    warning is Melder's GIL-mode UserWarning under `-X gil=1`. A docstring-only edit made after those runs (the
    class's Performance section) was rechecked: build assets, creations, public surface, the probe and the
    integration file, 401 passed, 1 skipped. Routing (release then `_idle.pop()`, 200,000 cycles x 7 rounds): the
    pool's `put_back` 66-69 ns a cycle; a bound `registry.release` +50 to +51 ns (min); the one-line
    `ReleaseManagedSpell().release` +137 to +144 ns, because the singleton call itself costs about 70 ns, the same
    as `Aether()` (69-72 ns both). Density: 70 tests on the 294 code lines of the two new modules (24 per 100),
    plus 12 on the changed lines elsewhere. Not run: coverage and hosted CI (the owner's).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_validation_index.md:1-54
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_resumable_summary.txt:1-8
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_release_routing_gil0.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_release_routing_gil1.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_singleton_call_gil0.txt:1-5
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_singleton_call_gil1.txt:1-5
  - src/melder/aether/conduit/creations/release_managed_spell.py:59-62
  IMPACT: The exit gate's test half is met in both modes. The routing target (about 100 ns over the pool call) is
    met with the registry bound once; the documented one-liner also pays the Aether-shaped singleton call, which the
    owner's singleton ruling fixes, so the class docstring and AGENT_PURPOSE now tell hot loops to bind it once.
  NEXT: Notch 0.2.8244 and extend the running release note's managed section.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S4 - the Aether-owned `ReleaseManagedSpell` singleton, `ManagedSpellLease`, the Creations register and
  unregister calls, the cleanup-safe reads they need, the package-root exports.
- State: done; landed 0.2.8244 (the FACT, DECISION and MEASURE notes; runs/s4_validation_index.md).
- Open for the owner's review: the lease on the package root and the holding-root record (DECISION note).
- Next: S5 (STORY-2026-10-15-managed_dispense_codegen) - meld leases through the emitted plans and
  `Conduit.managed_spell_meld` returns a `ManagedSpellLease`.

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
