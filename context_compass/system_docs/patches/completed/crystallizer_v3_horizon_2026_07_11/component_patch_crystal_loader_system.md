# Component Patch: crystal_loader_system (S1 load-scope maturity)

- Patch ID: crystallizer_v3_horizon_2026_07_11
- Story: STORY-2026-07-11-load-scope-maturity

## Before
- plan_formation_load(record) derives scope and mints the canonical-order
  window verbatim; no notion of a target frame or the live world's state.
- execute_plan runs the engine (refuse_on_blockers=True) and adjudicates
  scope over the BUNDLE preflight only; the live world is never consulted.
- Engine: frames ensure+posture (conflict keeps live truth silently at the
  frame level), conjure applies the recorded conduit name unconditionally
  (cloud collision = stage failure = full teardown), create_cluster raises
  ValueError on an existing name (stage failure = full teardown).

## After
- LoadPlan carries target_frame_name/skip_existing/host_findings (additive;
  defaults keep old construction sites valid). describe() reports them.
- plan_formation_load: when target_frame_name is set, the DETACHED window
  rewrites frame identity before planning - frame twin keys, spellbook
  payloads' frame_name, cluster payloads' frame_name, and (frame-scope) the
  scope record. Payload dicts are copied before mutation; the stored
  formation record is never touched.
- NEW _host_preflight(plan), plan-time, read-only over the live world:
  - frame row: target/recorded frame missing -> info "frame_will_be_created";
    existing frame with frozen conflicting posture -> warning
    "host_frame_posture_conflict" (frame keeps live truth; recorded posture
    will not apply).
  - named-conduit row: recorded conduit_name present AND
    cloud.has_conduit_name(name) -> BLOCKER "host_conduit_name_taken"
    (skip_existing=True: severity becomes "skipped_existing").
  - cluster row: recorded cluster_name in cloud clusters (documented
    deliberate private seam, same class as the engine's _conduit_cloud
    access; follow-up public has_cluster noted) -> BLOCKER
    "host_cluster_name_taken" (skip_existing=True: "skipped_existing").
- execute_plan: host blockers refuse BEFORE engine construction with the
  same teach-grade row format as engine admission; otherwise the engine runs
  with skip_existing threaded, and the admission view gains the additive
  "host" section {"findings", "verdict"}.
- Engine skip semantics (skip_existing=True only):
  - _conjure_for_book: live name collision -> conjure(name=None) + shortfall
    "conduit_name_taken_built_unnamed". Identity map still binds the
    recorded conduit ULID to the live conduit, so links/contracts replay
    unchanged.
  - _replay_clusters: existing cluster name -> skip create_cluster, still
    add members + shortfall "cluster_existed_members_joined".

## State/Failure Deltas
- New refusal class (host admission) raises RuntimeError before any build:
  nothing to tear down, report marked failed("host_admission").
- No existing failure path changes shape.

## Dependency/Ordering
- Host preflight runs at plan/execute seam (mediator); bundle preflight
  stays inside the engine post-fold. Order: host -> fold -> bundle -> replay.

## Validation Expectations
- Unit: plan retarget rewrite coverage (frame/book/cluster/scope rows);
  host-finding severities per skip_existing; refusal message format; engine
  name-drop + cluster-reuse lanes; LoadPlan additive describe.
- Integration (sentinel additions): conduit formation into a live world -
  refused by default on collision, loads with skip_existing=True (unnamed
  conduit + reused cluster + shortfalls), retargeted frame load lands on the
  new frame name.
- Owner runs 3.14t; agent reports "Not run." until then.
