# Component Patch: crystal_loader_system (S4 - the unfold)

## Metadata
- Patch ID: crystallizer_decomposition_2026_07_09
- Story: STORY-2026-07-09-crystal-loader-system-boot-mediator
- Status: active
- Created: 2026-07-10T05:20:00Z
- Author: melder_0

## Before
Loading has no owner. PersistenceSystem.load_checkpoint (:1046) assembles the
detached chain under the ledger lock then runs the engine; the formation
engine leg (restore_formation_record) also sits on the ledger; the engine's
preflight verdict gates nothing by default (bootstrap's with_preflight_gate
is an opt-in that re-checks AFTER restore); nobody owns durable load state
(last report/shortfalls/identity map die with the caller); restore_engine.py
and CrystallizerBootstrap live outside any subsystem.

## After
NEW `crystallizer/crystal_loader_system/` package:
- restore_engine.py MOVES unchanged EXCEPT one addition: ctor knob
  `refuse_on_blockers: bool = False`; after `_fold_chain` + `_run_preflight`
  and BEFORE any stage replay, a "blockers" verdict raises a teach-grade
  RuntimeError naming the blocker rows (nothing is built yet, so no teardown
  is needed). VERDICT LAW lands at the only seam that owns authoritative
  folded truth - no fold duplication, no mediator drift.
- load_plan.py - LoadPlan (Cleanable value carrier): scope
  ("world"|"conduit"|"frame"), profile_name, checkpoint_ids/formation_name,
  window_count, per-kind key counts (from the chain/record journals),
  detached chain/window payloads for the engine. Inspectable BEFORE anything
  activates; describe() is counts+identity, not payload dumps.
- boot_mediator.py - BootMediator (small, per owner): builds plans
  (plan_checkpoint_load via the record's NEW detach_profile_chain;
  plan_formation_load from a loaded formation record - synthetic window
  minting moves here from the ledger), executes them (engine with
  refuse_on_blockers=True ALWAYS - admission is the standard path), and
  ADJUDICATES the report's preflight per scope: conduit/frame-scoped loads
  reclassify frame_posture warnings to "expected_for_scope" info in an
  additive "admission" view {"scope", "verdict", "reclassified": [...]} -
  the S1 flip-back criterion. Raw preflight rows stay untouched (bundle
  truth is never rewritten).
- crystal_loader_system.py - CrystalLoaderSystem (the owner Crystallizer
  talks to): borrows the record, owns the mediator, and REMEMBERS - durable
  load state (detached last-load payload + admission view), exposed via
  describe_last_load(). Verbs: load_checkpoint(id),
  restore_formation_record(record), describe_last_load().
- bootstrap_loader.py - CrystallizerBootstrap MOVES here; with_preflight_gate
  becomes an accepted no-op knob (docstring: absorbed - blocker refusal is
  standard admission now); its post-restore verdict re-check is deleted.

PersistenceSystem (ledger) deltas:
- ADDED: detach_profile_chain(checkpoint_id) -> {"profile_name",
  "checkpoint_ids", "chain"} (the :1084-1098 under-lock assembly, verbatim).
- REMOVED: load_checkpoint, restore_formation_record (engine legs move to
  the loader; the ledger never constructs engines again).

Crystallizer deltas (facade surface byte-compatible; payloads additive-only):
- Third child: `_crystal_loader_system = CrystalLoaderSystem(record)`
  (cleanup: loader first, then assets, then record - borrowers before owner).
- load_checkpoint facade -> loader (returns the report payload + additive
  "admission" key). restore_formation facade -> asset load_formation_record
  + loader.restore_formation_record (same additive enrichment).

## Interface Deltas
- Crystallizer public surface: zero signature changes; report payloads gain
  the additive "admission" key.
- Module paths: restore_engine + bootstrap move (their test import sites
  re-point; crystallizer_bootstrap.py top-level module is DELETED, no shim -
  rollout law).
- RestoreEngine ctor: +refuse_on_blockers (default False keeps unit-suite
  behavior byte-identical).

## State / Failure Deltas
- NEW failure: admission refusal - RuntimeError before replay listing
  blocker rows (teach-grade; names strategies/kinds/keys). All-or-nothing
  teardown semantics unchanged for failures DURING replay.
- Durable load state exists for the first time (loader-owned, detached).

## Dependency / Ordering
- Edges: loader -> record (detach/feedstock), loader -> crystal_analysis
  (engine's preflight import moves with it), loader -> engine (owned).
  Assets feed the loader THROUGH THE FACADE (record loading), so no
  loader -> assets edge exists. The record calls nobody (unchanged).

## Validation Expectations
- Sentinel integration green (all round trips now traverse loader admission).
- S1 flip-back: the formation test additionally asserts the admission view
  verdict is clean-for-scope while raw preflight stays "warnings".
- NEW unit: admission refusal on a blocker bundle; LoadPlan counts; scope
  adjudication reclassification; durable last-load state.
- py_compile/ast floor; "Not run." until owner runs.
