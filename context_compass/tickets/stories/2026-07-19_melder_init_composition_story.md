# Story: Melder package-root composition, single version truth, wheel posture

## Metadata
- Story ID: STORY-2026-07-19-melder-init-composition
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-19T11:49:00Z
- Updated: 2026-07-19T11:52:00Z
- Parent strategy: TASK-2026-07-19-melder-init-wheel-strategy

## Objective
Implement the owner's init rulings: flat eager LOADED root namespace (objects +
configurations + enums + DI descriptors), guard sentinel early, DEBUG_MODE and version
mutation deleted, single version truth wired into pyproject dynamic metadata,
license-files declared, wheel-ready.

## Ticket Contract
- ENTRY_GATE: owner rulings captured 2026-07-19 in the strategy task ("keep it simple...
  loading up the init imports so a user can do import melder as md"); patch docs under
  system_docs/patches/active/melder_init_composition_2026_07_19/ authored before code.
- EXECUTION_BOUNDARY: src/melder/__init__.py, pyproject.toml, version/surface tests.
  NOT the Spellbook._aether seam (separate patch-gated story). No subpackage __init__
  export wiring.
- DEPENDENCIES: patch docs above.
- EXIT_GATE: owner 3.14t green + owner-built wheel carries LICENSE/NOTICE and installs
  into the CommandOps venv from the wheelhouse.
- FAILURE_ESCALATION: DECISION_REQUEST on any surface-curation dispute (ClaimMode,
  Rift, SpellExaminer flagged as curation calls).

## Noting Behavior
- Story notes: cross-surface synthesis and gate transitions.

## Notes
- DATETIME: 2026-07-19T11:52:00Z
  TYPE: MEASURE
  CLAIM: Implementation LANDED per the captured rulings (patch docs first). (1)
    src/melder/__init__.py rewritten: grouped eager import blocks (metadata/guard ->
    objects -> configurations -> enums -> DI descriptors -> tools); +13 curated exports
    (Crystallizer + config + builder, MutationResearch + config + builder,
    NexusConfiguration, RiftConfiguration, LaneType, NexusFrameMode, RiftSpaceType,
    SpellMap, SpellContract - every class name verified against source before import);
    DEBUG_MODE and the version mutation DELETED (__version__ re-exports the metadata
    literal untouched); stale ThreadFactory docstring replaced with the DGR story +
    import-melder-as-md usage; guard sentinel construction + Aether() boot + both
    runtime warnings preserved at the same execution points. __all__ = 37 names
    mirroring the imports 1:1. Concrete-path law verified repo-wide: ZERO internal
    modules import the melder root (grep-proven), so the eager MR import chain (the one
    genuinely new import-time subtree) cannot cycle; its module heads are class-defs
    only. (2) pyproject.toml: version -> dynamic via [tool.setuptools.dynamic] attr on
    melder.__version__.__version__ (plain literal = static AST read, no build-time
    import); license-files = ["LICENSE", "NOTICE"] (both files exist); build-system
    setuptools floor 61 -> 77 (PEP 639 pairing). (3) Tests: version suite rewritten to
    the single-truth law (equality regression retires the dev-suffix contract); NEW
    test_package_public_surface.py (6 rows: all-__all__ resolvability, identity-not-
    equality for objects/configs/enums/descriptors against concrete paths, guard
    sentinel liveness). compile() green (init + both test files); 120-col clean; CRLF
    preserved; TOML unvalidatable on the 3.10 device VM (tomllib absent) - the owner
    build validates it. pytest Not run; wheel build Not run (owner: python -m build
    --wheel). Curation calls flagged for veto: ClaimMode stays internal; Rift/RiftSpace
    stay Nexus-created; SpellExaminer stays compiler-internal.
  EVIDENCE:
  - src/melder/__init__.py:1-170
  - pyproject.toml:1-30
  - pyproject.toml:60-75
  - tests/unit/melder/test_package_version_metadata.py:1-25
  - tests/unit/melder/test_package_public_surface.py:1-160
  IMPACT: import melder as md now reaches the whole front-facing system; version truth
    is one literal consumed by runtime and build alike; the wheel is one owner command
    away with correct Apache distribution files.
  NEXT: Owner: pytest tests/unit/melder -q, then python -m build --wheel, verify
    LICENSE/NOTICE inside the dist-info, stage the CommandOps wheelhouse
    (pip install melder --find-links=<wheelhouse>; pip install -e for co-dev).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-07-19T11:58:00Z
  TYPE: MEASURE
  CLAIM: Owner ruling landed - 3.14+ is the support floor, 3.13 dropped. Swept every
    reference: init version gate (3,13,0)->(3,14,0) with honest below-floor wording
    (the "will still work on older Pythons" claim is gone), nogil-warning text to
    3.14+, README's two public claims to 3.14+/free-threading, canonical C-doc
    guardrail lines synced (4 lines across src_architecture/src_components). pyproject
    needed nothing (requires-python/classifiers already 3.14-only). The one surviving
    "3.13+" in src is a FACTUAL CPython comment (__firstlineno__ appeared in 3.13) -
    accurate, not a support claim, left alone. compile() green on the init; grep-clean
    otherwise. pytest Not run.
  EVIDENCE:
  - src/melder/__init__.py:96-128
  - README.md:1-70
  - context_compass/system_docs/src_architecture.md:430-434
  - context_compass/system_docs/src_components.md:179-183
  IMPACT: The package now states one truth everywhere: 3.14+ free-threading or you
    are unsupported.
  NEXT: Rides the same owner runbook (pytest + wheel build).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T12:02:00Z
  TYPE: MEASURE
  CLAIM: Load-up wave LANDED per the owner's full-surface ruling. Root grows 37 -> 57
    names: +11 user-held work surfaces (Rift, RiftSpace, FrameViewer, Workstation,
    SpellSpace, ConduitCloud, ResearchSet, SpellExaminer, CrystallizerBootstrap,
    ExternalPersistenceManager + Configuration), +scan_bind (the deferred-registration
    decorator beside Scan), +9 user-catchable exceptions (every error type public verbs
    raise at users, incl. DeadReferenceError from the weak workstation lane -
    raise-site verified in the weak data structures). Every class name and module path
    source-verified before import; bootstrap_loader's import head checked for cycle
    safety (crystallizer chain already resolved when it loads). Curation law honored:
    ConduitWard and seven other looks-public depths pinned OFF the root by a negative
    regression row. Surface suite now 10 rows (identity-not-equality throughout).
    compile() green x2 (init 57-name __all__, tests); 120-col clean. pytest Not run.
  EVIDENCE:
  - src/melder/__init__.py:40-200
  - tests/unit/melder/test_package_public_surface.py:160-330
  - src/melder/crystallizer/crystal_loader_system/bootstrap_loader.py:1-17
  - src/melder/utilities/custom_exceptions/dead_reference_error.py:4-4
  IMPACT: import melder as md is now the complete user vocabulary - work surfaces,
    configurations, enums, descriptors, tools, and the whole catchable error family -
    with the internal depths deliberately fenced out.
  NEXT: Owner runbook unchanged: pytest tests/unit/melder -q -> python -m build
    --wheel -> wheelhouse into CommandOps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T12:16:00Z
  TYPE: MEASURE
  CLAIM: Pass-2 C-doc iteration landed (owner: "iterate over the documents a few
    times... theres a few decorators"). Re-read the External Interfaces section of
    src_architecture end-to-end and swept the source for every decorator factory. Root
    57 -> 64: +ViewFrame/ViewConduit/ViewSpell/ViewMultiFrame (doc names
    ViewSpell.describe_spell_research as an external interface; the family is what
    get_frame_viewer hands users), +DiffEngine (create_diff_engine() is a listed
    public verb - held-and-called), +LaneState (public lane.state property returns it;
    pairs LaneType), +class_wraps (the ONLY other true user decorator in the runtime -
    scan_bind was already in; decorate_public_view_actions is internal law machinery
    and stays out). Evidence-based exclusions: ConduitCluster (create_cluster -> None,
    users never hold one - verified in conduit_cloud.py:416), StaticFrameViewer
    (subclass vehicle), both pinned into the negative regression (now 10 exclusions).
    Surface suite 12 rows incl. a ledger-integrity row (uniqueness + vars coverage for
    all 64). compile() green x2; 120-col clean. pytest Not run.
  EVIDENCE:
  - src/melder/__init__.py:40-230
  - context_compass/system_docs/src_architecture.md:437-560
  - src/melder/aether/aetheric_frame/conduit_cloud.py:416-422
  - src/melder/utilities/helpers/class_wraps.py:5-44
  - tests/unit/melder/test_package_public_surface.py:330-400
  IMPACT: The root now carries every surface the canonical docs name as external, the
    full decorator vocabulary, and machine-checked fences around the depths.
  NEXT: Owner runbook unchanged (pytest + wheel). Curation vetoes still open.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Implementation lane for the init/wheel program; rulings live in the parent strategy
task; hand-off mechanics (wheelhouse --find-links, editable co-dev) documented there.
