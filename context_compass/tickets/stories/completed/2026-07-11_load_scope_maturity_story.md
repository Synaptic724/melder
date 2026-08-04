# Story: load-scope maturity (S1 - formations compose into live worlds)

## Metadata
- Story ID: STORY-2026-07-11-load-scope-maturity
- Parent Epic: EPIC-2026-07-11-crystallizer-v3-horizon-iteration
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-11T11:09:27Z
- Updated: 2026-07-11T11:09:27Z

## Problem / Opportunity
Formation loads are world-shaped: the mediator mints a synthetic window and the
engine replays it as if booting a world. Loading a conduit formation INTO an
already-live world has no host-precondition checks, no retargeting, and no
collision policy - and the record still carries two NotImplementedError
compose placeholders whose fate is unruled. This story makes formations real
composition units.

## Ticket Contract
- ENTRY_GATE: epic staged; owner directive 2026-07-11.
- EXECUTION_BOUNDARY: crystal_loader_system/ (mediator, plan, loader, engine
  seams), crystal_analysis/preflight/ (new host-precondition strategies),
  persistence/persistence_profile.py + persistence_system.py (compose_*
  ruling + any subtree-capture verb work), crystallizer.py (additive facade
  params only), NEW unit tests + sentinel additions. Nothing else.
- DEPENDENCIES: none (first tranche).
- EXIT_GATE: patch docs exist + linked before code; reroute/inventory
  checklist fully ticked; owner-run sentinel green.
- FAILURE_ESCALATION: fold/stage semantic deltas -> CONFLICT + stop.

## Design (PINNED 2026-07-11 from source truth; patch docs carry the contract)
1. FACADE (additive kwargs only): Crystallizer.restore_formation gains
   `target_frame_name: Optional[str] = None` and `skip_existing: bool =
   False`; threads asset-load -> loader unchanged otherwise.
2. LOADER: restore_formation_record threads both kwargs to the mediator.
3. LOADADMISSION (renamed from BootMediator 2026-07-11, owner ruling - the
   object runs a linear admission pipeline, it mediates nothing; rename
   EXECUTED pre-implementation, full sweep in the FACT note below):
   plan_formation_load performs RETARGETING by rewriting frame
   identities inside the DETACHED window only (frame twin keys, book
   payloads' frame_name, cluster payloads' frame_name, scope record for
   frame-scope loads); LoadPlan gains additive `target_frame_name`,
   `skip_existing`, `host_findings` slots. NEW plan-time _host_preflight
   (read-only over the live world; the bundle analyzer's charter stays
   bundle-only): frame-exists/posture-conflict -> warning; named-conduit
   collision (cloud.has_conduit_name) -> BLOCKER; cluster-name collision
   (cloud._conduit_clusters read via the engine's documented deliberate
   private seam; follow-up public has_cluster noted) -> BLOCKER.
   skip_existing=True downgrades the two collision families to
   "skipped_existing" rows. execute_plan refuses host blockers BEFORE
   engine construction (same teach-grade format) and merges host findings
   into the admission view under an additive "host" key.
4. ENGINE (additive ctor kwarg `skip_existing: bool = False`):
   _conjure_for_book drops the recorded name on live collision (conjure
   name=None + shortfall "conduit_name_taken_built_unnamed");
   _replay_clusters reuses an existing cluster instead of create_cluster
   (+shortfall "cluster_existed_members_joined"). SAFE because links and
   contracts replay via the identity map (_live_conduits keyed by recorded
   ULID), never by name - name-drop cannot break formation integrity.
5. compose_* RULING: DELETE both placeholders. Zero code callers repo-wide;
   the promised composer shipped as PersistenceProfile.
   capture_formation_slice (consumed by capture_formation_record). NOTE
   comment at the deletion site records the absorption.

## Tasks
- [x] T1: SOURCE INVESTIGATION complete (see FACT note). Loader package,
      engine stages, analyzer/strategy shape, record verbs, facade seam,
      cloud collision surfaces all evidenced.
- [x] T2: patch docs authored + linked (see Artifact Links). Consumption
      mapping: architecture_patch interface-deltas -> T3 steps 1-5 (LoadPlan
      slots, mediator retarget+host preflight, engine skip lanes, threading,
      compose_* deletion) -> component-patch Validation Expectations -> T4
      test rows. DONE 11:40Z.
- [x] T3: implementation per patch contract. DONE 2026-07-11T15:10Z.
- [x] T4: tests (unit + sentinel additions), gates, owner run request.
      DONE 2026-07-11T15:10Z (4 new unit tests; owner run requested).

## Acceptance Criteria
- A conduit/frame formation loads into a LIVE world through the mediated
  admission pipeline with: host preconditions verdict-gated in preflight,
  optional retargeting, and explicit skip_existing collision policy
  (refuse-by-default).
- compose_frame_subtree/compose_conduit_subtree either implemented as the
  record-side subtree capture the loads consume, or deleted with the ruling
  recorded - no NotImplementedError placeholders remain.
- Facade surface byte-compatible; additive params/keys only.

## Artifact Links (Optional)
- system_docs/patches/active/crystallizer_v3_horizon_2026_07_11/architecture_patch.md
- system_docs/patches/active/crystallizer_v3_horizon_2026_07_11/component_patch_crystal_loader_system.md
- system_docs/patches/active/crystallizer_v3_horizon_2026_07_11/component_patch_record_and_facade.md

## Applicable Anti-Patterns
- [x] No fold-logic duplication outside the engine (host preflight reads
      the WINDOW payloads + live registries; folding stays engine-only).
- [x] Raw preflight findings never rewritten (host findings are a separate
      additive "host" key; engine preflight untouched).
- [x] No implementation from UNKNOWN; design pins after T1 with evidence.
- [x] "Not run." until the owner runs.

## Noting Behavior
- Story notes: seam evidence, design pins, gate results.

## Notes
- DATETIME: 2026-07-11T11:35:00Z
  TYPE: FACT
  CLAIM: T1 complete; every design-relevant seam evidenced from source.
    (1) Formation loads are world-shaped: the engine ensures+postures frames
    (bind_frame_configuration is idempotent-matching / conflict-keeps-live),
    builds NEW books/conduits with fresh identities, and links/contracts/
    clusters resolve through _live_conduits keyed by RECORDED ULID - names
    are never resolution keys, so name-drop on collision is integrity-safe.
    (2) Real host collisions are name-anchored only: conjure(name=...) into
    the frame cloud, and create_cluster raising ValueError on duplicates.
    Public surfaces: cloud.has_conduit_name / find_conduit_id_by_name;
    cluster existence has NO public check (engine already documents the
    deliberate private _conduit_cloud seam with a public-accessor follow-up).
    (3) The bundle analyzer charter is explicitly bundle-only ("touches no
    live runtime objects"), so host preconditions belong to the mediator's
    admission plane, merged into the additive admission view.
    (4) compose_frame_subtree/compose_conduit_subtree have ZERO code callers
    (grep repo-wide: only ticket/artifact prose); their promised capability
    shipped as capture_formation_slice. DELETE ruling is safe.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/boot_mediator.py:102-174
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:988-1084
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1170-1232
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1428-1510
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py:34-65
  - src/melder/crystallizer/persistence/persistence_system.py:634-709
  - src/melder/crystallizer/persistence/persistence_profile.py:788-832
  - src/melder/aether/aetheric_frame/conduit_cloud.py:364-417
  - src/melder/crystallizer/crystallizer.py:1475-1512
  IMPACT: Design pinned (section above) with no UNKNOWNs; patch authoring
    can proceed without further discovery.
  NEXT: T2 patch docs under
    system_docs/patches/active/crystallizer_v3_horizon_2026_07_11/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T12:05:00Z
  TYPE: FACT
  CLAIM: RENAME EXECUTED (owner ruling): BootMediator -> LoadAdmission,
    boot_mediator.py -> load_admission.py. Full checklist swept: class +
    self-ref + docstrings (load_admission.py), loader import/slot/verbs/
    docstrings (crystal_loader_system.py: _boot_mediator ->
    _load_admission), load_plan + restore_engine docstring mentions,
    persistence_system NOTE comment, unit suite (import + 5 usages +
    module docstring), integration comment (:770 region), both C-docs
    (5 + 4 line fixes incl. "mediated unfold" -> "admission-gated
    unfold"), active architecture patch, graph node id/label/file/role +
    3 edge endpoints + 1 edge why (readable regenerated: JSON-valid,
    520/965, max line 220). Historical surfaces (patches/completed,
    closed tickets, board anchors, prior notes) left untouched by
    append-only law; provenance mentions ("formerly BootMediator")
    retained deliberately. Compile floor: 6/7 files ast-parse OK via
    bash; crystal_loader_system.py Not run (replica rot - grown file
    read at stale length; real disk verified complete via file-tool
    read of the full tail). Tests: Not run (owner runs 3.14t).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:1-30
  - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py:185-208
  - tests/unit/melder/crystallizer/crystal_loader_system/test_crystal_loader_system.py:1-15
  IMPACT: The TransactionMediator name collision is dead; the admission
    vocabulary is now uniform across code, docs, and graph. S1
    implementation proceeds on the renamed surface.
  NEXT: T3 implementation - preceded by the DevOps transaction-plane
    integration design the owner directed ("generic request from the
    actual transaction mediator"); design presented for sign-off before
    any dev_ops edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T12:30:00Z
  TYPE: FACT
  CLAIM: DevOps transaction plane understood from SOURCE (owner-directed
    study; link family as the exemplar). Mechanics: (1) callers need a
    DevopsIdentity that DECLARES the transaction name
    (identity.supports_transaction hard-gates begin_transaction); (2)
    start_transaction -> strategy.build_start_plan resolves participants
    REGISTRY-FIRST (get_identity / get_spellbook_for_conduit), emits scope
    keys + claim-mode overrides (link: conduits/wards EXCLUSIVE, owning
    spellbooks INTENT) + capabilities; (3) begin_transaction builds the
    immutable request -> _admit_with_scope_wait retries on embargo release
    in 1s slices, timeout names blocking scopes + holders; (4) same-thread
    nesting JOINS the root session and can EXTEND staged metadata +
    embargoes; (5) only the outermost frame finalizes: commit pipeline ->
    strategy commit delta (registry mirrors updated WHILE scopes are held)
    -> orchestrator release; abort mirrors.
    BOOTSTRAP CONFLICT CONFIRMED (owner's order-of-operations concern is
    structurally real): the ENTIRE plane is frame-local (CCM/mediator/
    registry are built in AethericFrame.__init__). A world load into a
    fresh Aether has NO frame -> no mediator exists to admit anything;
    frames are BORN mid-load (engine stage 5 _ensure_frame). Per-verb
    self-admissions work today only because each plane exists by the time
    its verbs run. A whole-load root claim CANNOT be taken on a plane that
    does not exist yet; and a "load" strategy cannot plan registry-first
    because the units it would claim do not exist pre-replay.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:328-478
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:900-971
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1101-1165
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py:53-164
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1077-1084
  IMPACT: The frame-scoped claim design CANNOT cover world loads; the
    owner's "give the loading thread all rights" instinct maps to an
    Aether-level load gate (close-and-drain, RiftGate/CreationGate
    precedent) that exists BEFORE any frame and that every frame-local
    mediator consults on root starts - loading thread passes free so its
    per-verb transactions keep maintaining registry truth.
  NEXT: present the LoadGate design for owner sign-off; no dev_ops edits
    until ruled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T12:45:00Z
  TYPE: FACT
  CLAIM: CORRECTION to the 12:30Z bootstrap claim (owner question "what
    initiates the first aetheric_frame" answered from source): the DEFAULT
    frame is created EAGERLY by Aether.__init__ itself (aether.py:121-123)
    and Aether() runs at package import (:126-127 comment), so the default
    frame's transaction plane ALWAYS exists before any load can run. The
    12:30Z note's "no frame -> no mediator exists" was an overclaim. The
    REAL gap: NAMED frames (and their planes) are lazily created via
    _ensure_frame - callers: Spellbook.__init__ (spellbook.py:229),
    Spellbook:5113, NexusFrameManager:966, FrameDescriptorManager:188/:259,
    and the engine's frames/cluster stages - so a world load's named-frame
    planes are born mid-load and cannot be claimed upfront; claims never
    cross planes. LoadGate-on-Aether conclusion UNCHANGED and strengthened:
    Aether constructs the default frame, so the gate predates every frame
    unconditionally. Bonus symmetry: Crystallizer is constructed BEFORE the
    default frame (aether.py:109) - the recorder predates frames exactly as
    the gate would.
  EVIDENCE:
  - src/melder/aether/aether.py:105-130
  - src/melder/aether/aether.py:648-690
  - src/melder/aether/spellbook/spellbook.py:229-229
  IMPACT: Design ask to the owner is now precisely scoped: one Aether-hosted
    LoadGate (close-and-drain) + one root-start check in TransactionMediator;
    no strategy family, no per-family claim rows needed.
  NEXT: owner sign-off on the LoadGate; then patch-doc the dev_ops slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T14:00:00Z
  TYPE: FACT
  CLAIM: LoadGate SIGNED OFF and IMPLEMENTED (owner: "yeah lets do that go
    ahead and implement this"; patch
    aether_lazy_frames_and_load_gate_2026_07_11 authored first, shared with
    the lazy-frames task as one tranche). Shipped: (1) NEW
    utilities/synchronization/load_gate.py - LoadGate (Cleanable): exclusive
    acquire(label)/release(), wait_for_passage(timeout) with holder-thread
    passthrough + teach-grade timeout naming the load; cleanup uses
    documented None TOMBSTONES so parked waiters exit cleanly (terminal
    open). (2) Aether hosts _load_gate (constructed before any frame can
    exist) + acquire_load_authority(label, drain_timeout)/
    release_load_authority() with re-snapshotting drain over every live
    frame's mediator active_session_count (gate released on drain-timeout
    failure). (3) Additive load_gate kwarg threaded AethericFrame ->
    DevOpsManager -> ChangeControlManager -> TransactionMediator (default
    None = ungated; direct-ctor test suites unaffected); mediator slot
    "_load_gate", wait_for_passage at BOTH new-root ingresses
    (begin_transaction pre-build_request - covers start_transaction and
    _start_strategy_transaction which funnel through it - and begin_frame
    pre-lock); joins never gate. (4)
    CrystalLoaderSystem(persistence_system, aether=None) wraps both load
    verbs in acquire/release try/finally spans (labels
    "checkpoint_load:<id>" / "formation_load"); Crystallizer passes its
    aether. (5) NEW unit suite
    tests/unit/melder/utilities/synchronization/test_load_gate.py (10
    tests: open/holder/label refusal/one-load-at-a-time/release discipline/
    hot-path noop/holder passthrough/park-and-resume/timeout-names-label/
    teardown wakes waiters).
  EVIDENCE:
  - src/melder/utilities/synchronization/load_gate.py:1-278
  - src/melder/aether/aether.py:766-871 (authority verbs)
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:320-334
  - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py:139-160
  IMPACT: "if there is a load happening we give all rights to the thread
    thats executing that load" is now real: one gate above all frame
    planes, bootstrap-proof under lazy frames (fresh systems load from
    zero frames).
  TESTS: Not run (sandbox cannot import melder; bash replica rot on grown
    files - real disk verified via file-tool). Owner full-tree 3.14t run
    pending; integration restore round-trips double as the passthrough
    proof.
  NEXT: owner run; then T3/T4 (retarget + host preflight + skip lanes)
    continue in this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T15:10:00Z
  TYPE: FACT
  CLAIM: T3/T4 IMPLEMENTED per the pinned patch contract. (1) LoadPlan:
    additive target_frame_name/skip_existing slots + properties + describe
    keys. (2) LoadAdmission: additive aether borrow (None = bare-record,
    host preflight empty); plan_formation_load(..., target_frame_name,
    skip_existing) with _retarget_payloads (copy-on-write: frame twin
    re-key, journal frame rows, book/cluster frame_name edges; multi-frame
    windows REFUSE; caller record never mutated); _preflight_host (frame
    registry read NEVER creates - critical under lazy frames; checks:
    frame_missing=info, frame_posture_conflict=warning,
    conduit_name_taken=blocker via cloud.has_conduit_name,
    cluster_name_taken=blocker via the documented _conduit_clusters seam);
    execute_plan refuses host blockers PRE-ENGINE (teach-grade rows) or
    downgrades them to "skipped_existing" under skip; admission payload
    gains additive "host" key {findings, checked}. (3) RestoreEngine:
    additive skip_existing kwarg; conjure skip lane (taken name -> conjure
    name=None + shortfall "conduit_name_taken_built_unnamed"; safe because
    names are never replay resolution keys) + cluster reuse lane (existing
    cluster -> members join + shortfall "cluster_existed_members_joined",
    not counted built). (4) Threading: loader passes aether into
    LoadAdmission; restore_formation_record + Crystallizer.restore_formation
    gain the two additive params. (5) compose_frame_subtree/
    compose_conduit_subtree DELETED (zero callers re-proven tree-wide;
    NOTE marker records the ruling; capture_formation_slice is the shipped
    composer). (6) T4: 4 new unit tests in test_crystal_loader_system.py
    (retarget rewrite + copy-on-write proof; multi-frame/bad-name refusal;
    host preflight all four check kinds incl. retarget-to-missing-frame
    clearing collisions; host-blocker refusal pre-engine + skip arming).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:238-489
  - src/melder/crystallizer/crystal_loader_system/load_plan.py:52-260
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1216-1240
  - tests/unit/melder/crystallizer/crystal_loader_system/test_crystal_loader_system.py:275-490
  IMPACT: S1 acceptance surface complete - formations compose into live
    worlds with host preconditions, retargeting, and explicit collision
    policy; facades stay a byte-compatible superset.
  TESTS: Not run (sandbox cannot import melder; bash replica rot on all
    grown files - real disk verified via file-tool sentinels). Owner
    full-tree 3.14t run requested (this tranche + the lazy-frames/LoadGate
    tranche land together).
  NEXT: owner run verdicts -> acceptance walk -> S2 physical custody.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T16:05:00Z
  TYPE: FACT
  CLAIM: DEVOPS-TWIN INVESTIGATION (owner-directed) + PROPAGATION FIX
    (owner go). Findings: the frame's dev-ops configuration IS twinned
    (AethericFrameCrystal.dev_ops_payload = full describe_posture map:
    7 disable_* gates, caching posture, shared flag,
    max_transaction_wait_time_in_seconds), IS reloaded
    (from_recorded_posture consumes the whole dev_ops surface with
    per-key backfill reporting; system_state_name hard-required), and IS
    booted for the disable_* gates (read LIVE at verb time:
    spellbook.py:2977/2981, conduit.py:1200-1246, conduit_cloud.py:174 -
    the rebind lands on the canonical posture object those reads consult).
    GAP found and FIXED: max_transaction_wait_time_in_seconds was captured
    ONCE at frame construction (CCM ctor -> mediator ctor) and
    mediator.configure() had ZERO callers - restored/rebound wait bounds
    never reached the live mediator (guaranteed at restore under lazy
    frames: frames born mid-replay with default posture before the frames
    stage rebinds). Fix: AethericFrame._propagate_transaction_wait_posture
    routes the canonical posture's bound through the existing public chain
    (dev_ops_manager -> CCM -> transaction_mediator.configure); called
    from BOTH posture-landing branches of bind_frame_configuration
    (adopt-new + copy-into-existing); match/conflict branches untouched.
    Patch doc component_patch_frame_posture_propagation.md added to the
    aether_lazy_frames_and_load_gate_2026_07_11 dir BEFORE code. New
    integration test test_bound_posture_wait_bound_reaches_the_live_mediator
    (boot 30.0 -> bind 44.0 -> mediator enforces 44.0). ALSO: consumed
    mutation_0's 13:46Z NOTICE (MR Phase-B additive; restore engine
    untouched, MR stays a report stage; no melder-side action) and cleared
    the alert line.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:562-570,614-622,638-685
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:627-712,1053-1094
  - src/melder/crystallizer/crystals/aetheric_frame_crystal.py:35-50
  - tests/integration/melder/aether/test_aether_integration_core.py:286-328
  IMPACT: Restored worlds now enforce their recorded transaction wait
    bounds; live posture rebinds propagate too. Dev-ops posture story is
    fully closed: twinned + reloaded + booted, no silent substitution.
  TESTS: Not run (sandbox; replica rot on grown files - disk verified via
    file-tool). Rides the same owner 3.14t sweep as the rest of the day.
  NEXT: owner run verdicts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T16:40:00Z
  TYPE: FACT
  CLAIM: CORRECTION (owner run 1 fallout, tree-wide cascade): the 16:05Z
    propagation fix accessed `CCM.transaction_mediator` as an ATTRIBUTE,
    but it is a plain accessor METHOD (no @property - unlike
    frame.dev_ops_manager and DevOpsManager.change_control_manager, which
    ARE properties; spellbook._get_required_transaction_mediator calls it
    with parens and was the available precedent I failed to check).
    AttributeError("'function' object has no attribute 'configure'") fired
    on EVERY conjure (bind_frame_configuration -> propagate helper), so
    the single line broke most suites from 11% onward. Same wrong form sat
    in Aether.acquire_load_authority's drain loop (gated loads) and the
    new integration test. ALL THREE fixed to
    `.transaction_mediator().{configure,describe}()`; tree-wide grep shows
    zero remaining bare uses (only import paths match). Process lesson
    recorded: accessor FORM (property vs method) is a source-verification
    item, not an assumption - the proven-live caller path is the check.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:681-687
  - src/melder/aether/aether.py:843-852
  - tests/integration/melder/aether/test_aether_integration_core.py:314-316
  - src/melder/aether/spellbook/spellbook.py:3002-3016
  IMPACT: The conjure-path cascade is closed at the root; LoadGate drain
    and the wait-bound test carry the same correction.
  TESTS: Not run. Owner rerun requested - remaining failures (if any)
    should now be genuine lazy-frames/LoadGate/S1 fallout, not this.
  NEXT: owner rerun; triage whatever remains one by one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T17:55:00Z
  TYPE: FACT
  CLAIM: CLOSED - owner full-tree 3.14t GREEN ("they all passed"), after
    two recorded correction passes (mediator accessor form 16:40Z;
    lazy-frames test sweep 17:20Z in the lazy task). ACCEPTANCE WALK
    against the criteria: (1) conduit/frame formations load into LIVE
    worlds through the admission pipeline - host preconditions
    verdict-gated in _preflight_host (refuse-by-default, teach-grade
    rows), optional retargeting via copy-on-write window rewrite,
    explicit skip_existing policy arming the engine's two skip lanes -
    ALL landed and covered by 4 new unit tests + the green integration
    round-trips; (2) compose_frame_subtree/compose_conduit_subtree
    DELETED with the ruling recorded in a NOTE marker (zero callers
    proven twice); (3) facade surface is a byte-compatible superset -
    additive params (target_frame_name, skip_existing) and additive keys
    (admission.host) only. BONUS LANDINGS in this lane: LoadAdmission
    rename, Aether LoadGate (load authority spans, drain, mediator
    root-start checks), DevOps posture propagation fix
    (wait bound -> mediator.configure), MR coordination consumed (Phase-B
    + read facade notices; no melder action). Patch dirs
    (crystallizer_v3_horizon_2026_07_11 +
    aether_lazy_frames_and_load_gate_2026_07_11) queued on the artifact
    board for C-doc promotion + graph sync as the epic's batch.
  EVIDENCE:
  - tickets/stories/2026-07-11_load_scope_maturity_story.md:60-99
  IMPACT: S1 complete; epic advances to S2 physical custody.
  NEXT: none (story closed); S2 opens.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
First tranche of the V3 horizon epic: make formation loads compose into live
worlds (host preconditions, retargeting, skip_existing) and retire the
compose_* placeholder debt. Investigation first; patches before code.
