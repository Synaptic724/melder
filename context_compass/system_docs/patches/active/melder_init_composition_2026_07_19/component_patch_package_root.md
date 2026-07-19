# Component Patch: package root (src/melder/__init__.py + pyproject)

Lane: melder_init_composition_2026_07_19.

## Before
- 24 imports / 22 __all__ names; Crystallizer, MutationResearch, their configurations,
  Nexus/Rift configurations, LaneType/RiftSpaceType/NexusFrameMode, SpellMap and
  SpellContract all missing from the root surface.
- DEBUG_MODE = True hardcoded at module scope mutates __version__ to base + ".dev0" -
  version truth lives in three places (init mutation, __version__.py, pyproject static).
- Docstring markets "ThreadFactory"; module-scope constant violates the module-scope
  law; guard + Aether() boot correct per ruling.
- pyproject: static version, no license-files declaration.

## After
- One grouped, commented import block (metadata/guard -> objects -> configurations ->
  enums -> DI descriptors -> tools); __all__ mirrors it 1:1; guard construction and
  Aether() boot preserved at the same point in module execution; both runtime warnings
  byte-preserved.
- __version__ re-exported UNTOUCHED from melder.__version__ (DEBUG_MODE deleted).
- Docstring describes the Dependency Graph Runtime and the `import melder as md` usage.
- pyproject: dynamic = ["version"] + [tool.setuptools.dynamic] attr read;
  license-files declared; setuptools>=77 floor.

## Interface Deltas
- ADDITIVE root exports: Crystallizer, CrystallizerConfiguration,
  CrystallizerConfigurationBuilder, MutationResearch, MutationResearchConfiguration,
  MutationResearchConfigurationBuilder, NexusConfiguration, RiftConfiguration,
  LaneType, RiftSpaceType, NexusFrameMode, SpellMap, SpellContract.
- REMOVED root name: DEBUG_MODE (never a documented contract; test suite pins the
  version equality that its deletion changes).

## State / Failure Deltas
- Import-time behavior identical except ~13 additional module imports that the runtime
  chain already loads transitively today (no new construction; enums/classes only).

## Validation Expectations
- Surface suite: every __all__ name resolves and IS the concrete-path object (identity,
  not equality); version equality law; no-DEBUG_MODE regression via version equality.
- Owner: python -m build --wheel produces melder-0.1.0-py3-none-any.whl with LICENSE +
  NOTICE inside the dist-info.

## Delta 2026-07-19 (owner ruling): 3.14+ support floor
- Version-warning gate moves (3, 13, 0) -> (3, 14, 0); warning text says "requires
  Python 3.14+" and drops the works-on-older-Pythons claim (below-floor interpreters
  are unsupported, stated honestly). GIL-mode warning wording follows. README public
  claims updated to 3.14+/free-threading. pyproject was already 3.14-only
  (requires-python, classifiers). Canonical C-doc guardrail lines synced.

## Delta 2026-07-19 (owner ruling): FULL user-facing load-up
- Root surface grows 37 -> 57 names. Added: user-HELD work surfaces (Rift, RiftSpace,
  FrameViewer, Workstation, SpellSpace, ConduitCloud, ResearchSet, SpellExaminer,
  CrystallizerBootstrap, ExternalPersistenceManager + Configuration), the scan_bind
  decorator, and the nine-user-catchable exception vocabulary (SpellbookValidationError,
  MeldExecutionError, SpellSpaceScopeError, HookExecutionError,
  InternalRegistrationError, PhaseSchedulerError, PhaseExecutionError,
  PhaseTimeoutError, DeadReferenceError).
- Curation law (owner's counter-example: ConduitWard): looks-public-but-internal depths
  stay OFF the root - ConduitWard, Meld/Creations, command systems, View* helpers, room
  subclasses, lanes/nodes, diff/impact engines, builders/managers, PhaseScheduler,
  LoadGate, RestoreEngine, admission plane, ClaimMode, crystals/twins, Cleanable and
  logging seams. A negative regression pins eight exclusions.

## Delta 2026-07-19 (pass 2, C-doc iteration): doc-named surfaces + decorators
- 57 -> 64 names. Added from the External Interfaces re-read: the viewer family the
  doc names as user surfaces (ViewFrame, ViewConduit, ViewSpell, ViewMultiFrame),
  DiffEngine (held-and-called via create_diff_engine()), LaneState (enum behind the
  public lane.state property, pairing LaneType), and class_wraps (the second true user
  decorator - functools.wraps for class decorators, documented user Usage block).
- Verified exclusions extended: ConduitCluster (create_cluster returns None - never
  user-held) and StaticFrameViewer (subclass vehicle; FrameViewer is the contract)
  pinned into the negative regression. decorate_public_view_actions stays internal
  (viewer-law machinery, not a user hand).
