# Architecture Patch: persistence_loop_load_order_r11_2026_07_12

## Metadata
- Patch ID: persistence_loop_load_order_r11_2026_07_12
- Status: active
- Owner ruling: 2026-07-12 - "implement your things you suggested" (mutation_0
  owns the persistence-loop epic). Companion slice to
  persistence_loop_m1_m5_residue_2026_07_12.
- Ticket: tickets/epics/2026-07-02_agent_object_persistence_loop_epic.md

## Objective
Close the two remaining proven residues: (1) the shared user-world rebuild lane
now unfolds in the crystal's recorded topological `module_load_order` (dot-depth
parents-first remains the fallback for pre-load-order payloads); (2) R11
reverse-edge-aware unseed - a park no longer unpublishes a synthetic module
that a live PUBLISHED synthetic dependent still relies on.

## Non-Goals
- M8 callsign/version-store wiring (awaits owner alias-semantics ruling).
- Physical-dependent enumeration at runtime (impossible by design; recorded
  physical->synthetic edges stay governed by the hot-swap law).

## Changed Components
- crystal_loader_system/user_world_rebuild.py (ordering seam only).
- crystallizer.py `record_spell_activity` park lane (R11 guard).
- synthetic_module.py: +`has_live_synthetic_dependents` registry classmethod
  (read-only, lock-disciplined).

## Invariants (unchanged)
- Live-file-wins, never-mask-sys.modules, honest shortfalls, all-or-nothing
  engine semantics, R-A covenant, knob gating (`remove_inactive_synthmodules`).

## Invariants (new)
- Recorded load order wins over dot-depth whenever the payload carries it;
  names unknown to the order still rebuild (appended, dot-depth-sorted).
- Only PUBLISHED dependents keep a parked module resident; the keep-resident
  decision is logged (INFO) with the R11 law named.

## Interface Deltas
- `SyntheticModule.has_live_synthetic_dependents(module_name) -> bool` (new
  public classmethod).
- No signature changes anywhere else.

## Migration Order
1. synthetic_module.py classmethod. 2. crystallizer.py guard.
3. user_world_rebuild.py ordering. 4. Tests.

## Rollback
Revert the three files + test file; no record/schema change.

## Ticket Coverage Matrix
| Delta | Epic item |
| --- | --- |
| rebuild ordering | M3 residue ("load_order-driven loader depth") |
| park guard + classmethod | R11 / M6 full slice |
