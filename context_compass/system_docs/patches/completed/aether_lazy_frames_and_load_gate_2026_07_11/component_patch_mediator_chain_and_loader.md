# Component Patch: mediator chain threading + loader integration

- Patch ID: aether_lazy_frames_and_load_gate_2026_07_11

## DevOpsManager / ChangeControlManager / TransactionMediator
Before: no knowledge of loads; root starts admit purely on scope claims.
After: additive `load_gate` ctor kwarg (default None) threaded frame ->
DevOpsManager -> CCM -> TransactionMediator. Mediator stores the borrowed
gate; at NEW-ROOT starts only (begin_transaction after the join/existing
branches; begin_frame new-root branch) it calls
`wait_for_passage(timeout=_max_transaction_wait_time_in_seconds)`:
- gate open -> passes untouched;
- gate held by CURRENT thread (the loader) -> passes (per-verb replay
  transactions keep maintaining registry truth inside the load);
- gate held by another thread -> waits on the gate condition, RuntimeError
  on timeout naming the holder label (teach-grade).
Nested joins and staged-metadata extension never consult the gate.

## CrystalLoaderSystem / Crystallizer
Before: loader constructed over the record only; loads unguarded.
After: `CrystalLoaderSystem(persistence_system, aether=None)`;
load_checkpoint and restore_formation_record wrap the plan+execute span in
`aether.acquire_load_authority(label)` / `release_load_authority()`
(try/finally; label = source_label). Crystallizer passes `self._aether`.
None aether = ungated (existing unit suites construct loaders bare).

## State/Failure Deltas
- New refusal: root-start timeout while a load holds the system (names the
  load label). New refusal: second concurrent load (gate already held).
- Load failure releases the gate in finally; engine teardown semantics
  unchanged.

## Validation Expectations
- Unit (gate): acquire/release/holder-passthrough/second-load refusal/
  waiter timeout naming the label; mediator gated vs ungated construction.
- Unit (lazy): import-time zero frames; Spellbook() births default;
  named book births only its name; recreate-after-clean contract.
- Integration: existing restore round-trips green with the gate active
  (loader thread passthrough proves itself); one new test - a competing
  bind from another thread waits/times out during a held load.
- Owner runs 3.14t; "Not run." until then.
