# component_patch_conduit_runtime

## Metadata
- Patch ID: host_read_surface_2026_09_29
- Component: Conduit Runtime (Normal and Lesser)
- Status: archived without promotion (owner turn-in, 2026-09-29)
- Owner: user (agent melder_0)
- Created: 2026-09-29T21:27:17Z
- Updated: 2026-09-29T22:26:28Z

## Component Purpose and Boundary
- Current boundary: a conduit resolves through the Spellbook it was built with: the conjuring Book for a root,
  the root's Book for a lesser; `upgrade_to_normal` rebinds the upgraded conduit to its new Book.
- Target boundary: unchanged, plus one read (the mirror of `Spellbook.conduit`).

## Before/After Behavior Summary
- Before: the Book was readable only as `_spellbook`.
- After: `Conduit.spellbook` returns it, borrowed.

## Interface Deltas
- Inputs: none.
- Outputs: `Spellbook`.
- Error semantics: RuntimeError once the conduit is cleaned.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none. Reading the property keeps nothing alive.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Not on the meld path; a property adds no per-meld work.

## Validation Expectations
- Test/validation item: root -> its Book (and `book.conduit is root`); lesser -> the root's Book; cleaned conduit
  raises.
- Evidence target: artifacts/host_read_surface_20260929/ logs.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: landed at 0.2.8208 as specified (`Conduit.spellbook`; src/melder/aether/conduit/conduit.py:1910-1937), with the tests this patch lists.
  Not promoted into the canonical system documents: the owner turned the lane in first.
- Remaining risks: none known.
- Next entrypoint: `src/melder/aether/conduit/conduit.py`, the Properties region after `name`.
- Promotion owner: tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
