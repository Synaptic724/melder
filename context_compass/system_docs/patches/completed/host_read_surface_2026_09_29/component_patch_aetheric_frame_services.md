# component_patch_aetheric_frame_services

## Metadata
- Patch ID: host_read_surface_2026_09_29
- Component: AethericFrame Services (AethericFrame, AethericFrameConfiguration)
- Status: archived without promotion (owner turn-in, 2026-09-29)
- Owner: user (agent melder_0)
- Created: 2026-09-29T21:27:17Z
- Updated: 2026-09-29T22:26:28Z

## Component Purpose and Boundary
- Current boundary: a frame owns its posture (`frame_configuration`) and, when the posture shares it, the
  frame-wide rich Spellbook configuration bound by the first conjuring Book (`_configuration`).
- Target boundary: unchanged, plus two reads.

## Before/After Behavior Summary
- Before: the shared rich configuration and the posture's freeze state were readable only as `_configuration`
  and `_frozen`.
- After: `AethericFrame.shared_spellbook_configuration` returns the bound rich configuration while the posture's
  `shared_framewide_spellbook_configuration` is True, else None (also None before any Book binds one);
  `AethericFrameConfiguration.frozen` returns whether the posture is frozen (settled).

## Interface Deltas
- Inputs: none.
- Outputs: `Optional[SpellbookConfiguration]`; `bool`.
- Error semantics: RuntimeError once the frame or the posture is cleaned (`check_cleaned`).

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. `shared_spellbook_configuration` mirrors `Spellbook._get_configuration_from_aether`: the sharing flag gates the
   answer, so a configuration bound under an earlier posture is never reported as shared.
2. `frozen` reads under the posture's own lock, like its other properties.

## Validation Expectations
- Test/validation item: sharing off -> None; sharing on after conjure -> the Book's configuration object;
  posture frozen False before settlement and True after; cleaned objects raise.
- Evidence target: artifacts/host_read_surface_20260929/ logs.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: landed at 0.2.8208 as specified (`AethericFrame.shared_spellbook_configuration` and `AethericFrameConfiguration.frozen`; src/melder/aether/aetheric_frame/aetheric_frame.py:591-624 and aetheric_frame_configuration.py:1500-1522), with the tests this patch lists.
  Not promoted into the canonical system documents: the owner turned the lane in first.
- Remaining risks: none known.
- Next entrypoint: `src/melder/aether/aetheric_frame/aetheric_frame.py` (`frame_configuration` neighbourhood).
- Promotion owner: tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
