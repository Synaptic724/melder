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


## Context / Handoff Summary
Implementation lane for the init/wheel program; rulings live in the parent strategy
task; hand-off mechanics (wheelhouse --find-links, editable co-dev) documented there.
