# architecture_patch

## Metadata
- Patch ID: spellspace_meld_abc_split
- Status: draft
- Owner: codex
- Created: 2026-05-30T10:46:42Z
- Updated: 2026-05-30T10:46:42Z

## Patch Scope and Non-Goals
- Objective:
  - Convert `Meld` into the shared abstract runtime core.
  - Make `ConduitMeld` and `SpellSpaceMeld` the concrete front-door classes.
  - Move caller-specific state and runtime-routing behavior out of the base.
- Non-goals:
  - No Phase 10-12 executor rewrite in this patch.
  - No transfer/pooling semantics rewrite in this patch.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| meld | modify | Split shared core from caller-specific hot paths. | conduit, spell_space |
| conduit | modify | Instantiate `ConduitMeld` instead of generic `Meld`. | meld |
| spell_space | modify | Instantiate and own `SpellSpaceMeld` with spellspace-local and owner-conduit storage surfaces. | meld |

## Interface and Boundary Deltas
- Boundary delta 1:
  - `Meld` becomes an abstract/shared runtime base instead of the concrete
    conduit front door.
- Boundary delta 2:
  - `ConduitMeld` owns conduit-caller state.
  - `SpellSpaceMeld` owns spellspace-caller state.
- Interface delta 1:
  - `Conduit` constructs `ConduitMeld`.
- Interface delta 2:
  - `SpellSpace` constructs or owns `SpellSpaceMeld`.

## Cross-Component Invariants
- Invariant 1:
  - Shared spell lookup, structural gating, contract revalidation, and
    compiler-system access stay in the abstract base.
- Invariant 2:
  - `SpellSpaceMeld` has direct access to both spellspace-owned creations and
    owner-conduit creations.
- Invariant 3:
  - `ConduitMeld` must not depend on spellspace-owned creations as its primary
    runtime store.

## Migration and Rollout Order
1. Define base-class attrs and abstract front-door/runtime-routing methods.
2. Reduce `ConduitMeld` to conduit-specific state and behavior only.
3. Reduce `SpellSpaceMeld` to spellspace-specific state and behavior only.
4. Rewire conduit and spellspace construction to instantiate the concrete
   classes.

## Rollback Strategy
- Rollback trigger:
  - The new class/state split cannot parse cleanly or leaves runtime
    construction inconsistent.
- Rollback steps:
  - Revert the ABC/class split and construction rewiring files only.
- Post-rollback verification:
  - `py_compile` the reverted touched files.

## Validation Expectations and Evidence Plan
- Validation item 1:
  - Narrow syntax validation for touched meld/conduit/spellspace files.
- Evidence source 1:
  - `python -m py_compile <touched files>`

## Ticket Coverage Map
- Epic:
  - `tickets/epics/2026-05-27_spellspace_sharded_runtime_ownership_epic.md`
- Story:
  - none
- Tasks:
  - `tickets/tasks/2026-05-30_start_spellspace_meld_split_task.md`

## Unknowns and Decision Requests
- UNKNOWN:
  - Whether the base should share hot caches across both concrete front-door
    instances or leave them per-instance in this slice.
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - Opened the ABC/class-split patch lane.
- What remains:
  - The code refactor itself.
- Next entrypoint:
  - `src/melder/aether/conduit/meld/meld.py`
