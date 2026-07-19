# Architecture Patch: Melder package-root composition + single version truth + wheel posture

Lane: melder_init_composition_2026_07_19.
Ticket: STORY-2026-07-19-melder-init-composition.

## Objective (owner rulings 2026-07-19, captured in the strategy task)
`import melder as md` must land the user in a LOADED, flat, eager namespace: all
front-facing configurations, all front-facing enums, all important runtime objects and
DI descriptors - no lazy machinery, no __getattr__, no shims. Version truth collapses to
ONE place. The wheel posture finishes (Apache license files declared; dynamic version).

## Non-Goals
- No change to the import-time world boot: the guard sentinel constructs FIRST and
  Aether() eagerly boots (owner ruling: redundancy with Aether's own guard accepted -
  it is a sentinel and must exist early).
- No touch of the Spellbook._aether class-body seam (separate patch-gated story).
- No re-export wiring in SUBPACKAGE __init__ files (the no-export-wiring law stands
  everywhere below the root; the root is the deliberate public facade).

## Changed Components
1. src/melder/__init__.py: curated flat export surface (below), DEBUG_MODE + version
   mutation DELETED, stale "ThreadFactory" docstring rewritten, guard + Aether() boot
   and both runtime warnings preserved verbatim.
2. src/melder/__version__.py: stays the single version truth (plain literal).
3. pyproject.toml: [project] version -> dynamic via setuptools attr on
   melder.__version__ (static AST read; no import at build time);
   license-files = ["LICENSE", "NOTICE"] (Apache distribution duty); build-system
   setuptools floor raised to >=77 (PEP 639 pairing for license-files).
4. tests: version-contract tests rewritten to the single-truth law; new public-surface
   suite pins every __all__ name resolvable and identical to its concrete-path class.

## Public Surface (curated per ruling)
- Objects: Aether, Nexus, Spellbook, SpellBinder, Conduit, Crystallizer,
  MutationResearch, Scan, ProtocolCrafter.
- Configurations: AetherConfiguration(+Builder), AethericFrameConfiguration,
  SpellbookConfiguration, CrystallizerConfiguration(+Builder),
  MutationResearchConfiguration(+Builder), NexusConfiguration, RiftConfiguration.
- Enums: Existence, Policies, Permissions, SystemState, LaneType, RiftSpaceType,
  NexusFrameMode.
- DI descriptors: SpellMap, SpellContract.
- Curation calls (owner may veto): ClaimMode stays internal (admission-plane
  vocabulary); Rift/RiftSpace stay Nexus-created (not exported); SpellExaminer stays a
  compiler-internal tool for now.

## Invariants
- Internals NEVER import from the melder root (concrete-path law) - the root facade
  cannot create cycles.
- melder.__version__ == melder.__version__.__version__ byte-equal, every build, every
  runtime; no environment-dependent mutation.
- The wheel remains py3-none-any, zero-dependency, src-layout (context_compass, tests,
  benchmarks excluded by the existing find/exclude).

## Migration Order
Init rewrite -> version test rewrite + surface suite -> pyproject dynamic/license ->
owner builds the wheel (python -m build --wheel) and stages the CommandOps wheelhouse.

## Rollback
Restore the static [project] version line and the prior init; tests revert with it.

## Ticket Coverage Matrix
- Init surface rows -> tests/unit/melder/test_package_public_surface.py
- Version truth rows -> tests/unit/melder/test_package_version_metadata.py
