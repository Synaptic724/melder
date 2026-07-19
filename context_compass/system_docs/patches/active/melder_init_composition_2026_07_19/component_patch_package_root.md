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
