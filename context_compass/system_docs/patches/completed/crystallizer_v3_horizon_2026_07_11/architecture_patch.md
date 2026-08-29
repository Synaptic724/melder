# Architecture Patch: crystallizer V3 horizon - S1 load-scope maturity

- Patch ID: crystallizer_v3_horizon_2026_07_11
- Story: STORY-2026-07-11-load-scope-maturity
- Status: active (S1 slice)
- Created: 2026-07-11T11:40:00Z

## Objective
Formations become composition units: a stored conduit/frame formation loads
INTO a live world through the existing mediated admission pipeline, with host
preconditions verdict-gated at plan time, optional frame retargeting, and an
explicit skip_existing collision policy. The dead compose_* placeholder debt
retires.

## Non-goals
- No checkpoint-load semantic changes (world loads stay world-shaped).
- No bundle-analyzer charter change (it stays bundle-only; host truth lives
  in the mediator's admission plane).
- No MR work of any kind (other agent's lane).
- No facade signature breaks (additive kwargs only).

## Changed Components
1. crystal_loader_system (LoadAdmission - renamed from BootMediator
   2026-07-11 by owner ruling, executed pre-implementation - LoadPlan,
   CrystalLoaderSystem, RestoreEngine) - host preflight, retargeting,
   skip semantics.
2. persistence record (PersistenceProfile) - compose_* placeholder deletion.
3. Crystallizer facade - additive restore_formation kwargs.

## Invariants (unchanged and load-bearing)
- Verdict law: blockers refuse BEFORE anything is built; the engine's folded
  preflight stays the only owner of folded truth. Host blockers refuse even
  earlier (before engine construction) - a strictly tighter gate.
- Adjudication stays a VIEW: raw findings (bundle or host) are never
  rewritten; scope/host reinterpretation rides the additive admission view.
- Never-rehydrate-ULIDs, all-or-nothing teardown, re-emission, shortfall
  honesty: untouched.
- Names are never resolution keys during replay (links/contracts/clusters
  resolve via the identity map) - the ground that makes name-drop safe.

## Interface Deltas (all additive)
- Crystallizer.restore_formation(formation_name, profile_name=None, *,
  target_frame_name: Optional[str] = None, skip_existing: bool = False).
- CrystalLoaderSystem.restore_formation_record(record, *, target_frame_name
  =None, skip_existing=False).
- LoadAdmission.plan_formation_load(record, *, target_frame_name=None,
  skip_existing=False); NEW LoadAdmission._host_preflight(plan).
- LoadPlan(..., target_frame_name=None, skip_existing=False) + carried
  host_findings; describe() gains the new fields.
- RestoreEngine(..., skip_existing: bool = False).
- Admission payload gains additive "host" key:
  {"findings": [...], "verdict": "clean"|"warnings"|"blockers"|"skipped"}.
- REMOVED (ruled, zero callers): PersistenceProfile.compose_frame_subtree,
  compose_conduit_subtree (capability shipped as capture_formation_slice).

## Migration Order
1. LoadPlan additive slots -> 2. mediator retarget + host preflight ->
3. engine skip semantics -> 4. loader/facade threading -> 5. compose_*
   deletion -> 6. tests.

## Rollback
Every delta is additive or dead-code deletion; reverting the patch commits
restores prior behavior byte-identically (defaults preserve all existing
call shapes).

## Ticket Coverage
- tickets/stories/2026-07-11_load_scope_maturity_story.md (T1 evidence note
  carries the full seam map).
