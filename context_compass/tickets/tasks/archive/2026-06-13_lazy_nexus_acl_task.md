

# Task: Defer nexus.acl import + FrameACLManager construction to first use

## Metadata
- Task ID: TASK-2026-06-13-lazy-nexus-acl
- Status: blocked (reverted; retry requires traceback + describer read)
- Owner: claude
- Agent Name: compiler_strategy_0
- Priority: p2
- Created: 2026-06-13T09:40:00Z

## Objective
Last catalogued import-wall cut (~20-25ms): Nexus built FrameACLManager in
`__init__`, which runs inside the package-import `Aether()` bootstrap,
dragging the full nexus.acl chain at import. Same deferral pattern as
MutationResearch.

## Notes
- DATETIME: 2026-06-13T09:40:00Z
  TYPE: FACT
  CLAIM: Landed in src/melder/nexus/nexus.py only: (1) the four
    module-level acl imports moved under TYPE_CHECKING; (2) init sets
    `_frame_acl_manager = None`; (3) new `_get_frame_acl_manager()` --
    double-checked under self._lock, check_cleaned first, builds once,
    cleanup never re-creates; (4) ALL 17+ use sites routed through the
    accessor via mechanical `self._frame_acl_manager.` ->
    `self._get_frame_acl_manager().` replacement, with the cleanup site
    reverted to the direct guarded read; (5) FrameACLCompiler and
    CompiledFrameACLAccessSurface get method-local imports at their only
    construction sites (1694, ~1618). Verified: no module-level acl
    importers remain outside the acl package itself. SEMANTIC NOTE: the
    acl chain + manager now load on FIRST ACL access (frame registration
    during conjure), so first-conjure absorbs the one-time cost import
    used to pay -- import metric improves, total process time unchanged.
    RISK: tests poking `nexus._frame_acl_manager` directly see None until
    first accessor use.
  EVIDENCE:
  - src/melder/nexus/nexus.py:33-40
  - src/melder/nexus/nexus.py:202-208
  - src/melder/nexus/nexus.py:2110-2140
  IMPACT: expected ~20-25ms off cold import (the catalogued estimate).
  NEXT: user validation -- importtime grep for acl rows (expect zero),
    full nexus + spellbook suites, cycle benchmark for the first-conjure
    shift. Board row sync after validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T10:30:00Z
  TYPE: BLOCKER
  CLAIM: REVERTED IN FULL. The lazy cut broke 150 nexus-viewer matrix
    tests with `NameError: FrameACLConfiguration is not defined`. Fixing
    the two isinstance sites changed NOTHING (identical 150 failures), so
    the raising frame is not nexus.py's executed code -- something in the
    viewer/AST-describer surface (frame_viewer.py imports
    class_surface_ast_describer and reflects over the Nexus surface)
    resolves nexus annotations at runtime against module globals. Without
    the full traceback that is a guess, and two blind patches is the
    limit: nexus.py restored to its exact pre-change state (module-level
    imports, eager FrameACLManager in __init__, no accessor, no local
    imports). LESSON RECORDED: TYPE_CHECKING deferral is NOT
    automatically safe in this codebase -- the AI-native introspection
    surfaces (class_surface_ast_describer, viewer matrices) evaluate
    annotations that plain runtime execution never touches. The
    MutationResearch/metadata cuts survived because nothing introspects
    those surfaces; any future import deferral must FIRST check whether
    the describer reflects over the target module.
  EVIDENCE:
  - src/melder/nexus/rift/frame_viewer/frame_viewer.py:31-39
  IMPACT: ~20-25ms import cut foregone for now; zero residue in src.
  NEXT: retry ONLY with: (1) the full pytest traceback for one failure,
    (2) a read of class_surface_ast_describer's annotation resolution,
    (3) a fix shaped to that contract (e.g., describer-safe lazy names).
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Validation
- Reverted before any validation could pass; user reruns the viewer
  matrix file + full unit tree to confirm restoration.
