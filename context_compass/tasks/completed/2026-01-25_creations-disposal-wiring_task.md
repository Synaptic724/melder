# Task: Wire disposal metadata into Creation registration and gate Existence.many

- Completed: 2026-01-25
- Summary: Creation wrappers now carry disposal metadata and Existence.many
  registration is gated when no disposal methods are declared.
- Summary: Meld and MeldEngine register with disposal metadata and tests cover
  the gating behavior.

## Metadata
- Task ID: TASK-2026-01-25-creations-disposal-wiring
- Story: N/A (user-approved task-only)
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Use Spell disposal metadata to (1) annotate Creation wrappers with the
spell's disposal method list and (2) skip registering Existence.many
instances into Creations/LesserCreations when no disposal methods exist.

## Scope Boundaries
- In scope:
  - Creation metadata wiring for registered instances.
  - Gating Existence.many registration in Meld and MeldEngine.
  - Unit/component tests for the new gate and metadata wiring.
- Out of scope:
  - Changes to cleanup semantics beyond registration gates.
  - Mutation or spell_id behavior changes.
  - New configuration flags.

## Steps / Checklist
- [x] Add disposal metadata fields to Creation lifecycle (constructor or setter).
- [x] Update Creations/LesserCreations registration helpers to accept metadata.
- [x] Gate Existence.many registration in Meld and MeldEngine when
      spell.has_disposal_methods is False.
- [x] Update test stubs to include disposal metadata defaults.
- [x] Add/adjust tests for the gating behavior and creation metadata wiring.
- [x] Review docstrings/comments touched for accuracy.

## Deliverables
- Creation objects carry per-spell disposal metadata when registered.
- Existence.many registration is skipped when disposal is not required.
- Tests covering the gating and metadata wiring.

## Files / Paths Impacted
- `src/melder/aether/conduit/creations/creation.py`
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/lesser_creations.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`
- `src/melder/utilities/interfaces/interfaces.py`
- Tests in `tests/unit/melder/aether/conduit/meld/` and
  `tests/unit/melder/aether/conduit/creations/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit/meld -k many`
  - `pytest tests/unit/melder/aether/conduit/creations -k many`

## Risks / Rollback Notes
- Risk: Skipping Existence.many registration could alter transfer or
  introspection behavior that depends on Creations._many.
  Mitigation: Gate only when spell.has_disposal_methods is False and
  document the behavior change in tests.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Creation now records disposal metadata and exposes it for cleanup decisions
  (`src/melder/aether/conduit/creations/creation.py`).
- Creations/LesserCreations accept disposal metadata on registration
  (`src/melder/aether/conduit/creations/creations.py`,
  `src/melder/aether/conduit/creations/lesser_creations.py`).
- Existence.many registration is gated when `has_disposal_methods` is False in
  Meld and MeldEngine
  (`src/melder/aether/conduit/meld/meld.py`,
  `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`).
- Unit coverage exercises creation metadata and gating behavior
  (`tests/unit/melder/aether/conduit/creations/test_creations.py`,
  `tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py`).
- Validation: Not run.
