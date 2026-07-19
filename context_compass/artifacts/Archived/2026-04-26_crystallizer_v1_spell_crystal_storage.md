# Crystallizer V1 Spell Crystal Storage

## Metadata
- Artifact ID: ART-2026-04-26-crystallizer-v1-spell-crystal-storage
- Parent Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: active
- Created: 2026-04-26T15:23:20Z
- Updated: 2026-04-26T15:23:20Z

## Purpose
Capture the Base V1 storage contract for Crystallizer.

This artifact is intentionally narrower than the broader philosophy artifacts.
It only defines the first practical storage shape:
- what id a spell gets
- what record object Crystallizer stores
- what string representation is retained
- how spells and agents read it back
- how the store maintains and updates those records

The point of V1 is not to solve all mutation and promotion mechanics.
The point is to give the system one stable storage contract to build on.

## V1 Thesis
Crystallizer V1 is a string-and-module representation keeper.

It does not own:
- workflow orchestration
- comparison logic
- debugger control
- mutation strategy
- git history

It does own:
- `spell_crystal_id`
- the record store keyed by that id
- the current source representation for a spell-backed asset
- the ability to return that representation later
- the ability to replace the stored representation when later systems decide
  to update it
- the ability to upload/download those records to and from a DB later

That is the Base V1 story.

## Core V1 Handle
The stable handle returned by Crystallizer is:

- `spell_crystal_id`

This id is:
- created once when a spell-backed source representation is first crystallized
- stored on the spell
- used as the lookup key into the Crystallizer store
- stable across later representation updates for the same crystallized asset

For V1, the spell does not need to know the whole storage system.
It only needs the `spell_crystal_id` and a facade path to retrieve the stored
representation.

## Availability And Mode Gating
Crystallizer V1 is not a universal Melder runtime guarantee.

Default availability rules:
- Crystallizer is disabled in `automatic` mode.
- Spells created under `automatic` mode must not receive a
  `spell_crystal_id`.
- Crystallizer storage only activates for `dynamic` posture work.

Optional-package rules:
- Crystallizer only exists when the Crystallizer implementation class exists.
- In practice, that means this storage system should be treated as a
  `melder_pro` capability, not a base-Melder guarantee.
- If the class is absent, normal spell binding and runtime behavior still work,
  but no `spell_crystal_id` is assigned and no crystallized representation is
  maintained.

This gives V1 a clear boundary:
- no automatic-mode crystallization
- no requirement that open-source/base Melder ship Crystallizer
- no assumption that every spell can resolve source through the crystallizer
  facade

## V1 Preconditions
Before a `spell_crystal_id` can exist, all of these must be true:
- the spell/runtime posture is `dynamic`
- the Crystallizer implementation class exists
- the current workflow actually chooses to crystallize the spell-backed source
  representation

If any of those are false:
- the spell remains a normal spell with no crystallizer linkage
- the spell-facing facade should report that no crystallized representation is
  available

## Core V1 Object Model
V1 should use a dict-backed store and one main record object:

### `SpellCrystal`
`SpellCrystal` is the stored record for one crystallized spell representation.

Minimum fields:
- `spell_crystal_id`
- `source_kind`
  - `codegen`
  - `module`
- `module_name`
- `file_path`
- `target_qualname`
- `target_kind`
  - `class`
  - `function`
  - `method`
  - `runtime_object`
- `representation_string`
  - for codegen-backed assets:
    - the raw codegen string
  - for file-backed assets:
    - the entire module string
- `representation_hash`
- `target_start_line`
- `target_end_line`
- `target_loc`
- `created_from_spell_id`
- `created_from_spell_index_id`
- `created_at`
- `updated_at`
- `metadata`

### `CrystallizerStore`
V1 store shape:

- `_spell_crystals_by_id: Dict[str, SpellCrystal]`

This is the first concrete storage contract.

It is intentionally simple:
- one id
- one record
- one current string representation

If later versions/history are added, they should grow around this shape
instead of replacing it immediately.

## Source Kinds In V1
V1 only needs to distinguish two practical storage shapes:

### 1. Codegen-backed
Store:
- raw codegen string exactly as created
- namespace/module identity that created it
- any useful frame/room metadata

This is the easy case because no file has to exist first.

### 2. File-backed
Store:
- the full module string
- module name
- file path
- target location metadata inside that module

This is the important rule:
for file-backed assets, V1 stores the **entire module string**, not just the
class or function body.

That gives later systems enough context to:
- inspect surrounding imports and helpers
- understand local sibling structures
- replace the right section later
- preserve a truthful authority boundary

## Why Full Module Strings Matter
For file-backed Python, a class or function rarely exists in isolation.

The target may depend on:
- module imports
- sibling helpers
- sibling classes
- module constants
- local layout and supporting functions

So V1 should not pretend the stored source unit is only the local class body.

The V1 stored source representation for file-backed assets should be:
- the entire module string

plus:
- target line span
- target qualname
- target kind

That is enough for later agent workflows to:
- inspect the full context
- locate the target precisely
- build challengers or rewrites honestly

## Spell Facade Contract
V1 should expose a small spell-facing facade rather than making the spell own
storage itself.

The spell stores:
- `spell_crystal_id`

Then a spell-facing facade should support:
- get the `spell_crystal_id`
- resolve the `SpellCrystal`
- return the current stored representation string

Conceptually:
- spell -> facade -> crystallizer store -> `SpellCrystal`

The key V1 behavior is:
- when an agent wants the string representation for a spell-backed asset, the
  facade returns the current `representation_string`
- for file-backed assets, that string is the whole module
- for codegen-backed assets, that string is the raw codegen string
- when no `spell_crystal_id` exists, the facade must return a stable
  "not crystallized" result rather than pretending a representation exists

## V1 Maintenance Flows
### Flow 1: First crystallization of a codegen-backed asset
1. Codegen creates a new object or definition.
2. Runtime posture and package availability are checked:
   - `dynamic` mode required
   - Crystallizer class must exist
3. If either check fails, stop and do not assign a `spell_crystal_id`.
4. If both checks pass, bind or the room runtime can identify the marked
   namespace/module that created it.
5. Crystallizer allocates a new `spell_crystal_id`.
6. Crystallizer creates one `SpellCrystal` with:
   - `source_kind=codegen`
   - raw code string
   - namespace/module identity
7. The spell stores the `spell_crystal_id`.

### Flow 2: First crystallization of a file-backed asset
1. A spell is resolved to a file-backed module.
2. Runtime posture and package availability are checked:
   - `dynamic` mode required
   - Crystallizer class must exist
3. If either check fails, stop and do not assign a `spell_crystal_id`.
4. If both checks pass, Crystallizer reads the full module string.
5. Crystallizer computes target metadata:
   - qualname
   - start line
   - end line
   - LOC
6. Crystallizer allocates a new `spell_crystal_id`.
7. Crystallizer creates one `SpellCrystal` with:
   - `source_kind=module`
   - full module string
   - file path/module name
   - target metadata
8. The spell stores the `spell_crystal_id`.

### Flow 3: Agent reads the representation
1. Agent holds or discovers a spell.
2. Agent asks the spell-facing facade for the current stored representation.
3. Crystallizer resolves the `spell_crystal_id`.
4. Crystallizer returns the `representation_string`.

This is the key V1 read path.

### Flow 4: Representation update
1. A higher-level workflow decides the representation should change.
2. Crystallizer resolves the current `SpellCrystal` by `spell_crystal_id`.
3. Crystallizer replaces:
   - `representation_string`
   - `representation_hash`
   - any target metadata that changed
   - `updated_at`
4. The `spell_crystal_id` stays stable.

V1 does not need sophisticated version graphs yet.
It only needs stable id plus replaceable current record data.

### Flow 5: DB upload/download
1. Crystallizer serializes the `SpellCrystal`.
2. It writes or uploads the record to DB storage.
3. Later it can reload that same record by `spell_crystal_id`.

This is a later storage adapter concern, but the V1 record must already be
structured for it.

### Flow 6: Non-availability path
1. A spell is created in `automatic` mode, or the optional Crystallizer class
   does not exist.
2. No `spell_crystal_id` is assigned.
3. The spell-facing facade resolves to "not crystallized".
4. Runtime behavior continues normally with no crystallizer storage work.

## What V1 Deliberately Does Not Solve
V1 does not yet solve:
- full mutation workflow
- promotion workflow
- revert workflow
- file patch strategy
- runtime hot-apply strategy
- incumbent/challenger comparison
- git integration
- deep version graph modeling

Those can all be built later.
V1 only needs to preserve the current source-bearing representation in one
stable place.

It also deliberately does not try to force crystallization into every runtime:
- no automatic-mode support
- no requirement that open-source/base Melder ship the crystallizer class
- no assumption that every spell can be source-backed through this path

## Why This Shape Is Good Enough
This V1 shape is good because it gives later systems:
- one stable id (`spell_crystal_id`)
- one stable lookup object (`SpellCrystal`)
- one truthful source representation
- enough target metadata to understand the representation
- a simple dict-backed storage root

That is enough to support:
- source retrieval
- source inspection
- later module-aware iteration
- later codegen-aware iteration
- later DB persistence

without prematurely overdesigning the whole subsystem.

## Future Pressure
Later systems will likely want:
- version history
- diff/change records
- challenger/incumbent lineage
- promotion records
- revert records
- package/wheel distribution metadata

But those should grow **on top of** V1, not instead of V1.

## V1 Summary
If we reduce the whole thing to one sentence:

Crystallizer V1 gives each spell a stable `spell_crystal_id` that resolves to
one `SpellCrystal` record holding the current raw string representation of that
spell-backed asset, where codegen assets store raw code strings and file-backed
assets store full module strings plus target-location metadata.
