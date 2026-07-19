# Crystallizer Configuration

## Metadata
- Artifact ID: ART-2026-05-03-crystallizer-configuration
- Parent Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: active
- Created: 2026-05-03T17:13:48Z
- Updated: 2026-05-03T17:13:48Z

## Purpose
Capture the dedicated configuration feature for crystallizer-driven
synthetic-module copy mode.

This artifact exists to define:
- when and how physical `.py` modules may be copied into synthetic-module-backed
  asset truth
- how registration should work
- how root reference targets and path targets should be mapped
- how the system locates the real file location of source-backed modules
- why this makes snapshots easier to use

This is not the general philosophy file.
It is the feature-specific configuration layer for one powerful optional mode.

## Core Feature
The system should support a crystallizer configuration option that allows
eligible Python source modules to be mapped into synthetic-module-backed assets
without forcing users to change their imports.

In this mode:
- the module keeps its canonical import name
- the system creates a synthetic-module copy of the source-backed module
- the copy can be stored in the database as asset-backed module truth
- loaders can later reactivate that module into `sys.modules`
- snapshots can rebuild the module world from the retained asset set

This is an explicit mode, not an always-on default.

## Why This Exists
This mode is useful because:
- synthetic modules are easier to move, activate, and persist
- users can keep working in codegen mode when they want
- directory layout becomes less operationally important once module truth is
  retained as assets
- snapshots can byte-copy the relevant source-backed and synthetic-backed world
  more directly

The point is not to erase files from reality.
The point is to let crystallizer retain a module-backed world that can be
reloaded later with less filesystem coupling.

## Hard Boundary From The Experiments
This feature must respect the recent physical->synthetic swap experiment:
- transparent live reassociation of already-imported physical code is not
  generally safe
- eager imports, function globals, class-method globals, existing instances,
  and already-imported class objects keep the old physical world
- lazy imports and explicit `importlib.reload(...)` can see the new synthetic
  provider world

Therefore:
- this configuration feature is intended for bootstrap/rebuild/reload
  boundaries
- it is not a general-purpose invisible mid-flight hot swap under already-live
  physical references

That boundary is non-negotiable unless later experiments prove otherwise.

## Configuration Surface
The exact code shape can still vary, but the configuration needs to express at
least:

### 1. Feature toggle
- whether synthetic-module copy mode is enabled at all

### 2. Eligibility scope
- which physical modules are eligible to become synthetic copies
- likely restricted to user source under configured roots
- site-package-backed modules are a separate authority class and should not be
  blindly copied as if they were local source

### 3. Activation boundary
- this mode applies during:
  - bootstrap
  - explicit rebuild
  - explicit reload
- not arbitrary transparent live reassociation

### 4. Registration mode
- how the synthetic copy is registered into `sys.modules`
- how parent package shells are prepared
- how import names remain the same

### 5. Snapshot preference
- whether snapshots should prefer retaining synthetic-module copies for
  eligible `.py` files
- whether physical paths are still retained alongside the synthetic copy as
  reference/projection truth

## Root Reference Target
The system needs one root reference target for the spell/module world it is
trying to retain.

For this feature, the root reference target should be the canonical module
identity:
- the full dotted import name of the module being retained

Examples:
- `project.domain.models.user`
- `melder.aether.nexus.rift.rift`

This matters because later loaders need a stable module identity to:
- activate the right module
- place it in `sys.modules` under the right key
- satisfy import statements without changing source code

## Path Targets
The system also needs path targets.

Path targets should capture the real physical source locations associated with
the retained module world.

These should be stored as flat path-oriented references so loaders and
validators can answer:
- where did this module actually come from?
- what file backs this source truth?
- what directory root did it belong to?

At minimum, the feature should preserve:
- module file path
- package root path or nearest relevant source root
- any directly associated support file paths when needed later

## Registration Rules
If a synthetic-module copy is created for an eligible physical `.py` module:

1. the canonical module name must stay the same
2. the synthetic module must be activated under that canonical name in
   `sys.modules`
3. parent packages/shells must also exist with the right package semantics
4. imports should continue to work without source-code changes

So the important rule is:
- the source authority changes
- the import surface does not

This is the only reason the feature is ergonomically valuable.

## Actual File-Location Discovery
The configuration feature must also define how we locate the real source file
being copied.

Reasonable discovery inputs include:
- module object metadata (`__file__`)
- inspect/module resolution
- package directory structure under configured source roots

The goal is not to guess forever.
The goal is to record enough physical-path truth that:
- the synthetic copy has provenance
- snapshots know what was copied
- later physical projection or validation remains possible

## Relationship To Assets
This feature fits the broader asset model:

- the original `.py` remains an asset
- the synthetic-module copy becomes a retained module asset
- both can be referenced in snapshots if needed

This means the system does not have to choose between:
- files exist
- memory exists

It can retain both:
- physical path truth
- synthetic module truth

That is stronger than pretending one destroys the other.

## Relationship To SpellCrystal
This feature is closely related to `SpellCrystal` but not identical to it.

The current intended relationship is:
- the synthetic-module copy mode determines how a physical source module may be
  lifted into retained module truth
- the resulting spell/module world can then be referenced by crystals and
  snapshots

That means this configuration feature helps define:
- what module truth exists
- what the loader can activate
- what snapshots can keep in codegen-like mode later

## Snapshot Implications
This is one of the strongest reasons to support the feature.

If eligible physical `.py` files can be copied into synthetic-module-backed
asset truth, then snapshots become easier to use because they can:
- snapshot the relevant directory or source root
- byte-copy the required source-backed assets
- store the synthetic-module-backed representations too
- rebuild the module world more directly later
- optionally keep the restored system in codegen/synthetic-module mode

That is a strong world-first property.

The snapshot is no longer only:
- a file tree reference

It can also be:
- a module world capture

## What This Feature Does Not Promise
It does not promise:
- safe transparent hot swap under already-imported physical code
- automatic correctness for modules tightly coupled to `__file__` or arbitrary
  filesystem layout assumptions
- a universal replacement for all package/resource semantics

Those remain bounded by the explicit loader/rebuild model and by module
eligibility.

## Practical Intended Use
The intended use is:

1. user enables synthetic-module copy mode for eligible source
2. crystallizer captures the root reference target and path targets
3. source is copied into retained synthetic-module-backed asset truth
4. snapshot stores the needed module/path world
5. loader later reactivates the modules under the same import names
6. imports continue to work without source changes
7. the rebuilt world may stay in codegen/synthetic-module mode if desired

## Summary
In one sentence:

The crystallizer configuration feature should allow eligible physical `.py`
modules to be copied into synthetic-module-backed asset truth at explicit
bootstrap/reload boundaries, preserve both canonical module identity and real
file-location targets, register the synthetic copies under the same import
names in `sys.modules`, and make snapshots easier to byte-copy and rebuild
while still optionally keeping the restored world in codegen/synthetic-module
mode.
