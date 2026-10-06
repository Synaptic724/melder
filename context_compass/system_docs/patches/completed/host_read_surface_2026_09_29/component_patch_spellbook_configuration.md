# component_patch_spellbook_configuration

## Metadata
- Patch ID: host_read_surface_2026_09_29
- Component: Spellbook Configuration and System State (SpellbookConfiguration)
- Status: archived without promotion (owner turn-in, 2026-09-29)
- Owner: user (agent melder_0)
- Created: 2026-09-29T21:27:17Z
- Updated: 2026-09-29T22:26:28Z

## Component Purpose and Boundary
- Current boundary: the rich per-Book configuration; its target frame is fixed at construction and a Spellbook
  refuses a supplied configuration that names another frame; freeze seals every property.
- Target boundary: unchanged, plus two reads.

## Before/After Behavior Summary
- Before: the target frame and the freeze state were readable only as `_aether_frame` and `_frozen`.
- After: `aether_frame` returns the frame name given at construction; `frozen` returns whether the configuration
  has been frozen.

## Interface Deltas
- Inputs: none.
- Outputs: `str`; `bool`.
- Error semantics: RuntimeError once the configuration is cleaned.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. `frozen` reads under the configuration's lock, which `freeze()` holds when it flips the flag.
2. `aether_frame` is immutable after construction; no lock is needed.

## Validation Expectations
- Test/validation item: default frame "default"; a named frame round-trips; frozen False then True after
  `freeze()`/`finalize()`; cleaned configuration raises.
- Evidence target: artifacts/host_read_surface_20260929/ logs.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: landed at 0.2.8208 as specified (`SpellbookConfiguration.aether_frame` and `frozen`; src/melder/aether/spellbook/configuration/spellbook_configuration.py:219-269), with the tests this patch lists.
  Not promoted into the canonical system documents: the owner turned the lane in first.
- Remaining risks: none known.
- Next entrypoint: `src/melder/aether/spellbook/configuration/spellbook_configuration.py`.
- Promotion owner: tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
