# Task: Investigate the managed-shell design for `managed_spell_quantity` (three modes) with a VM spike

- Completed: 2026-10-14T23:46:57Z
- Summary: The owner's shell shape investigated on the 0.2.8238 copy and reshaped with him in chat: the Spell
  keeps the options, `ManagedSpellQuantity(deque)` of idle objects in the root's Creations, `ReleaseManagedSpell`
  keyed by class to `(holder, spell_id)`, release = optional reset + append; measured 90-265 ns per lease cycle.
  The settled shape, seam map, numbers and implementation plan are in the epic's Notes (2026-10-14T23:45:47Z).
  No source landed (no notch); the spike is retained under the epic.

## Metadata
- Task ID: TASK-2026-10-14-investigate_managed_shell_design
- Story: none (epic-level investigation; Epic: EPIC-2026-10-14-managed_spell_quantity)
- Status: done
- Owner: user
- Agent Name: fable_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T22:15:12Z
- Updated: 2026-10-14T23:46:57Z

## Objective
Answer, with source evidence and a working-copy spike, whether the owner's shell shape - a `ManagedShell` stored in
the owner store under the spell id, three modes (`limited_quantity`, `elastic`, `queue`), `ReleaseManagedSpell` as
the one way back hosting a `with`, `Conduit.managed_spell_meld("target")` over meld + release, a reset list at bind -
can be built with minimal change to the kernel and the same features; name the exact seams and their costs.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the owner's direction in chat (2026-10-14, "could you investigate this
  idea? ... keep it simple and see what happens"); investigation and a spike on the VM working copy only.
- EXECUTION_BOUNDARY: reads of `existence.py`, `creations.py`, `conduit_creations.py`, the meld doors
  (`conduit_meld.py`, `spellspace_meld.py`, the warm lane of `conduit.py`), `spell.py` ownership stamping,
  `scope_ordering_strategy.py`, `abstract_elastic_pool.py`, `site_plan_lowering.py`; the spike lives under
  `artifacts/managed_shell_spike_20261014/` and `$HOME/work/melder_cc` (prototype module, probes,
  measurements). No tree `src/` edit.
- DEPENDENCIES: EPIC-2026-10-14-managed_spell_quantity (the decided design; melder_1's lane keeps the patch docs);
  0.2.8235/0.2.8238 (children follow the holder).
- EXIT_GATE: FACT notes on every seam with `path:start-end`; the spike runs the three modes through a captured plan
  and a hand-wired door on the working copy with measured acquire/release costs; a DECISION or DECISION_REQUEST on
  the two open points (out-record representation; binding mutation paths); the epic's Decision Log carries the
  owner's direction; the owner reads the result.
- FAILURE_ESCALATION: DECISION_REQUEST when the shell cannot keep an existing member's behaviour or the warm door's
  shape; BLOCKER if a release path cannot stay off the existing lock chains.

## Scope Boundaries
- In scope: reading the seams, a standalone shell + singleton prototype, a captured-plan and door experiment,
  measurements, the written assessment.
- Out of scope: any tree `src/` or `tests/` change; patch docs and stories (melder_1's lane); MelderOps.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: The owner read the result, ruled the four points and the deque shape, and handed
  implementation to the next agent (chat 2026-10-14); the epic carries the handoff notes (2026-10-14T23:46:57Z).
- previous: from_state: in_progress
- to_state: review
- transition_reason: Seams read, spike measured, DECISION and DECISION_REQUEST written, the epic's
  Decision Log carries the result; the owner reads it and rules on the four points (2026-10-14T23:08:03Z).
  Previous: draft -> in_progress, opened on the owner's direction (2026-10-14T22:15:12Z).

## Steps / Checklist
- [x] Read the seams whole: the Existence enum and the resolution matrix, Creations publish/purge/cleanup and the
      disposal walk, ConduitCreations, the warm lane and the creation-context doors, `_add_owned_conduit`, Phase 6
      ranks, the elastic pool base; one FACT note per seam.
- [x] Spike on the working copy: `ManagedShell` (three modes), `ReleaseManagedSpell` (weak index, `with`), a
      captured plan with one site rewritten to `sh.acquire()` + reserve/publish miss, a hand-wired door; measure.
- [x] DECISION / DECISION_REQUEST notes: out-record representation, binding mutation paths, the door route.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The seam map with evidence; the spike module and probes under the artifacts folder; measured costs; the
  written recommendation for the patch docs.

## Files / Paths Impacted
- artifacts/managed_shell_spike_20261014/ (prototype, probes, logs)
- tickets/epics/2026-10-14_managed_spell_quantity_epic.md (Decision Log and Notes, additive)

## Validation
- Run on the VM (CPython 3.14.7t, `-X gil=0`, caching off): `probe_modes.py` run 2 ALL OK (15/15);
  `probe_cost_variants.py`, `probe_plan_shape.py` and `probe_door_modes.py` printed the figures in the MEASURE
  notes; logs under `artifacts/managed_shell_spike_20261014/logs/`. No tree test suite was run (no tree change).
- Recommended commands:
  - `python -X gil=0 context_compass/artifacts/managed_shell_spike_20261014/<probe>.py` on the VM working copy
    (`probe_plan_shape.py` and `probe_plan_capture.py` need `tests/experimentation` on the path)

## Risks / Rollback Notes
- The spike is scratch; nothing lands. Risk: the shell changes what `store._creations.get(sid)` returns for a
  managed spell, so every reader of a store must be found (purge, extract, transfer, teardown, the doors).

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [x] No tree edit from an investigation task.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/managed_shell_spike_20261014/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept as the epic's design evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the managed shell in the owner store; the three modes; the release singleton; the door and plan seams
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): fable_0 (synaptic_python_developer); the whole ticket and the spike; initial
  revision 2026-10-14T22:15:12Z
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: the owner, in chat (2026-10-14): the four points ruled, the deque shape chosen; accepted
  as the reserved-owner disposition ("I'll get opus to do the rest")

## Notes
- DATETIME: 2026-10-14T22:15:12Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened on the owner's direction (chat 2026-10-14): investigate the shell shape - the managed object
    "managed in creations as a special interface", a shell in the Creations store that "pulls out the object
    required in the
    required ways or inserts it back", looked up by spell id like today, root-owned; `ReleaseManagedSpell` as the
    one way back, hosting a `with`; `Conduit.managed_spell_meld("target")`; protocol and mixins dropped; a reset
    list at bind; the three modes `limited_quantity`, `elastic`, `queue`; "the most minimal change ... the same
    features ... keep it simple and see what happens". The assessment that preceded it (chat, 2026-10-14) named four
    gaps: the out-record representation, the miss ordering (reserve before children), binding mutation paths, and
    injection into slotted holders.
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1-120
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-275
  IMPACT: Reading order fixed: the store and its readers first (what a shell in the store touches), then the doors,
    then the lowering, then the spike.
  NEXT: read `creations.py` whole in chunks and list every reader of `_creations` values.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T22:17:41Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The seams, read whole on 0.2.8238. (1) The store: `Creations._creations[sid]` holds one object (slotted) or a
    list (many); `_disposable_creations[sid]` holds a tuple, a `ManyDisposalBucket` or a `HolderDisposalEntry` (the
    holder plus its adopted `many` children, 0.2.8238), and every retirement dispatches on those three shapes by
    isinstance (`_dispose_disposable_registry`, `_dispose_entry`, `extract_spell_creations`, `restore_spell_creations`,
    `_detach_purge_entries`). A shell stored under the spell id is therefore a FOURTH record shape that each of those
    five readers must name explicitly (the `else` branches assume a holder record today); nothing else in the store
    changes. (2) The readers outside the store: the two meld doors (`conduit_meld.py:843-1086`,
    `spellspace_meld.py:783-1027`: live-creation probes, purge resolution, existing lookups) and the emitted door
    templates in `creation_runtime_door_compiler.py:498-865`, one `(route, lane)` template per Existence that reads
    `_owner_creations._creations.get(_spell_id)` and returns the value. (3) The warm lane of `Conduit.meld`
    (`conduit.py:4878-4938`) calls the emitted door's executor (`captured_context._no_overrides_instance_executor`)
    after its guard ladder - it never reads a store itself - so a managed route is one more door template
    (`shell = ..._creations.get(_spell_id); creation = shell.acquire(); if None: reserve, build, publish_out`) and the
    hot door needs no change at all. (4) Ownership: `Spell._add_owned_conduit` (`spell.py:1558-1606`) stamps
    `_owner_creations` under the spell lock at conjure, the one place to create and register the shell; the lowering
    binds that store as a constant for automatic unique sites (`site_plan_lowering.py:1341-1381`), so a managed site
    binds the shell the same way and emits `v = sh.acquire()`. (5) Phase 6 (`scope_ordering_strategy.py:80-121`): a
    rank table keyed by Existence; `managed` = rank 0 is one entry. (6) Bind: `disposal_method_names` flows
    `Spellbook.bind` (`spellbook.py:5400-5450`) -> `Bind._bind_logic` (`bind.py:464-562`) into the Spell; a
    `reset_method_names` list rides the same path and is fingerprinted only for managed bindings. (7) The Existence
    enum (`existence.py:60-117`) is six `auto()` members with `__str__` = name; a seventh member is additive.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:10-120
  - src/melder/aether/conduit/creations/creations.py:470-560
  - src/melder/aether/conduit/creations/creations.py:1134-1206
  - src/melder/aether/conduit/creations/creations.py:1296-1470
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-660
  - src/melder/aether/conduit/conduit.py:4878-4938
  - src/melder/aether/spellbook/spell.py:1558-1606
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - src/melder/aether/spellbook/spellbook.py:5400-5450
  - src/melder/aether/spellbook/existence/existence.py:60-117
  IMPACT: The owner's "minimal change" reading holds: one new class, one Existence member, one door template, one
    lowering branch, five explicit store branches, one Phase 6 rank entry, one bind keyword; the warm meld lane and
    every existing member are untouched.
  NEXT: the spike - `ManagedShell` + `ReleaseManagedSpell` prototype with the three modes, a stress probe, then the
    captured-plan and door-shape measurement on the VM copy at 0.2.8238.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T22:59:45Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probe A (`probe_modes.py`: the three modes and the one way back; CPython 3.14.7t, `-X gil=0`, the VM). Run 1
    failed 1 of 15 checks - a forgotten lease's dead child was not disposed, because `acquire` returned the idle
    object before draining the dead list - and cost 1594 ns per dispense+release cycle single-thread (acquire ~684,
    release ~945) and 3516 ns amortized over 4 threads x 50k; the costs were a weakref plus closure minted per lease,
    the type->shells index read under its lock, and a condition notify on every put_back. Run 2, after one
    persistent weakref per entry (a bound-method callback), the dead check outside the lock in acquire and
    put_back, a copy-on-write index read lock-free and notify only in queue mode: 15/15 ok - limited(3) never
    exceeds 3 under 8 threads (built 3); queue waits, then raises at its 0.25 s timeout, and a waiter is served by a
    release with no build; elastic builds 20 under 20 concurrent leases and caps idle at max_idle=4 (16 destroyed
    with their children); a forgotten lease is collected, its place freed and its dead child disposed on the next
    verb; double and foreign releases raise; a failing reset raises, destroys and frees the place; the `with`
    releases on exit - at 638 ns per cycle single-thread (acquire ~272, release ~628 one-shot) and 939 ns amortized
    over 4 threads. Probe A2 (`probe_cost_variants.py`, elastic, one idle object per thread, two repeats): the
    locked warm path costs 591-604 ns per cycle single-thread and 840-876 ns over 4 threads; a lock-free warm path
    (variant B: `deque.pop`/`append` and one dict store, each atomic per object on 3.14t) 474-485 ns and 724-730 ns,
    so the two leaf-lock sections cost about 115 ns per cycle single-thread and 115-145 ns under four threads.
    Variant B does not keep the shell's invariants: the destroyed flag, the elastic cap and the dead-list drain are
    read outside the lock, so an acquire or put_back racing `destroy_all` or `evict_idle` can hand out or re-idle an
    object those verbs already disposed, and idle can overshoot max_idle. A2's limited(3) check releases at once
    (peak 1), so Probe A's limited check is the one that counts.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:68-88
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:117-143
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:145-183
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:185-235
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:273-294
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:354-389
  - context_compass/artifacts/managed_shell_spike_20261014/probe_modes.py:1-201
  - context_compass/artifacts/managed_shell_spike_20261014/probe_cost_variants.py:1-82
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_modes_run1.txt:1-19
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_modes_run2.txt:1-19
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_cost_variants_run1.txt:1-8
  IMPACT: Against the epic's targets (about 5 us to acquire and about 1 us to return a ChannelLogger-like object;
    74-82 us for a fresh logger meld) the locked shell is an order of magnitude inside both, so the lock-free
    variant buys nothing the design needs: keep the one leaf lock (N1) and the one way back. A reuse cycle is about
    20x a warm `unique` site read (~30 ns) and about 120x cheaper than the fresh logger meld; what remains is the
    Python-level verbs themselves (type lookup, weakref check, the reset call, two lock sections).
  NEXT: Probe B on `$HOME/work/melder_cc` (0.2.8238): capture the normal plan of a Worker(many) -> Service(unique)
    root, rewrite the Service site to `sh.acquire()` with a reserve/publish miss, run it and measure acquire+release
    per creation against today's unique site read; then the hand-wired door shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:02:58Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probe B on the 0.2.8238 working copy (`-X gil=0`, caching off). B0 captured the emitted normal plan of the
    worker shape (Manager `unique` with disposal -> Worker `many` with disposal) through the certification
    harness: the S9 body reads the Manager site as `v0 = c0._creations.get(sid0)` / `if v0 is None: v0 =
    _miss0(meld, c0)` with `c0` the owner store bound in the namespace. B1 executed that body unchanged and a
    transformed body whose Manager site reads a locked elastic `ManagedShell` instead (`v0 = sh0.acquire()`;
    the miss reserves, builds `t0()`, cancels on failure, publishes out), one Worker creation per call, the
    user's release included for the managed one: plain 166 ns per creation (3 py / 5 C calls); managed +
    `ReleaseManagedSpell.release` 715 ns (6 / 19); managed + release through the shell that dispensed it 584 ns
    (5 / 17); over 4 threads x 30k the managed cycle is 1044 ns amortized against 307 ns plain. The door shapes
    alone: the owner-store read 30 ns; `sh0.acquire()` + put_back through the shell 428 ns; `acquire` +
    `ReleaseManagedSpell.release` 521 ns; `Manager()` itself 70 ns; the whole `conduit.meld("Worker")` 337 ns.
    B2, the warm cycle per mode on the shell alone (one idle object): elastic 407 ns (shell) / 505 ns (singleton),
    with a declared `reset()` 478 / 599; limited_quantity(4) 389 / 484; queue(4, 1.0 s) 470 / 567 (its notify);
    the `with ReleaseManagedSpell.managed(...)` form costs 1067-1172 ns because it is a `contextlib.contextmanager`
    generator - a small class with `__enter__`/`__exit__` is the shape to emit instead.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/probe_plan_capture.py:1-38
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_capture_worker_source.txt:1-23
  - context_compass/artifacts/managed_shell_spike_20261014/probe_plan_shape.py:1-201
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_shape_run1.txt:1-11
  - context_compass/artifacts/managed_shell_spike_20261014/probe_door_modes.py:1-77
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_door_modes_run1.txt:1-4
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1319-1381
  IMPACT: The lease costs 400-550 ns per creation over a warm `unique` read, all of it the Python-level pool verbs
    (two method calls, two leaf-lock sections, the id/dict/deque work); the one way back costs 93-100 ns more than
    a release through the known shell (the type lookup, the out-record get and the weakref check), inside the
    epic's "about 100 ns" routing budget. Pooling pays for an object that costs more than about 0.5 us to build:
    the Iris logger (74-82 us) by two orders of magnitude, a 70 ns `Manager` not at all - the mode changes nothing
    on the warm path (queue +65-80 ns for its notify). A managed site drops into the emitted plan as one more
    site shape; the plan's other sites, the many registration and the door are untouched.
  NEXT: the DECISION and DECISION_REQUEST notes (out-record representation, binding mutation paths, the door
    route and the `with` shape), then the recommendation into the epic's Decision Log.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:06:02Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The shell shape is buildable as the owner read it, and these points are settled by the evidence. (1) The
    door route: the hot `Conduit.meld` warm lane is untouched; a managed spell gets one more emitted door template
    (read the shell from the owner store under the spell id, `acquire()`, else the plan's miss) and one more site
    shape in the lowering (`v = sh.acquire()`, bound like the S9 store constant); the plan's other sites, the many
    registration and the guard ladder do not change (Probe B: the transformed body is the plain body with one site
    swapped). (2) The miss order: `reserve()` first (limited refuses, queue waits, both before anything is built),
    then the site's children, then the object, then `publish_out(entry, object, children)`; a failed build
    `cancel()`s the place and disposes the children it built. A managed site has no slot guard - the shell is its
    guard - and its children are built before any holder's guard is taken (the 0.2.73/0.2.8235 order), so a queued
    wait never holds a store or build lock. (3) The out-record: one `ManagedEntry` per object with one persistent
    weakref (created at first publish, reused across leases; strong `item` while idle), an `_out` dict keyed by
    `id(object)`, and the identity check `entry.ref() is object` on release; a recycled id cannot match because
    the dead object's callback removed its entry before its memory could be reused, and the callback does
    bookkeeping only (count, dead list) under the shell's leaf lock, never disposal. (4) Locking: one leaf lock
    per shell; reset and disposal run outside it; the lock-free variant is rejected (115-145 ns per cycle for
    broken teardown and cap invariants, Probe A2). (5) Costs against the targets: acquire 272 ns and release
    628 ns (<5 us / <1 us), routing through the one way back +93-100 ns (<=100 ns), a reuse cycle 400-550 ns over
    a warm unique read, so pooling pays above about 0.5 us of construction and the logger case wins by two orders.
    (6) The `with`: a small class with `__enter__`/`__exit__` that releases through the shell that dispensed
    (Probe B2: the generator form costs 600 ns more); `Conduit.managed_spell_meld("target")` returns it.
    (7) Shell creation and travel: `_add_owned_conduit` is the one stamping point - conjure, post-conjure bind and
    bind_inactive, the transfer flip - so the shell is created there (adopting one already stored under the same
    id, which the fingerprint makes the same configuration) and registered in `ReleaseManagedSpell`; a transfer's
    `_move_creations` moves it as the fourth record shape through `extract_spell_creations` /
    `restore_spell_creations`, the same object, so the index and every out lease are untouched; a lesser upgrade
    keeps its stores. (8) The index: type -> tuple of shells, copy-on-write under its own leaf lock, read lock-free;
    a release scans the class's shells with one dict get each.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:68-88
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:145-183
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:273-294
  - context_compass/artifacts/managed_shell_spike_20261014/managed_shell.py:328-389
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_shape_run1.txt:1-11
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_door_modes_run1.txt:1-4
  - src/melder/aether/spellbook/spellbook_creation_system.py:1350-1375
  - src/melder/aether/spellbook/spellbook.py:5255-5290
  - src/melder/aether/spellbook/spellbook.py:5590-5620
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1470-1545
  - src/melder/aether/conduit/creations/creations.py:1302-1330
  IMPACT: The minimal change set for the patch docs: one Existence member; `ManagedShell` + `ManagedQuantity` +
    `ReleaseManagedSpell` (one module); one door template; one lowering site shape; the fourth record shape in the
    five store readers; one Phase 6 rank entry; two bind keywords (`quantity`, `managed_spell_reset_methods`)
    fingerprinted only for managed bindings; one cache generation bump; RecordVersion for the quantity. No change
    to the six members or the warm lane.
  NEXT: the DECISION_REQUEST below (what only the owner can rule), then the epic's Decision Log.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:06:02Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Four rulings the spike cannot make. (A) F9's letter versus the weak out-record: with the weak index a
    lease nobody returns is reclaimed when its holder dies, its place freed and its `many` children disposed on
    the shell's next verb (Probe A: "forgotten lease" checks), so a leaked object no longer holds a limited place
    until root teardown - recommended, it keeps "we just trust" (no reference is held, nothing is checked at the
    user's expense) and still refuses double and foreign releases; the alternative, strong references to out
    objects, pins every leak for the root's life. (B) Binding mutation paths: on `notch` (the outgoing version)
    and `cleanup_spell` of a managed spell the shell is retired - idle objects destroyed now, out objects destroyed
    at their release, the shell dropped from the store and the index when its count reaches zero - instead of the
    slotted members' "product left alive in its slot" (0.2.8219); a rebind under the same id meanwhile gets a fresh
    shell; `purge(instance)` destroys that object and frees its place, `purge_all` is the same soft eviction
    (open question 3); recommended. (C) Injection into a slotted holder: a `unique` or per-conduit holder that
    takes a managed dependency holds the lease for its own life, so a limited or queued pool feeding such holders
    exhausts by design; recommended: allowed with no Phase 6 rule (the managed spell ranks with unique), documented
    as a lifetime lease the holder's own disposal may release, and the inspection listing names the holders' out
    objects. (D) Overrides on a managed site: refused (a dispensed object is reused by other holders), as the epic's
    (g) recommends. Independent of these, the owner's earlier defaults (a)-(j) still await their answers.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_modes_run2.txt:13-15
  - src/melder/aether/spellbook/spellbook.py:4325-4420
  - src/melder/aether/spellbook/spellbook.py:3824-3965
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-258
  IMPACT: (A) and (B) change the shell's verbs (a `retire()` beside `evict_idle()`/`destroy_all()`, a put_back that
    destroys on a retired shell); (C) and (D) are Phase 6 and lowering rules; none changes the measured warm path.
  NEXT: report to the owner; on the rulings, melder_1's patch docs carry the shape, this task closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:18:14Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner ruled on the DECISION_REQUEST (chat, 2026-10-14) and corrected its model: Melder is a living
    runtime - tools are built on the fly, stored in conduits, rebuilt six times with the newest kept, and the whole
    scope is destroyed when it is done - so objects that are out "maybe are still being used" and nothing polices
    them. (A) Out-record: a plain dict of STRONG references keyed by id(object) (the record exists only so a release
    finds the shell it came from among the roots managing that class and the count comes back down); the weak
    record is withdrawn - F9 stands as written, an unreleased object holds its place until the scope is torn down,
    and the scope teardown is the reclaim. (B) Notch and cleanup_spell destroy nothing: the outgoing version's shell
    stays in the root's store under its id, its out objects keep working and come back to it, and a rebind under
    the same id meets that shell (same configuration, the quantity is fingerprinted); only scope teardown or the
    owner's purge disposes anything; no `retire` verb (consistent with 0.2.8219's "product left alive in its
    slot"). (C) Injection: slots do not matter; a holder built once keeps its injected managed object for its own
    life and whoever disposes the holder (or the scope teardown) releases it, never Melder on its behalf; no Phase 6
    rule, withdrawn. (D) Overrides on a managed site are allowed: the supplied object is used for that construction,
    the key-set plan skips the site, no lease is taken and nothing stored is replaced (the "stored shared instance"
    refusal does not apply to a dispenser); the epic's default (g) is reversed. (E) `ManagedShell` and
    `ManagedQuantity` merge into one class: `ManagedShell.elastic()` / `.limited_quantity(n)` /
    `.queue(n, timeout_seconds)` is the inert bind-time declaration (mode and numbers; hashed into the fingerprint and
    recorded), and each root owning the binding keeps a live copy in its store. The warm path measured in the
    MEASURE notes is unchanged by (A)-(E): the strong record is the same dict get as the weak one minus the weakref
    check.
  EVIDENCE:
  - tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md:325-355
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:99-128
  - src/melder/aether/spellbook/spellbook.py:3824-3965
  IMPACT: The change set shrinks: one class instead of two, no weakref or callback, no retirement verbs, no Phase 6
    or override rule for managed sites; F5 (double and foreign release refused) and F8/F9 stand as the epic wrote
    them; open questions 3 (purge with no instance destroys the idle objects, out objects come back as usual) and 6
    are answered by these rulings.
  NEXT: the owner reads the corrected shape; this task closes on his word and melder_1's patch docs carry it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:27:40Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probe C, the owner's simpler shape (chat 2026-10-14): the holder is a `deque` subclass
    (`ManagedSpellQuantity`) of idle objects kept in the Creations object under the spell id, the mode and numbers
    composed from the Spell when it is created, no out-record, no identity checks; the emitted site is an inline
    `try: v = h.pop() except IndexError: v = <miss>`; release is `append` after the optional reset (elastic trims
    the oldest idle above max_idle, queue notifies). On the VM (3.14.7t, `-X gil=0`), one idle object, acquire +
    release per cycle: elastic 140 ns through `ReleaseManagedSpell` / 90 ns through the known holder (with a
    declared `reset()` 215 / 149); limited_quantity(4) 124 / 82; queue(4, 1.0 s) 265 / 239 - against 505 / 407,
    484 / 389 and 567 / 461 for the spike's `ManagedShell` (Probe B2), 3-4x cheaper, and a whole cycle now costs
    about three to five warm `unique` reads (30 ns). The checks that matter still pass: limited(3) never exceeds 3
    under 8 threads (built 3; the refusals are the limited mode's raise, 13792 of 16000), queue(1, 0.25 s) waits
    then raises at its timeout, and a waiter is served by a release (the same object, no build).
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:1-193
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_deque_holder_run1.txt:1-7
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_door_modes_run2.txt:1-4
  IMPACT: The owner's shape is both simpler and faster: the acquire is a deque pop inlined in the plan (no method
    call, no lock - `deque.pop`/`append` are atomic per object on 3.14t) and the lock exists only on the cold
    paths (the limited/queue count, the queue wait) and the elastic trim.
  NEXT: the DECISION below records the shape; the task closes on the owner's word.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:27:40Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner direction (chat 2026-10-14), superseding the DECISION notes above where they differ: the Spell
    retains every managed requirement as bind options (the mode, the limit, the timeout, the idle cap, the reset
    names) - no settings object and no new composition frame; Creations composes the holder from the Spell: a new
    holder kind, `ManagedSpellQuantity(deque)`, the idle objects, with the elastic system built into the subclass
    optionally; "we don't care about identity": release appends, nothing is checked, a double release is the
    user's. What the shape still needs, all off the warm path: (1) `_built`, the strong list of every object the
    holder built, appended once at build, so `limited`/`queue` count against `len(_built)`, root teardown destroys
    idle and out objects alike (F8), and `purge(instance)` finds its object by a cold identity scan; (2) a side map
    id(object) -> its disposal-bearing `many` children, written only at build and only for objects that have any,
    read only when the object is destroyed, so the 0.2.8235/0.2.8238 rule (children die with the object they were
    built for) holds; (3) release routing by type(object) -> the one holder of that class in the normal case, and
    the meld-style target (`release(obj, target)`) when the same class is bound in two Books, raised as an ambiguity
    like meld's; (4) the holder created at `_add_owned_conduit` from the Spell so the lowering binds it as a plan
    constant like the S9 store (`h0`), and the site inlines the pop; (5) `with` as a small class holding the holder
    and the object (`__exit__` appends; 90 ns measured), returned by `conduit.managed_spell_meld("target")`.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:28-91
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_deque_holder_run1.txt:1-7
  - src/melder/aether/conduit/creations/creations.py:1302-1330
  - src/melder/aether/spellbook/spell.py:1558-1606
  IMPACT: The change set: one Existence member; the bind options on the Spell (fingerprinted); one `deque` subclass
    in Creations with its own dict branch in the five readers; one door template and one inline site shape; one
    Phase 6 rank entry; `ReleaseManagedSpell` as a type -> holder index; cache generation and RecordVersion bumps.
    The spike's `ManagedShell`, its entries and weakrefs are retired as reference only.
  NEXT: the owner reads this; melder_1's patch docs carry the deque shape; this task closes on the owner's word.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:37:08Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner direction (chat 2026-10-14) on `ReleaseManagedSpell`: it is a dict keyed by the managed class
    (`type(obj)` is the class object itself, identity-hashed, one dict get of about 35 ns on the VM) whose value
    pairs the holder with its spell id - `(holder, spell_id)` - so a release is `registry[type(obj)]` then
    `holder.put_back(obj)` (the reset names registered at bind, optional, then `append`), and the spell id is the
    key into the owning root's Creations dict for every cold path (purge, teardown, the transfer move, inspection).
    Root conduits register their pairs at conjure, when the owner store is stamped and the holder composed from the
    Spell, and unregister at teardown; helper methods on the class are welcome. A class bound in two Books (or the
    same spell id in two frames under per-frame ids) holds a tuple of pairs: one pair routes directly, more make the
    bare `release(obj)` an ambiguity and `release(obj, target)` picks by the meld-style target. `id(obj)` (an int,
    no reference held, valid only while the object lives) is not needed for routing and stays unused.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:94-104
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_deque_holder_run1.txt:1-7
  IMPACT: Resolution and the store lookup are each one dict get; nothing is added to the warm cycle measured in
    Probe C (140 ns elastic through the singleton).
  NEXT: the owner's word closes the task; the epic's Decision Log gets one consolidated line for the final shape at
    close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-10-14T23:46:57Z: DONE (was REVIEW). The seams are read (FACT), the spike ran on the 0.2.8238
copy (two MEASURE notes), the shape is decided where the evidence decides it (DECISION) and four rulings are
the owner's (DECISION_REQUEST); the epic's Decision Log and Notes carry the result. The prototype and probes
stay under the artifacts folder (retain_as_reference). Waiting on the owner's reading; nothing landed in the
tree. The owner's rulings of 2026-10-14T23:18:14Z (strong out-record, nothing destroyed on notch or cleanup_spell, no
injection or override rule, one class) are in the latest DECISION note and the epic's Decision Log. Resume:
the task closes on the owner's word; melder_1's patch docs carry the deque shape of 2026-10-14T23:27:40Z (the
Spell keeps the requirements, `ManagedSpellQuantity(deque)` in Creations, no identity tracking; Probe C
measured it).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
