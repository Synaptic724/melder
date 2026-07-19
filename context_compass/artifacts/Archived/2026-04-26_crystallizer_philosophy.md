# Crystallizer Philosophy

## Metadata
- Artifact ID: ART-2026-04-26-crystallizer-philosophy
- Parent Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: active
- Superseded-where-conflicting by: `2026-07-01_crystallizer_philosophy_v2.md` (2026-07-01 tool-model refinement;
  that document wins on any disagreement)
- Created: 2026-04-26T10:11:59Z
- Updated: 2026-05-03T16:22:08Z

## Purpose
Capture the modern crystallizer philosophy in one canonical artifact instead of
spreading it across disconnected notes.

This document is the current source of truth for:
- world-first crystallizer design
- synthetic-module retention and activation
- bind as the promotion boundary
- conduit snapshots as the primary load unit
- mutation manifest relationship to conduit snapshots
- optional subsystem boundaries across Melder core and `melder_pro`

The goal is not to freeze every implementation detail.
The goal is to state the current architecture clearly enough that future code
and artifacts stop drifting into contradictory models.

## Core Thesis
Crystallizer is the source-truth, persistence, and recovery bridge for managed
software artifacts in this system.

The split is:
- `Melder`
  - live runtime truth
  - spell registration
  - resolution, lifecycle, and conduit behavior
- `Rift`
  - local dynamic construction surface
  - namespace-backed codegen
  - optional local synthetic-module ownership
- `Crystallizer`
  - retained module truth
  - dependency truth
  - activation/bootstrap truth
  - snapshot/export/import truth
- `MutationResearch`
  - lineage/version/fork semantics
  - research lanes
  - promotion and merge semantics over live spell worlds

So Crystallizer is not:
- a second runtime
- a package manager
- a DB framework
- a replacement for MutationResearch
- a command/orchestration engine

It is:
- the managed artifact persistence and recovery layer

## World-First Design
This is a world-first design, not a file-first one.

The system should support three different but related realities:

### 1. Local dynamic construction
- scratch codegen execution in a namespace
- temporary Rift-managed synthetic modules
- cheap local experimentation

### 2. Promoted runtime world-building
- module-backed code that becomes bindable
- conduit-local spell worlds
- dynamic runtime slices that matter beyond one scratch action

### 3. Durable reloadable world slices
- conduit snapshots
- retained module/crystal truth
- optional mutation manifests
- later reload into another runtime location

The important rule is:
- do not collapse these three realities into one object
- do not force every local act of codegen into persistence
- do not pretend a published module is automatically durable world truth

## Layered Foundation
The current practical layering should be:

- all files are assets
- codegen remains namespace-backed by default
- Rift may also host local `SyntheticModule` objects
- when code becomes bind-relevant or world-bearing, it crosses a promotion
  boundary and becomes crystal-backed module truth
- conduits, not individual spells, are the first-class reload unit

So:

- `Asset`
  - universal storage / transport / checksum / mapping layer
- `CodegenNamespace`
  - scratch/runtime execution layer
  - cheap and local by default
- `SyntheticModule`
  - live in-memory module embodiment
- `SpellCrystal`
  - retained module/activation truth for bindable code and conduit rebuilds

This means a `.py` can be both:
- an asset
- and a spell-crystal-capable software unit

It also means a `SpellCrystal` may:
- hold inline module payload directly
- or point to asset-backed payload and dependency assets

If payload is stored in base64 transport form, activation should decode it back
into canonical module source text before building the live `SyntheticModule`.

## Runtime Boundary
Crystallizer must respect the actual runtime grammar:

- `Spellbook.bind(...)` is where spell registration begins
- `Bind` creates the `Spell` + `SpellIndex` story
- `Spellbook.conjure(...)` creates the root `Conduit`
- `Conduit` owns the live resolution/runtime surface
- `Nexus -> Rift -> RiftSpace` is the public AR/runtime surface
- `CodegenRiftSpace` owns the internal `CodegenSystem`
- `CodegenCommandSystem` is the room-facing facade over that engine

That means crystallizer semantics should be described in terms of:
- spell registration
- module truth
- conduit ownership boundaries
- room/runtime embodiment
- codegen-origin artifacts
- conduit snapshot loads

not in terms of generic Python module theory alone.

## Ownership And Authority
The system needs separate answers for:
- who currently owns a live module object
- who owns the authoritative retained module truth
- what the runtime import name is

The current intended split is:

### `Rift`
- may create, host, publish, and unload local synthetic modules freely
- may use those modules to support multi-module codegen work
- does not need Crystallizer ownership just because a module became importable

### `Crystallizer`
- owns the authoritative retained module truth once a module crosses the
  bind/persistence boundary
- owns the records used to reactivate those modules during conduit loads

### `sys.modules`
- is the live publication surface only
- publication does not imply persistence
- importability does not imply crystallization

This means:
- a module being present in `sys.modules` is not enough to conclude that
  Crystallizer owns it
- a Rift-local synthetic module may be published and later unregistered
  without any persistence implication
- import names can remain the normal canonical module names
- Crystallizer ownership does not need to appear in the import path

## Codegen Modes
The system deliberately keeps more than one codegen mode.

### 1. Generic codegen stream
- default scratch/runtime path
- executes against the normal codegen namespace
- good for probes, helpers, harnesses, and temporary work
- not bindable by default
- does not need a durable module identity

### 2. Rift-local synthetic-module stream
- explicit agent action inside the room
- agent chooses the module name intentionally
- module may be published into `sys.modules`
- remains Rift-owned while it is only local support material
- useful for multi-module local software worlds

### 3. Promoted bindable synthetic-module stream
- explicit promotion boundary
- module truth becomes durable enough to matter for bind/snapshot/load
- Crystallizer tracks the retained module/dependency truth
- conduit snapshots may later depend on it

This distinction matters because current Rift codegen executes in a plain
`CodegenNamespace` and therefore does not create module-backed provenance
automatically. Deliberate synthetic modules are the path from scratch codegen
into module-backed world truth.

## Publication Is Not Persistence
One of the most important rules is:

- `sys.modules` presence is publication, not durability

So:
- local module publication is fine
- importability is fine
- later unpublish/unload is fine

until a stronger boundary is crossed.

The stronger boundary is not publication.
The stronger boundary is promotion into durable world-bearing truth through bind
or conduit snapshot semantics.

## Bind As The Promotion Boundary
Bind is the promotion boundary from local dynamic construction into durable
world truth.

Before bind:
- a synthetic module may be local and transient
- it may support codegen without becoming durable truth
- it may be published and unloaded by Rift

At bind:
- module truth stops being "just local support"
- dependency mapping starts to matter
- source truth starts to matter
- the thing becomes eligible for persistence and conduit snapshot reload

This does not mean every small local codegen act must become a crystal.
It means anything that becomes part of a durable world slice must have
module-backed retained truth.

## What Crystallizer Owns
Crystallizer should own:

### 1. Artifact identity
- stable asset ids
- stable crystal ids

### 2. Module/source truth
- synthetic source text
- physical module text
- source authority kind
- source hash / SHA256
- canonical module name

### 3. Dependency truth
- AST import data
- `from ... import ...` data
- export surface
- internal/external dependency view
- enough graph semantics to reactivate interdependent synthetic modules

### 4. Activation truth
- enough metadata to publish retained modules back into `sys.modules`
- enough metadata to help rebuild conduit-facing spell worlds after activation

### 5. Persistence truth
- JSON export/import
- adapter-facing transaction/event emission
- bootstrap payloads

Crystallizer should not be the authoritative owner of:
- current owner conduit semantics
- live frame/conduit/spellbook placement
- current CreationContext state
- current phase artifacts
- live mutation runtime logic
- world orchestration

## What Crystallizer Does Not Own
Crystallizer should not own:
- DB schema/table creation
- pip/uv internals
- package-manager semantics
- runtime MutationResearch logic
- orchestration/workflow control
- debugger/probe logic
- automatic global deduplication policy beyond payload-hash reuse
- user update semantics for external systems

## Asset Model
Crystallizer should be the general asset manager for this system, but not all
assets are treated equally.

Practical rule:
- all files are assets
- some assets are also spell-crystal-capable software units
- codegen may start in a namespace and later become a synthetic module
- when code becomes bind-relevant or conduit-persistent, it gets a
  `SpellCrystal`

At the current design level:

- `.py`
  - asset
  - also spell-crystal-capable software truth
- `.pyi`
  - companion asset
- `.pyc`
  - cache asset
- `.pyd` / `.so` / `.dylib`
  - binary dependency assets
- configs/resources/other files
  - supporting assets
- `uv.lock`
  - environment/package asset
  - package-environment snapshot/reference, not world truth

Not every asset gets a crystal.
Crystals belong to code that has crossed the bind/persistence boundary.

### Authority classes for bind-relevant software
Crystals may point at different source authority classes:
- `codegen`
- `physical`
- `site_package`
- `opaque_reference` (best-effort / non-reconstructible support case)

The important point is:
- all bind-relevant software units can still become crystal-addressable
- but not every authority class carries the same payload depth

## The Smallest Honest Unit
Crystallizer should answer:

**what is the smallest honest mutation/persistence unit?**

For source truth:
- symbol-scope only when truly self-contained
- module-scope by default for file-backed Python
- synthetic-module scope for retained codegen
- external imports as dependency edges, not recursively crystallized source by
  default

For reload truth:
- the smallest honest reload unit is usually not the single spell
- it is the conduit world slice that owns a coherent set of modules, binds,
  links, permissions, and optional mutation state

## SpellCrystal
`SpellCrystal` is the canonical retained module unit.

Its modern job is:
- retain module truth
- retain dependency truth
- retain enough activation truth to rebuild a module world for conduit loads

Its modern job is not:
- mirror every mutable field on a live `Spell`
- become the full live runtime spell object in storage
- own mutation branching semantics

### `SpellCrystal` should own at least:
- `spell_crystal_id`
- `module_name`
- `source_text`
- `source_sha256`
- `source_authority_kind`
- `target_kind`
- `target_qualname`
- AST import/export/dependency metadata
- optional physical/materialized locations
- enough activation metadata to help rebuild a conduit world

### `SpellCrystal` should not be authoritative for:
- current owner conduit
- current frame
- current spellbook placement
- current spell-phase artifacts
- current live runtime ownership

It may cache best-effort bind-facing hints if useful, but those should not
control the truth of the live runtime.

## SyntheticModule
`SyntheticModule` is the live in-memory module object.

It exists so:
- generated code can be given real module-like shape
- agents can build multi-module local software worlds in Rift
- later codegen or runtime machinery can consume those modules coherently
- conduit loads can reactivate retained module truth into `sys.modules`
- file materialization remains optional

The same module name can therefore move through these states:
- local Rift-owned live module
- promoted bindable module
- crystal-backed retained module
- reactivated load-time module during conduit rebuild

## Conduit Snapshots As The Primary Load Unit
The first-class portable world unit should be the conduit, not the single
spell.

A conduit snapshot should be able to describe:
- the modules/crystals it needs activated
- the reconstructible bound spells inside that conduit
- conduit-local configuration and policy
- links/contracts/permissions when those belong to the snapshot boundary
- optional mutation manifest state when MutationResearch is present

This is easier for agents to reason about than arbitrary single-spell replay.

### Default snapshot exclusions
Some things are not honestly reconstructible by default:
- user-created objects
- lambdas
- other runtime-only opaque spell kinds

Those should be excluded from snapshot recreation and surfaced explicitly as
warnings/diagnostics.

## Snapshot Model
Snapshots are the versioned unit of current-state capture.

Practical snapshot behavior:
- point the mapper at configured roots and relevant world slices
- crawl current assets and codegen-managed software truth
- map each asset by identity + payload hash
- reuse payloads by hash when they already exist
- create a new snapshot record that points at:
  - asset identities
  - payload hashes
  - crystals
  - synthetic/codegen-managed units
  - conduit world slices
  - optional mutation manifests
  - bootstrap instructions

This gives:
- smart reuse by hash
- snapshot-level versioning
- no forced giant diff engine

## Transactions
Runtime persistence traffic should be expressed as transaction-shaped objects.

Examples:
- asset transactions
- crystal upsert transactions
- activation/deactivation transactions
- mutation research transactions
- conduit snapshot transactions
- bootstrap snapshot transactions

Current design preference:
- transactions should be plain data objects
- dataclass-shaped payloads are a good fit
- transaction outputs should be emitted as ordered lists of raw data objects
  that the host can persist or route however it wants

Crystallizer defines the payload shape.
The host system owns the update semantics.

## External Persistence Contract
Crystallizer should not own DB tables.

The contract is:
- JSON in
- JSON out
- transactions emitted
- adapters receive and persist them
- adapters load and return the right payloads

That means:
- the host system defines the table shapes
- callbacks/adapters satisfy the contract
- Crystallizer consumes and emits through those interfaces

This keeps persistence adapter-driven and preserves the optionality of the
pro-layer systems.

## Dependency Recovery Policy
Current intended policy:
- `uv` is the preferred and supported dependency recovery path
- `pip` is tolerated only through a user-supplied subprocess/script path
- `site-packages` contents do not need to be mirrored by default
- Crystallizer restores environment support; it does not become the package
  manager

The dependency story is:
- recover what is missing
- then restore crystals/modules

## Environment Assets And Site-Package Validation
The system should separate:

- environment/package truth
- world/module truth

That means:

### Environment/package truth
- package names
- versions
- package-distribution metadata when resolvable
- `uv.lock` as the preferred package-environment snapshot/reference asset

### World/module truth
- crystals
- synthetic modules
- physical module assets
- conduit snapshots
- mutation manifests

This matters because `uv.lock` alone cannot describe the whole world.
It only describes the package environment that the world expects to run inside.

### Site-package-backed crystals
For bind-relevant software backed by `site-packages`, the crystal should record
best-effort package association when it can, such as:
- import/module name
- distribution/package name when resolvable
- snapshot-time version as reference

On load, the system should validate:
- is the required package present?
- is the required module importable?
- are the required assets/files visible enough for the loader to proceed?

If the installed version is newer than the snapshotted version:
- that can be accepted when the module is available
- the crystal still retains the older snapshot-time version as reference truth

If the package or module is missing:
- the loader should throw
- or a user-provided repair/install path may be used if the deployment policy
  explicitly allows it

Crystallizer should not attempt to solve package auth and host-specific install
problems by itself.

### User-owned package install boundary
The intended operator split is:
- users/operators install the broad site-package environment they want
- `uv.lock` records the expected package environment
- Crystallizer validates that environment during bootstrap/load
- if prerequisites are missing, the internal loader throws

Optional/custom package install behavior is still allowed:
- users can build their own pip/uv install conduits or helper scripts
- curated agent-side install tools may exist later
- those are outside the core Crystallizer build

This keeps Crystallizer from becoming a package manager while still letting the
system reason about environment drift and missing package assets.

## Bootstrap And Restore Order
Bootstrap should be manifest-driven.

The bootstrap manifest should describe:
- what assets need to be loaded
- what crystals need to be available
- what modules should activate as synthetic modules
- what supporting dependency files exist
- what environment/package asset references exist (such as `uv.lock`)
- what conduit/world slices should be rebuilt
- what optional mutation manifests should be restored
- what bootstrap entry should run

### Internal bootstrap stance
The bootstrap used by the system is the custom loader that Crystallizer
creates and runs internally.

That loader should:
- pull DB assets
- resolve crystals
- validate environment prerequisites
- activate required modules
- rebuild frames/conduits/world slices
- throw when prerequisites are missing or inconsistent

The user/operator still has to do some real work:
- install the broad site-package environment they want available
- handle private index/auth concerns
- prepare any custom package-install behavior they want outside the default
  loader contract

This is intentional.
The system should not pretend it fully owns package management.

Practical restore flow:
1. load snapshot / bootstrap payload
2. validate environment/package prerequisites (optionally using package assets
   like `uv.lock` as reference)
3. restore crystals
4. restore synthetic modules into `sys.modules`
5. restore MutationResearch state when present
6. bind or rebuild the conduit-facing spell world that depends on those
   modules
7. restore conduit-level config, links, permissions, and other world-slice
   mechanics
8. continue runtime activation

If required package assets are missing:
- throw
- or later, invoke a user-provided/custom repair path when deployment policy
  explicitly allows it

The loader validates and rebuilds.
It does not own pip/uv control as part of the crystallizer build itself.

## MutationResearch Relationship
MutationResearch is a separate system.

The clean split is:
- `MutationResearch` owns:
  - lineage/version/fork semantics
  - research lanes
  - head movement and promotion
  - merge/rebase/fork semantics later
- `Crystallizer` owns:
  - source/module persistence
  - artifact ids
  - transaction persistence
  - restore/bootstrap support

At runtime:
- MutationResearch emits mutation transaction data into Crystallizer
- Crystallizer persists it

At startup:
- Crystallizer loads persisted mutation payloads
- the real MutationResearch system is rehydrated from that data when present

### Conduit ownership
Mutation is conduit-owned.

That means:
- mutation access is gated through conduits
- mutation manifests travel with conduit snapshots when present
- lineage/version semantics belong to MutationResearch, not to Crystallizer
  directly

The current code already leans this way:
- stable lineage identity
- concrete spell versions under that lineage
- promotion of new versions
- but no full git-style branch/head/rebase/merge model yet

## Branching, Forking, And World Merge
Different collaboration modes need different semantics.

### Same-conduit collaboration
- shared live world
- multiple agents may work against the same conduit
- this wants transaction and ownership discipline

### Different-conduit collaboration
- parallel world evolution
- multiple conduits may diverge from a common base snapshot
- this is closer to git-style branch/worktree behavior

Useful concepts to borrow:
- branch
- head
- merge
- rebase
- fork

But the unit is not only file text.
It is also:
- module truth
- bind truth
- conduit world topology
- mutation lineage truth

### Current direction
- research-only branching may remain under one lineage until it is promoted
- live coexistence inside one conduit likely requires distinct bind address
  differentiation, usually through a new binding name or new addressable
  surface
- true long-lived forks that are meant to coexist as separate live futures
  should likely become new lineages

String diffs are not the hard part.
The harder merge layer is world merge:
- bind collisions
- spell identity selection
- permissions
- link topology
- mutation head selection
- which world slice is authoritative

## Collaboration Modes
The system should be comfortable with at least three modes:

### Shared-conduit mode
- many agents
- one conduit
- tight live collaboration

### Forked-conduit mode
- many agents
- separate conduits from one base snapshot
- isolated experimentation
- later merge/rebase back

### Integration-conduit mode
- one target conduit
- reintegration point for promoted work

That keeps the design world-first and makes large-system collaboration easier
to reason about.

## Mixed Physical And Synthetic Worlds
The system must support mixed worlds such as:
- physical `.py` modules
- synthetic modules created through codegen
- physical modules with synthetic modules "strapped" to them

This is one of the main reasons for crystals:
- we want the synthetic-module layer retained
- we want dependencies mapped
- we want conduit reloads to reactivate the module world before binds

That is a stronger and clearer purpose than asking crystals to be a full live
spell mirror.

## Package Shape
The current agreed package shape reflects these concern splits:

- top level:
  - `crystallizer.py`
  - `spell_crystal.py`
  - `synthetic_module.py`
- `configuration/`
- `crystal_analysis/`
- `asset_management/`
- `crystal_loader/`

This matters because the subsystem is no longer trying to split V1, V2, and V3
into separate package trees.

## Main Rules Going Forward
1. Keep runtime truth in Melder/runtime objects.
2. Keep local dynamic construction first-class in Rift.
3. Keep source truth in Crystallizer.
4. Keep bind as the promotion boundary from local construction into durable
   world truth.
5. Treat conduit snapshots as the primary reload unit.
6. Keep synthetic modules first-class for retained codegen and conduit rebuilds.
7. Keep MutationResearch graph semantics out of crystallizer runtime logic.
8. Keep persistence adapter-driven.
9. Keep environment/package truth separate from world/module truth.
10. Keep dependency recovery simple and `uv`-first as a package-environment
   asset/reference layer.
11. Keep user/operator-owned package installation and custom install loaders
   outside the core crystallizer build.
12. Keep files optional as projections, not mandatory as primary truth.

## Summary
In one sentence:

Crystallizer is the source-truth, persistence, and recovery bridge for
synthetic modules and other managed software artifacts in Melder; Rift can own
local synthetic modules freely, bind is the promotion boundary into durable
world truth, conduit snapshots are the primary reload unit, and
MutationResearch remains a separate conduit-owned graph-semantics system whose
state travels with those world slices instead of being reimplemented inside
Crystallizer, while environment/package truth (for example `uv.lock`) remains a
separate asset/reference layer that the internal loader validates rather than
manages directly.
