# Story: Define compiled plan model and lifecycle

## Metadata
- Story ID: STORY-2026-01-25-compiled-plan-model
- Epic: EPIC-2026-01-25-fast-path-meld-compiled-plans
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As a performance engineer, I want a compiled execution plan model with a clear
lifecycle, so that meld runtime can execute without rebuilding graphs.

## Value / MRP Alignment
A stable plan model defines the minimum trusted core for fast-path execution and
enables safe fallback when plan validity changes.

## Requirements (Functional)
- Define RootExecutionPlan structure and invariants.
- Define plan signature and invalidation rules.
- Define plan storage location and cleanup ownership.

## Requirements (Non-Functional)
- Avoid module-level mutable state.
- Plan objects must be cleanable and safe to discard.

## Scope Boundaries
- In scope:
  - Plan schema and signature design.
  - Plan storage lifecycle and cleanup discipline.
- Out of scope:
  - Plan compilation algorithms.
  - Fast-path runtime execution logic.

## Dependencies / Related Work
- RootResolutionBlueprint artifacts from Phase 5
  (src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints).
- MeldRuntime and MeldEngine runtime path
  (src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py,
  src/melder/aether/conduit/meld/meld_engine/meld_engine.py).

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-plan-model-research - Research plan model storage and lifecycle.
- [ ] Task: TASK-2026-01-25-compiled-plan-schema - Define plan fields and invariants.
- [ ] Task: TASK-2026-01-25-plan-signature-invalidation - Specify signature and invalidation.
- [ ] Task: TASK-2026-01-25-plan-storage-lifecycle - Decide storage and cleanup rules.
- [ ] Task: TASK-2026-01-25-plan-docs-update - Update architecture/components docs.

## Acceptance Criteria
- RootExecutionPlan schema and invariants are documented.
- Plan signature inputs and invalidation events are explicit.
- Plan storage and cleanup ownership are defined and consistent.

## Validation / Test Plan
- Not run.
- Targeted unit tests for plan schema and signature once implemented.

## UX / API / Data Notes
- Internal API only; no public API changes in this story.

## Risks / Mitigations
- Risk: plan schema is too complex to execute fast.
  Mitigation: prefer structure-of-arrays and avoid nested dicts.

## Open Questions
- Should the plan be attached to RootResolutionBlueprint, SpellCrafter, or Conduit?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created; plan model and lifecycle design pending.
