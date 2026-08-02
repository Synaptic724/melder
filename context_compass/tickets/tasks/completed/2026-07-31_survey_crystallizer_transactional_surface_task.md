# Task: Survey the Crystallizer transactional surface

## Metadata
- Task ID: TASK-2026-07-31-survey-crystallizer-transactional-surface
- Story ID: STORY-2026-07-31-subsystem-transactional-survey
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: completed
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-08-02T17:30:00Z

## SELF-CONTAINED BY DESIGN
You do NOT need the history of the investigation that produced this task. Read
the epic's Problem section for the why, then work only from the reads below.
This task is READ-ONLY. Do not change code.

## Purpose
Establish what in Crystallizer actually needs transactionalizing, so the
AethericMediator plane can be wired to it later without guessing.

## Starting Facts (verified 2026-07-31; re-verify, do not trust)
Crystallizer currently protects concurrent structural mutation with:
Aether-hosted LoadGate (globally exclusive, one load at a time; cohort enrolled via _enroll_restore_cohort so the load's own 4 default workers pass free), engine-local _build_lock for check-then-posture, and posture idempotence. Failure handling is _teardown_built() (newest-first, best-effort, swallows per-unit cleanup errors) plus an 80-site shortfall ledger.

## Required Reads
- `context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md`
  (Problem, Component Split, Key Design Decisions)
- src/melder/crystallizer/ -> crystal_loader_system/crystal_loader_system.py, crystal_loader_system/restore_engine.py, crystal_loader_system/load_plan.py

## Questions To Answer (each with file:line evidence)
1. What STRUCTURAL MUTATION verbs does Crystallizer expose or perform? Name them.
2. What protects each today, and what does that protection NOT cover?
3. What SCOPE KEYS would express those mutations? Propose concrete strings using
   the namespaced flat form (e.g. `crystallizer:<unit>:<id>`).
4. What MODE does each need - `x` exclusive, `s` shared, or `ix` intent?
   Justify any `ix`; do not use it by default.
5. What are Crystallizer's "BASIC CONDITIONS" - the state it would emit to the plane
   when it becomes enabled and active? (Owner constraint 6.)
6. Is there any protection here that CANNOT be expressed as scope claims? That is
   a first-class finding, not a failure - record it loudly.

## Acceptance Criteria
- All six questions answered with `path:start-end` evidence.
- Proposed scope keys and modes are concrete, not descriptive.
- Any inexpressible protection is recorded as a CONFLICT note.
- No code changed.

## Applicable Anti-Patterns
- [x] No proposing a design; this is a survey.
- [x] No promoting a doc claim to FACT without opening the source.
- [x] No code changes under a read-only task.

## Validation / Test Approach
Not run - read-only survey. Verification performed instead: all 30 `path:line`
references in the findings were re-resolved against source programmatically
(each line's +/-3 window checked for the symbol it is cited for); 0 mismatches.
Method-range citations were corrected after that check - `activate` is 544-633
not 574-633 (574 was its body start, which would mislead a reader grepping for
`def activate`), and `_teardown_built` ends at 2669 not 2670.

## SURVEY FINDINGS (bootstrap_0, 2026-08-02T17:30:00Z)

Read-only. No code changed. Every claim below was taken from source, not from
the Starting Facts block or from `src_components.md`.

### CORRECTION to the Starting Facts (they said re-verify, so I did)

The block says "an 80-site shortfall ledger". Actual count is **36 call sites**
of `add_shortfall(` repo-wide, all of them in `restore_engine.py`, carrying **18
distinct literal reason strings**. Nothing else in `src/melder/` calls it. The
"80" figure is not reproducible from source and should not be carried forward.
Everything else in the block verified: LoadGate is globally exclusive
(`load_gate.py:14-30`), the cohort is enrolled via `_enroll_restore_cohort`
(`crystal_loader_system.py:249-271`), the pool defaults to 4 workers
(`crystallizer_configuration.py:537`), `_build_lock` guards check-then-posture
(`restore_engine.py:1636`), and `_teardown_built` is newest-first best-effort
that swallows per-unit errors (`restore_engine.py:2647-2669`).

---

### Q1. What STRUCTURAL MUTATION verbs does Crystallizer expose or perform?

They fall into four classes, and the classes matter more than the list because
each class has a DIFFERENT protection story.

**(a) World unfold - builds live runtime objects from the record.**
- `CrystalLoaderSystem.load_checkpoint(checkpoint_id)` -
  `crystal_loader_system.py:273-326`
- `CrystalLoaderSystem.restore_formation_record(record, target_frame_name,
  skip_existing)` - `crystal_loader_system.py:328-398`
Both funnel into `LoadAdmission.execute_plan` -> `RestoreEngine.restore()`
(`restore_engine.py:643-707`), which runs one of two drivers:
`_restore_sequential` (`:709-775`, nine named stages ending in contracts) or
`_restore_parallel` (`:868-933`, sequential head then `topological_levels()`
executed as scheduler phases). Units the engine builds are frames, books, binds,
conjures, indexes, links, clusters and contracts - every one appended to
`_built_stack` via `_record_built_unit` (`:624-642`).

**(b) Graft - mutates a LIVE host book, outside any load.**
- `Crystallizer.graft_index(graft_record, host_spellbook, ...)` -
  `crystallizer.py:937-1019` (the `GraftRunner` construction and `runner.run()`
  call are the last ~15 lines of it).
- `GraftRunner.run()` - `graft_runner.py:226-326`.
This binds members ACTIVE, parks others via `bind_inactive`, and can `notch` a
selection. It is the only Crystallizer verb that writes live structure without
being a load. (`Crystallizer.capture_index_graft`, `crystallizer.py:902-935`, is its
read-only half.)

**(c) Record mutation - writes the ledger the unfold later reads.**
The `Crystallizer.emit_*` family (`emit_spell_crystal` at
`crystallizer.py:1021-1050`, `emit_spell_removed`,
`emit_spellbook_removed`, `emit_cluster_removed`, `emit_contract_removed`,
`emit_spell_index_removed`, `emit_frame_removed`, `emit_nexus_state`,
`emit_mutation_research_state`, `emit_spell_activity`) plus the checkpoint verbs
(`create_checkpoint`, `flush_checkpoint`, `delete_cached_checkpoint`) and the
profile verbs (`create_profile`, `set_active_profile`, `clear_profile`,
`delete_profile`). These land on `PersistenceSystem`
(`persistence_system.py:279+`) and `AssetManagementSystem`.

**(d) Policy install - changes how (a) will behave.**
- `Crystallizer.activate(...)` - `crystallizer.py:544-633`. Installs checkpoint
  cadence + retention, auto-flush, and calls
  `configure_restore_scheduler(parallel_enabled, worker_count,
  barrier_timeout_ms)`.
- `CrystalLoaderSystem.configure_restore_scheduler(...)` -
  `crystal_loader_system.py:185-247`. **Replaces the pool**: cleans an existing
  scheduler (sentinel + join) before installing the new one.

---

### Q2. What protects each today, and what does that protection NOT cover?

**(a) World unfold - THE ONLY WELL-PROTECTED CLASS.**
Protection: `Aether.acquire_load_authority(label, drain_timeout=30.0)`
(`aether.py:1015-1095`) claims the process-wide `LoadGate` FIRST, then polls
every live frame's mediator active-session count to zero, re-snapshotting the
frame registry each slice so frames born mid-drain are counted. Released in a
`finally` on both verbs (`crystal_loader_system.py:324-326`, `:396-398`). The
holder's own pool threads are enrolled into the span cohort so they pass
(`:249-271` -> `aether.enroll_load_worker` -> `LoadGate.enroll_worker`).
Within the run, `_build_lock` (`restore_engine.py:562`) serializes the
teardown-stack append (`:642`) and the check-then-posture pair (`:1636`).

WHAT IT DOES NOT COVER - and this is the important part:
The gate is only consulted in **two places in the entire codebase**:
`transaction_mediator.py:359` and `transaction_mediator.py:501` - the
`begin_transaction` / `begin_frame` NEW-ROOT ingresses. So the LoadGate bars
*root transactions*, not *mutation*. Anything that changes structure WITHOUT
opening a root transaction walks straight past a held gate. `_ensure_frame` is
exactly such a path (see Q6).

Second gap: the drain is a **poll to zero with a deadline**, not a barrier. It
proves no session was active at the instant of the last slice. Between that
instant and the first replay stage, a thread already past `wait_for_passage`
(it passed before the gate was claimed) can still be mid-verb. The gate closes
the front door; it does not evict whoever is already inside.

Third: `drain_timeout` releases the gate before raising (`aether.py:1035-1036`
contract), which is correct - but means a slow world turns a load into a refusal,
not a wait.

**(b) Graft - EFFECTIVELY UNPROTECTED AT THE GRAFT GRAIN.**
`graft_index` does NOT call `acquire_load_authority`. Its body is
`check_cleaned()` -> `_require_activated()` -> construct `GraftRunner` ->
`run()` -> `cleanup()`. `GraftRunner`'s own docstring states the posture
plainly: *"Thread-confined to the calling thread (the host book's verbs run
their own per-verb transactions)"* and *"Unlike a world load it is NOT one
transaction - each member entry is its own self-admitting per-verb
transaction"*.
So a graft of N members is N independent transactions. Nothing prevents a
concurrent structural mutation from interleaving between member 3 and member 4,
and nothing rolls back members 1-3 if member 4 refuses. This is a documented
design choice, not an oversight - but it is the clearest case in Crystallizer of
"a mutation that wants a transaction and does not have one."

**(c) Record mutation - per-object locks with one read-then-act seam.**
`PersistenceSystem` holds one instance RLock and its docstring says it serializes
"registry mutation, active selection, and checkpoint sealing. Profiles serialize
their own content ops." Verified: `set_active_profile` (`:221-243`),
`create_checkpoint` (`:939-1010`), `detach_profile_chain` (`:1114-1162`),
`capture_formation_record` (`:752-824`) and `insert_cached_items` (`:861-902`)
all take `self._lock`.
`record_spell_crystal` (`:279-297`) does **not**. It reads `self.active_profile`
(which takes the lock at `:188-202` and releases it on return) and then calls
the profile's own verb. That is a read-then-act pair across two different locks:
a `set_active_profile` interleaving between them lands the crystal in the
profile that was active when the emit began. That may well be the intended
semantics - an emit belongs to the profile that was live when it happened - but
it is nowhere stated as a contract, which is precisely the class of local,
unwritten decision this epic exists to consolidate.
`AssetManagementSystem` holds its own RLock with a declared one-way order
(asset lock -> record public verbs, "the record never calls the asset system,
so no inversion can occur").

**(d) Policy install - the loader lock only.**
`configure_restore_scheduler` runs under the loader RLock and its docstring says
"no load may be in flight". Nothing ENFORCES that. The loader lock is held by
`load_checkpoint` for the whole span, so a concurrent call would block rather
than corrupt - which is adequate today, and is adequate by accident rather than
by claim.

---

### Q3. What SCOPE KEYS would express those mutations?

Concrete strings, namespaced flat form:

| mutation | scope key(s) |
| --- | --- |
| world unfold (checkpoint) | `crystallizer:load:world` |
| world unfold (formation, retargeted) | `crystallizer:load:world`, `frame:<target_frame_name>` |
| graft into a host book | `spellbook:<host_book_id>`, `conduit:<host_conduit_id>`, `spell_index:<live_index_id>` |
| graft, merge mode | additionally `spell_index:<merge_into_index_id>` |
| record emit (custody row) | `crystallizer:profile:<profile_name>` |
| active-profile swap | `crystallizer:profile:*` (or `crystallizer:active_profile`) |
| checkpoint seal | `crystallizer:profile:<profile_name>`, `crystallizer:ledger` |
| asset cache write / flush / delete | `crystallizer:asset:<checkpoint_id>` |
| formation store / delete | `crystallizer:asset:formation:<formation_name>` |
| restore-pool policy install | `crystallizer:load:policy` |

`crystallizer:load:world` is deliberately ONE key, not a set. That is what the
LoadGate means today and the survey should not quietly widen it: today's law is
one load at a time, process-wide.

---

### Q4. What MODE does each need?

| scope key | mode | justification |
| --- | --- | --- |
| `crystallizer:load:world` | **x** | One load at a time is the existing law (`LoadGate`: a second acquire from ANY thread refuses, including the holder - a nested acquire is a pairing bug, not a wait). |
| `frame:<target_frame_name>` | **x** | The load postures the frame and builds into it. |
| `spellbook:<host_book_id>` (graft) | **x** | Members bind into it; a concurrent bind/notch on the same book is exactly the interleave that is unprotected today. |
| `conduit:<host_conduit_id>` (graft) | **x** | Matches how the frame's own `add_to_index` / `notch` strategies already claim spellbook+conduit exclusively. |
| `spell_index:<index_id>` | **x** | The selection pointer is repointed. |
| `crystallizer:profile:<name>` (emit) | **s** | Emits are appends into distinct locations; they do not conflict with each other. Shared is the honest mode and it makes the swap case (below) expressible. |
| `crystallizer:active_profile` (swap) | **x** | Must exclude the readers holding `s` on a profile - this is what makes the `record_spell_crystal` seam in Q2(c) a stated contract instead of an accident. |
| `crystallizer:profile:<name>` (checkpoint seal) | **x** | Sealing reads the whole profile and writes a ledger entry. |
| `crystallizer:asset:<id>` | **x** | Byte-level file writes. |
| `crystallizer:load:policy` | **x** | Replaces the pool (cleans and joins worker threads). |

**No `ix` proposed anywhere.** The task says justify any `ix` and not to use it by
default, and I could not find a case that earns it. `ix` in the frame's DevOps
plane means "I will later escalate this to exclusive, block others from doing the
same" - it fits `link`/`cluster` work where an owning spellbook is touched
indirectly. Crystallizer's mutations claim their targets directly and up front;
there is no two-phase escalation in any of the four classes. If wiring later
discovers one, it should be added with a reason, not defaulted in now.

---

### Q5. What are Crystallizer's BASIC CONDITIONS on enable? (Owner constraint 6)

"Enabled and active" has a precise moment: `Crystallizer.activate(...)`
(`crystallizer.py:544-633`), which sets `_activated = True` under the instance
lock and installs the frozen policy. The state it would emit to the plane at
that moment, all read from that method body:

1. `crystallizer.active = true` and `crystallizer.id = <self._id>` - every
   emission seam in the codebase checks `_activated` before emitting
   (`activated` property contract), so this flag is the difference between a
   recording world and a silent one.
2. `active_profile = <name>` - the record's selected profile, since almost every
   record-side scope key is namespaced under it.
3. `restore_parallel_enabled` (schema default **True**), `restore_scheduler_workers`
   (default **4**), `restore_scheduler_barrier_timeout_milliseconds`
   (default **60000**) - `crystallizer_configuration.py:516,537,561`. The plane
   needs the worker count because those threads are the load span's COHORT: they
   must be admitted alongside the holder or every restore unit deadlocks against
   the plane the same way it would against the gate.
4. `max_persistence_crystals` (retention cap) and `checkpoint_interval_minutes`
   (the emit-driven ticker cadence) - these make checkpoint sealing a
   *scheduled* mutation, not only a user-invoked one, which the plane must know
   or it will see unexplained periodic claims on `crystallizer:ledger`.
5. `auto_flush_checkpoints` (default **False**) - when true, sealing also writes
   bytes, so a ledger claim implies an asset claim.
6. `drain_timeout = 30.0s` (`aether.py:1018`) and the load-authority label
   format (`checkpoint_load:<id>` / `formation_load`,
   `crystal_loader_system.py:305,377`) - the plane inherits the deadline
   semantics and the human-readable holder label that today's teach-grade
   timeout error depends on.

Point 3 is the one that will bite if it is missed: the cohort is not an
optimisation, it is a correctness requirement inherited from `LoadGate`'s "no
membership survives a span" law.

---

### Q6. Protection that CANNOT be expressed as scope claims

**CONFLICT (primary) - frame creation is invisible to the admission authority.**
This is the epic's Problem-section claim, and it holds up under source reading,
so I am recording it as VERIFIED rather than inherited:

- `Aether._ensure_frame(name)` (`aether.py:893-941`) creates and registers a
  frame under the **Aether lock**.
- `AethericFrame.bind_frame_configuration(posture)`
  (`aetheric_frame.py:626+`) applies posture under the **frame's own lock**.
- `RestoreEngine` calls them as two separate statements
  (`restore_engine.py:1706-1708`), guarded only by the engine-local
  `_build_lock`.

Two different locks, two acquisitions, no shared authority. And the LoadGate
cannot close it, because the gate is consulted only at mediator new-root
ingresses (`transaction_mediator.py:359,501`) and **a frame under construction
has no mediator yet** - the admission authority is owned by the very thing being
created. A scope claim on `frame:<name>` expresses the INTENT correctly, but it
can only be enforced by an authority that exists BEFORE frames do. That is
precisely the AethericMediator's stated reason to exist (owner constraints 3 and
4: constructed immediately after Aether, and must not depend on Aether). So this
is not "inexpressible" - it is expressible only in the plane, never in anything
that lives inside a frame. Recording it loudly as the task asks.

**CONFLICT (secondary) - all-or-nothing teardown is not compensation.**
`_teardown_built` (`restore_engine.py:2647-2669`) pops the built stack
newest-first and swallows every per-unit cleanup exception by contract ("the
original stage error is the signal; teardown noise must not mask it"). Two
consequences a claim-based plane cannot express:
1. A partial teardown leaves live objects behind with **no record** of which
   ones failed to clean - the swallowed exception is discarded, not collected.
   Scope claims can serialise the next mutation; they cannot tell it that the
   world it is claiming is dirty.
2. The teardown order is *global build order reversed*, which is stronger than
   any per-key claim ordering. Releasing N scope claims in reverse acquisition
   order is not the same guarantee as tearing down N built objects in reverse
   construction order, because claims and objects are not 1:1 (one
   `crystallizer:load:world` claim covers thousands of built units).

**NOT a conflict, but worth stating:** the graft lane's per-member transactions
(Q2(b)) are perfectly expressible as claims - `spellbook:<id>` + `conduit:<id>`
held across the whole `run()` instead of per member. It is unprotected today,
but nothing about it resists the plane.

---

### Answers-to-criteria checklist
- [x] All six questions answered with `path:line` evidence.
- [x] Scope keys and modes are concrete strings, not descriptions.
- [x] Inexpressible protection recorded as CONFLICT notes (two of them).
- [x] No code changed - read-only throughout.
- [x] No design proposed; where a fix is obvious it is named as a finding, not a plan.

### Reads performed
`crystal_loader_system/crystal_loader_system.py` (whole),
`crystal_loader_system/restore_engine.py` (targeted: locks, drivers, stages,
teardown, posture, shortfalls), `crystal_loader_system/load_admission.py`
(threading contract), `crystal_loader_system/graft_runner.py` (threading +
`run` contract), `crystallizer.py` (class contract, `activate`, `deactivate`,
`graft_index`, emit family), `persistence/persistence_system.py` (lock audit of
six verbs), `asset_management/asset_management_system.py` (threading contract),
`configuration/crystallizer_configuration.py` (schema + defaults),
`utilities/synchronization/load_gate.py` (control model),
`aether/aether.py` (`acquire_load_authority`, `release_load_authority`,
`enroll_load_worker`, `_ensure_frame`), and the epic's Problem / Owner
Constraints sections.

## Notes
- (append findings here as they land, per the Ticket Microcycle)

## Context / Handoff Summary
Read-only survey of Crystallizer feeding the AethericMediator wiring story. Answer the
six questions with evidence; propose scope keys and modes; flag anything that
cannot be expressed as a claim.
