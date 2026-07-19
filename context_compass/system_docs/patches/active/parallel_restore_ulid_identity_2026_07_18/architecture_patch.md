# Architecture Patch: parallel_restore_ulid_identity_2026_07_18

- Status: active (entry-gate artifact)
- Owner ruling: Option A accepted 2026-07-18 - identity = ULID, order = journal sequence,
  parallel replay via PhaseScheduler behind a cohort-aware LoadGate.
- Tickets: EPIC-2026-07-18-parallel-restore-ulid-identity (S1-S4).

## Objective
Replace the single-threaded checkpoint replay with per-entity parallel execution inside the
existing canon stage order, without changing identity semantics, record compatibility, the
all-or-nothing law, or foreign-thread exclusion during loads.

## Non-Goals
- No monotonic-ULID variant; ULIDs stay opaque identity (ulid_factory.py:18-20).
- No new order-of-operations source: the journal sequence remains the only order truth
  (persistence_crystal.py:59, 133-155).
- No head-stage parallelism (aether config / crystallizer policy / MR / nexus are
  single-root; zero win, needless risk).
- No emit batching in this program (measure first; separate owner decision).

## Changed Components
1. Conduit link verbs + conduit crystal (S1): links become identity-bearing recorded units.
2. PhaseScheduler construction seam (S2): explicit worker/timeout values beside the
   SpellbookConfiguration path; instances no longer implicitly spellbook-scoped.
3. LoadGate + Aether load-authority surface (S3): span authority extends from one thread to
   an enrolled cohort (loading thread + restore workers). Foreign semantics unchanged.
4. RestoreEngine + LoadAdmission + CrystalLoaderSystem (S4, amended by owner ruling
   2026-07-18): a RestorePlanGraph (DirectedAcyclicWorkGraph over per-entity nodes with
   recorded dependency edges) is built after fold, flattened to topological levels, and
   loaded into the scheduler one phase per level. Per-entity units; thread-safe report +
   built stack. Entity placement (including nexus) is graph-derived, not slot-coded.

## Invariants (unchanged, load-bearing)
- Never-rehydrate-ULIDs: recorded ids live only in the identity map
  (restore_engine.py:32-34); rebuilt world mints fresh ids.
- All-or-nothing: any stage/phase failure tears down every built unit in reverse global
  build order, then raises with the cause chained (restore_engine.py:493-494, 570-577).
- The recorded dependency partial order is the execution truth. The canon stage order
  (restore_engine.py:549-569) remains the PARITY BASELINE: on today's record shapes the
  graph levels must reproduce its outcomes exactly. Barriers between levels are MANDATORY;
  parallelism exists only within a level; a recorded-edge cycle refuses at admission.
- Foreign exclusion during load: non-cohort threads park at the LoadGate for the whole
  span, bounded by the mediator wait bound (transaction_mediator.py:136-144).
- Emit safety: one PersistenceSystem RLock serializes every record/remove verb
  (persistence_system.py:44-46, 87); journal sequences stay atomic under parallel builders.
- Per-book interior order is sequential: config freeze -> active binds in bind_order ->
  conjure -> staged binds -> selections (restore_engine.py:1231-1313). A book is ONE unit.

## Interface Deltas (all additive)
- conduit crystal payload: + links: [{"link_id": ULID, "target_conduit_id": id}]
  (legacy link_targets list still folds; no migration).
- PersistenceSystem: + link row record/remove verbs (tombstone by link_id).
- PhaseScheduler.__init__: + keyword-only worker_count / barrier_timeout_ms overrides.
- CrystallizerConfiguration: + restore_scheduler_workers,
  restore_scheduler_barrier_timeout_milliseconds.
- Aether load authority: + enroll_load_worker / withdraw_load_worker span verbs.
- Public loader verbs (load_checkpoint / restore_formation_record): UNCHANGED shape.

## Migration Order
S1 (record shape + replay units) -> S2 (scheduler seam) -> S3 (cohort gate, double-gated by
its code_description patch) -> S4 (compiler + parallel engine, double-gated likewise).
Each story lands independently green; the engine stays sequential until S4 flips it behind
parity proof.

## Rollback
- S1: additive record fields - stop writing rows; legacy fold path remains.
- S2: overrides unused -> config path identical to today.
- S3: cohort of one == current single-thread law; revert enrollment call sites.
- S4: keep sequential stage driver as the fallback lane (config-selectable) until the
  owner retires it; rollback = select sequential driver.

## Ticket Coverage Matrix
| Delta | Story | Patch doc |
|---|---|---|
| Link identity + journal rows | S1 | component_patch_link_identity_persistence.md |
| Scheduler construction seam | S2 | component_patch_phase_scheduler_seam.md |
| Cohort LoadGate | S3 | component_patch_load_gate_cohort.md (+ code_description at start) |
| Phase compiler + parallel engine | S4 | component_patch_restore_engine_parallel.md (+ code_description at start) |

## Validation Expectations
- Parity: parallel restore of a chain == sequential restore outcomes (built counts,
  shortfalls, identity coverage). Chaos: mid-phase failure -> full teardown. Adversarial
  gate suite: foreign threads never pass a cohort span. Owner-run 3.14t; agent reports
  "Not run." until then.
