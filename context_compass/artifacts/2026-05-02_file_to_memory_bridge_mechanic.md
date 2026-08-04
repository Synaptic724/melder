# File To Memory Bridge Mechanic

## Metadata
- Artifact ID: ART-2026-05-02-file-to-memory-bridge-mechanic
- Parent Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: active
- Created: 2026-05-02T10:12:13Z
- Updated: 2026-05-03T16:22:08Z

## Purpose
Capture the specific crystallizer mechanic where file-backed software can move
into in-memory software truth and later be projected back out again.

This artifact is narrower than the broader crystallizer philosophy. It exists to
state one important bridge clearly:

- physical file -> in-memory managed software truth
- in-memory managed software truth -> physical file projection

## Foundation Rules
The current practical foundation should be:

- all files are assets
- codegen code first becomes a `SyntheticModule`
- when code becomes bind-relevant / spell-relevant, it gets a `SpellCrystal`

So the layers are:

- `Asset`
  - universal storage / transport / checksum / mapping layer
- `SyntheticModule`
  - live in-memory code embodiment
- `SpellCrystal`
  - spell-facing managed software-truth layer for bound code and later
    mutation-ready mapping

`SpellCrystal` may either:
- hold inline module payload directly
- or point to asset-backed payload and dependency assets

If inline payload is stored in transport form, base64 is valid as long as the
activation path decodes it back into canonical module source text before
building the `SyntheticModule`.

## Managed Python Truth
For this lane, a managed Python software unit should be understood as having
three valid embodiments:

- physical `.py` file
- `SpellCrystal`
- `SyntheticModule`

These are not three unrelated things. They are three forms of the same managed
Python software truth.

That means:
- the physical `.py` is still an asset
- a physical `.py` can become a `SpellCrystal`
- a `SpellCrystal` can activate as a `SyntheticModule`
- a `SyntheticModule` can later project back to a physical `.py`

The important design consequence is:
- `.py` is both a physical asset/projection and a spell-crystal-capable source
  unit
- `.pyc`, `.pyi`, `.pyd`, `.so`, `.dylib`, configs, and other companions are
  supporting assets around that Python truth, not the primary mutable source
  authority

## Core Mechanic
One clear `SpellCrystal` creation path happens during bind from a physical
Python file.

When bind receives something file-backed, the system should be able to:

1. identify the owning file/module
2. read the full module source
3. preserve the existing binding/configuration shape
4. convert that file-backed software truth into the in-memory managed form
5. link the resulting spell/runtime back to that durable software truth

This means the system should support a bidirectional transformation:

- `file -> in-memory software truth`
- `in-memory software truth -> file projection`

## Why This Matters
If this works cleanly, then the system gets the ephemeral mechanics it wants:

- files are not the only authority
- files can be ingested into memory-first managed truth
- memory can remain the primary working representation
- files can later be projected back out again

This is important because Crystallizer is not only for codegen-born software.
It is also the bridge for taking existing file-backed software and converting it
into memory-first managed software truth.

## Bind Path
For file-backed software, one clean bind path is:

1. bind sees a class/function/object originating from a physical module
2. bind or its supporting profile metadata identifies the owning file/module
3. the full module source is read, not just the local class/function body
4. the module/configuration/binding shape is preserved
5. the system creates:
   - a `SyntheticModule` as the live in-memory software unit
   - and/or a `SpellCrystal` as the durable software record, depending on the
     current durability transition
6. the bound spell links back to that software truth

The important rule here is the same one already established for file-backed
software truth:
- keep the full module string
- not only the local symbol body

That preserves surrounding imports, sibling helpers, constants, and local
layout, which later mutation or projection work may need.

## Relationship Between SyntheticModule And SpellCrystal
This mechanic implies the following split:

- `SyntheticModule`
  - the live in-memory software unit
  - what the runtime can activate/import/work with

- `SpellCrystal`
  - the durable record created when software truth becomes persisted or made
    durable enough to survive intact

The bridge is not:
- “store some text somewhere and hope later”

It is:
- take file-backed software truth
- normalize it into managed software truth
- let it live in memory-first form
- let it project back out later when needed

## File Projection Direction
The reverse move matters too.

If the system is perfect, then:
- filesystem is one projection
- in-memory graph/software truth is another projection

That means memory-first software can later be written back out to files without
losing the real module/config/binding semantics.

This is not the same thing as “save arbitrary runtime state.”
It is specifically about software truth:
- module text
- binding/configuration shape
- identity/provenance

## Common Workflow Patterns
The common workflow patterns we should explicitly support are:

### 1. `codegen -> py`
- agent creates code through codegen
- managed software truth starts as `SyntheticModule`
- if bound, it receives a `SpellCrystal`
- the result is projected to a physical `.py`

This is the path where a purely in-memory/generated unit later becomes a normal
file-backed software asset.

### 2. `py -> codegen -> py`
- start from an existing physical `.py`
- treat the `.py` as an asset-backed source unit
- move through `SpellCrystal` and `SyntheticModule` forms for iteration when
  needed
- project the updated result back to the physical `.py`

This is the path where existing file-backed software is iterated through the
runtime without losing its file-backed form.

### 3. `codegen alone`
- create and keep the software truth in `SyntheticModule` form only unless it
  later becomes bound
- never require file projection

This is the sessional or memory-first path where code remains runtime-native.

These three patterns should be considered the normal supported software-truth
flows.

### Binding as the promotion boundary
The important promotion boundary is:

- codegen or file-backed Python can exist without a `SpellCrystal`
- once the code becomes bind-relevant / spell-relevant, create or attach the
  `SpellCrystal`

That keeps `SpellCrystal` centered on bound code instead of forcing every piece
of code or every file-backed module into spell-truth state immediately.

For deliberate synthetic modules, another consequence is:
- their chosen module names should be tracked in a managed
  `synthetic_module_imports` set
- codegen import ACLs can then allow those names explicitly
- generic scratch namespace code should not gain the same importability by
  accident

## Non-Default Direction
The following direction should not be treated as a normal default pattern yet:

- `py -> codegen` and then removing the physical file entirely

That may become valid later, but it pushes the system toward a broader
fileless-asset policy that is outside the current narrow bridge mechanic. For
now, it should be treated as a later explicit mode rather than a baseline
expectation.

## Supporting Asset Rule
Around those Python-truth workflows:

- `.py`
  - asset and primary managed Python truth
  - can be physical, crystallized, synthetic, or mixed
- `.pyc`
  - derived cache artifact only
  - not primary mutation truth
- `.pyi`
  - companion typing/interface asset
  - useful to preserve, not primary executable truth
- `.pyd` / `.so` / `.dylib`
  - binary dependency assets
  - may support imported/bindable exports, but are not the primary mutable
    Python source truth

### Environment package assets
Some supporting dependencies are not local source files or synthetic modules at
all. They come from the installed environment.

For those cases:
- `uv.lock` is a useful environment/package asset reference
- site-package-backed modules should be detected and recorded as environment
  dependencies
- the internal loader should validate that those packages/modules are present
- if the environment is missing something required, the loader should throw

The package environment is therefore a prerequisite layer around the bridge
mechanic, not part of the primary mutable Python source truth itself.

So the bridge mechanic should center on `.py` while still allowing companion
assets to be mapped and transported around it.

## Physical To Synthetic Morphing As A Later Enhancement
It is still desirable if the system can eventually:
- ingest physical file-backed software into managed in-memory software truth
- later project that truth back out to physical files again

That would support a more ephemeral system style where:
- the live working truth can become memory-first
- a concrete centralized bootstrap remains the preferred authority
- physical files become a projection rather than the only source of truth

But this should be treated as a later enhancement rather than an immediate
first implementation target.

Reasons:
- package/module identity mapping must remain coherent
- import/package behavior must remain correct when moving between physical and
  synthetic forms
- file projection needs a clear mapper from managed truth back to the
  filesystem layout
- `.pyc` and related import/runtime projection details add additional
  complications
- physical-path expectations and module provenance need to stay honest

So the important design note is:
- the file <-> memory bridge is a good mechanic
- but full physical-to-synthetic morphing and back should be considered an
  enhancement layer after the simpler memory-first synthetic/crystal mechanics
  are solid

## Design Pressure
This mechanic reinforces several important crystallizer design pressures:

- full module truth matters for file-backed software
- codegen-born and file-born software should both be able to enter the same
  memory-first managed world
- file projection is a later output format, not necessarily the primary truth
- bind is one of the legitimate transitions where durable software truth can be
  created

## Summary
In one sentence:

The file-to-memory bridge mechanic lets bind take file-backed software,
normalize it into in-memory managed software truth, preserve its real module and
binding shape, and later project that software back to files again when needed,
while recognizing three normal workflow patterns (`codegen -> py`,
`py -> codegen -> py`, and `codegen alone`) and treating full
physical-to-synthetic file removal as a later explicit enhancement once mapping
and projection semantics are solid.
