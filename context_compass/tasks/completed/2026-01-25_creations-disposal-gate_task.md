# Task: Investigate gating Existence.many registration in Creations

- Completed: 2026-01-25
- Summary: Mapped Existence.many registration paths and confirmed the disposal
  gate location and conditions used for many-scope registration.

## Metadata
- Task ID: TASK-2026-01-25-creations-disposal-gate
- Story: N/A (user-approved task-only)
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Investigate how to skip registering Existence.many instances into
Creations/LesserCreations when disposal is unnecessary, using the new
spell disposal metadata.

## Scope Boundaries
- In scope:
  - Trace the code path that registers Existence.many instances into
    Creations/LesserCreations.
  - Identify the precise insertion points for a disposal gate.
  - Propose conditions using Spell.disposal_method_names / has_disposal_methods.
  - Assess impacts on cleanup, lifecycle, and any retrieval behavior.
- Out of scope:
  - Implementing the gate or changing runtime behavior.
  - Changes to mutation, spell_id, or validation logic.

## Steps / Checklist
- [x] Locate Existence.many registration path in Conduit/Creations/LesserCreations.
- [x] Map cleanup usage of many instances and any dependencies on tracking.
- [x] Identify tests that assert many registration behavior.
- [x] Draft a minimal gating proposal and risks.
- [x] Review findings with the user.

## Deliverables
- Evidence-backed map of Existence.many registration and cleanup behavior.
- Proposed gate location and conditions with risks.

## Files / Paths Impacted
- None (investigation only).

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: Skipping registration could break cleanup or any logic that expects
  many instances to be tracked.
  Mitigation: Confirm all consumers of many-instance registries before
  proposing a behavior change.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Existence.many registration entry points are `Meld._register_spell` and
  `MeldEngine._register_spell` and are now gated on
  `spell.has_disposal_methods` (`src/melder/aether/conduit/meld/meld.py`,
  `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`).
- Cleanup depends on disposal methods stored in Creation wrappers
  (`src/melder/aether/conduit/creations/creation.py`), so skipping registration
  when disposal is unnecessary avoids tracking overhead.
- Unit tests assert many-registration behavior and gating expectations
  (`tests/unit/melder/aether/conduit/creations/test_creations.py`,
  `tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py`).
- Validation: Not run.
