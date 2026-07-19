# Crystallizer V2 Synthetic Module Graph And Requirements

## Metadata
- Artifact ID: ART-2026-04-26-crystallizer-v2-synthetic-module-graph-and-requirements
- Parent Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: active
- Created: 2026-04-26T15:23:20Z
- Updated: 2026-04-26T19:17:32Z

## Purpose
Capture the V2 direction for Crystallizer after the Base V1 storage contract.

V1 is enough to preserve one spell-backed source representation through:
- `spell_crystal_id`
- one `SpellCrystal`
- one current raw string or module string

V2 begins when a single stored representation is no longer enough because:
- synthetic code depends on other synthetic code
- file-backed code depends on imports that matter for recovery and later
  editing
- agents want to save and restore whole synthetic systems, not isolated blobs

This artifact exists to define that V2 step clearly without turning Crystallizer
into a package manager or a full workflow engine.

## V2 Thesis
Crystallizer V2 should maintain a **synthetic module graph** and a
**requirements view** over that graph.

That means:
- synthetic Python code units become first-class stored modules
- those modules may depend on other synthetic modules
- those modules may also depend on userland or external imports
- Crystallizer should understand and preserve those relationships
- later runtime systems can restore those graphs into a conduit/world

The key shift from V1 is:
- V1 stores one representation
- V2 stores one representation **plus its relationship graph**

## Why V1 Is Not Enough
V1 is good for:
- single codegen-backed assets
- single file-backed module snapshots
- simple source retrieval

V1 is not enough for:
- codegen A depending on codegen B, C, and D
- codegen B depending on F, G, and H
- storing a reusable agent-built subsystem made from many synthetic units
- understanding what imports matter for later restoration or promotion

So the real V2 problem is not "store more strings."
It is:

**preserve source authority plus dependency truth well enough that agent-built
software systems can be restored later.**

## V2 Source Authority Classes
V2 should distinguish at least these authority classes:

### `synthetic_module`
- agent-authored codegen module
- no file-first authority required
- source lives primarily as a crystallized representation

### `userland_module`
- local project code under user control
- file-backed authority
- crystallizer stores module text and metadata, not just a class body

### `mirrored_external_module`
- external package or wheel-backed Python source that the user is willing to
  catalog or store
- not primarily agent-authored
- still may need to be understood for restore/editing flows later

### `binary_or_opaque_dependency`
- native extension, opaque artifact, or non-source dependency
- not module-text-first
- cannot be treated like synthetic or userland Python source

These classes matter because the restore and materialization semantics differ.

## Synthetic Modules As First-Class Units
The main V2 conceptual leap is:

**A retained codegen spell is no longer just a saved snippet.  
It is a synthetic module.**

That means a synthetic unit should have:
- module identity
- source text
- known exports
- known internal dependencies
- known external import references

This matters because the system wants to support:
- saved tools
- reusable helpers
- agent-authored runtime systems
- recovery of those systems into a conduit later

The synthetic-module experiment now gives this idea a concrete floor:
- a synthetic package shell can be created fully in memory
- synthetic submodules can be created fully in memory
- those module objects can be inserted into `sys.modules` before execution
- later synthetic units can import them by normal Python import syntax
- the synthetic package graph can then be removed again deterministically

So synthetic modules are no longer only a theoretical direction.
They are a demonstrated runtime capability.

## Synthetic Module Graph
The synthetic side of V2 should be graph-shaped, not flat.

If:
- synthetic module A depends on B, C, and D
- B depends on F and G
- C depends on H

then Crystallizer must preserve that structure honestly.

That does **not** force one runtime load strategy yet.
It only means the stored truth should remain graph-shaped.

The graph is important because later systems may want to:
- restore the whole graph
- restore one subgraph
- inspect what a saved toolset depends on
- promote part of a graph into file-backed userland later

The synthetic-module bench also sharpened one practical point:
- if the graph is package-shaped, package shells and submodules should be
  treated as real nodes in that graph
- not just the leaf exports

## V2 Record Direction
Without overcommitting to exact implementation, V2 likely needs at least these
conceptual records:

### `SpellCrystal`
Still the base stored source unit, now extended enough to represent a synthetic
module rather than just a raw standalone blob.

Key V2 additions:
- `module_name`
- `exports`
- `internal_dependency_names`
- `external_import_names`
- `authority_class`

### `SpellCrystalGraph`
Represents one saved multi-unit synthetic system or connected subgraph.

Conceptual fields:
- graph id
- member crystal ids
- root crystal ids
- dependency edges
- graph metadata

### `RequirementsView`
Represents what external environment support the graph expects.

This is not package installation history.
It is a recovery and runtime-support view.

### `PersistenceTableContract`
Represents the external persistence-table shape that adapters must satisfy.

This is important because the current direction is not:
- "Crystallizer invents your DB schema"

It is:
- the user or host system defines specific table shapes
- adapters read and write those table shapes
- Crystallizer consumes those tables through interfaces

So table shape belongs to the external storage contract, not to ad hoc runtime
guessing.

## Synthetic Module Bench Result
The experimentation bench established a concrete source-backed baseline for the
V2 direction.

What the bench did:
- defined a `SyntheticModule` as a `ModuleType` subclass
- defined a minimal materializer/loader
- created:
  - one synthetic package shell
  - one synthetic base module
  - one synthetic feature module depending on the base module
  - one synthetic consumer module importing the feature module
- inserted those modules into `sys.modules` before execution
- imported the dependent modules through normal Python import syntax
- instantiated and used exported objects
- removed the graph from `sys.modules` afterward

What that proved:
- package-shaped synthetic modules can work in one process
- later synthetic units can consume them through normal import syntax
- early registration before `exec(...)` is enough for the tested dependent
  graph
- deterministic cleanup is possible in the bounded case

What it did not yet prove:
- circular import handling
- scope-separated local/shared synthetic module spaces
- restoration from DB into a fresh runtime
- partial graph reload or version switching
- package-materialization to files

So the bench should be treated as:
- proof of the baseline synthetic-module import direction
- not proof that the whole V2 design is complete

## AST Import Investigation
V2 should use AST to inspect imports and shape rather than relying only on raw
strings or `pip freeze`.

AST investigation is important because it can reveal:
- direct import statements
- imported module roots
- imported symbol forms
- whether the unit is likely self-contained
- whether the target relies heavily on module-level siblings

The AST pass should answer:
- what other synthetic modules are referenced by name
- what external imports appear in code
- what file-backed local modules are referenced
- what the likely target span and local context are

This is the structured import understanding layer that V1 does not have.

## Two Dependency Classes
V2 should not blur all dependencies together.

### 1. Internal managed dependencies
These are under the system's own control:
- synthetic modules
- userland modules
- later maybe mirrored external modules the user chooses to manage directly

These belong to Crystallizer's graph story.

### 2. Environment dependencies
These are required for runtime support:
- stdlib
- installed distributions
- wheels
- package-level runtime dependencies not owned as first-class internal assets

These belong to the requirements view.

This distinction matters because Crystallizer is not supposed to become a full
package manager.

## Requirements View
The requirements side of V2 should not be install history.
It should be a **runtime support manifest**.

That means:
- `pip freeze` alone is not enough
- AST import inspection alone is not enough

The useful V2 direction is:
- use AST to discover what imports the saved code actually uses
- combine that with environment knowledge when needed
- produce a requirements view for restoration and later execution

## Dependency Recovery Policy
The current intended dependency policy is:

- `uv` is the preferred and fully supported dependency snapshot and recovery
  path
- `pip` is a tolerated fallback only when the user provides an explicit script
  or subprocess path
- Crystallizer should not become a package manager
- Crystallizer should only know enough to:
  - understand what the graph needs
  - decide what is missing
  - trigger the configured recovery path

This means:
- `uv` is the clean first-class story
- `pip` is allowed, but made intentionally less convenient

## `uv`-First Direction
`uv` is preferred because it gives the system a much cleaner recovery model for
environment truth.

The intended shape is:
- when dependency state should be preserved, Crystallizer can snapshot the
  environment requirement state through a `uv`-oriented lock/sync contract
- when a graph is restored later, Crystallizer can ask the configured `uv`
  recovery adapter to restore that requirement state before synthetic modules
  are materialized

This keeps the environment story much simpler than treating `pip freeze` alone
as the whole truth.

## `pip` Fallback Direction
`pip` is still possible, but not the primary experience.

The intended rule is:
- if the user wants `pip`, they provide an explicit script or subprocess path
- Crystallizer can call that script when dependency recovery is needed
- Crystallizer itself still does not become a package manager

That makes `pip`:
- possible
- not the preferred first-class workflow

## Site-Packages Storage Boundary
Current direction:
- Crystallizer does **not** need to store `site-packages` contents by default
- external packages can remain installed/recovered through the environment
  adapter path
- local or special cases can still be cataloged later if the user explicitly
  wants that, but it is not the primary story

That keeps the dependency model lighter:
- store graph truth
- store requirements truth
- recover packages when needed
- do not mirror the entire installed environment unless there is a real reason

This requirements view should support at least two conceptual modes:

### `exact_environment`
- closer to "match the environment this was built in"
- can be informed by a `uv`-first environment snapshot and, secondarily, by
  `pip`-compatible requirement views when needed

### `minimal_requirements`
- closer to "only what this synthetic graph actually uses"
- driven more by AST/module analysis

V2 does not need to finalize which mode is always preferred, but it should keep
the distinction explicit.

## What V2 Is Not
V2 is not:
- a general package manager
- a replacement for pip or uv
- a full install-history tracker
- a DB schema or table creator
- a workflow/orchestration engine
- a debugger/probe system

Those concerns belong elsewhere.

V2 is:
- graph-aware source preservation
- graph-aware source recovery support
- graph-aware requirements understanding
- adapter-facing persistence contract consumption

## External Table-Shape Contract
The current intended persistence model is:
- users define the persistence table shapes
- Crystallizer does not create those tables for them
- adapters are responsible for reading and writing those shapes
- Crystallizer only consumes and emits interfaced objects or JSON payloads that
  correspond to those adapter-backed table contracts

So the V2 contract should assume:
- there is a table or table-family for crystal units
- there is a table or table-family for graph relations
- there is a table or table-family for requirement snapshots if that feature is
  enabled

But Crystallizer itself only sees:
- interface objects
- JSON payloads
- adapter methods

This keeps the core clean while still making table shape a concrete
expectation.

## Relationship To File Materialization
V2 does not force one answer yet on whether restored synthetic graphs must stay
in memory or materialize to files.

What it does require is that the stored truth be good enough to support either:
- synthetic restoration
- later file-backed materialization

That is why preserving:
- source text
- graph edges
- imports
- exports

matters more than prematurely choosing one load mechanism.

## V2 Summary
If V1 is:
- one stored source-bearing representation

then V2 is:
- one stored source-bearing representation
- plus the graph and import truth needed to restore interdependent synthetic
  systems later

In one sentence:

Crystallizer V2 should treat retained codegen as a synthetic module graph,
investigate imports through AST, separate internal managed dependencies from
environment requirements, and preserve enough source and graph truth that later
systems can restore those agent-built software structures into a live world.

## Source Anchors
- `tests/experimentation/synthetic_module_import_testbench.py`
- `src/melder/aether/nexus/rift/codegen_system/codegen_system.py`
- `src/melder/aether/nexus/rift/codegen_system/codegen_transaction_context.py`
- `src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py`
- `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
