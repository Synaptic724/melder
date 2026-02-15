# Story: Move meld runtime override behavior into Phase 9/10 artifacts

## Metadata
- Story ID: STORY-2026-01-28-meld-runtime-phase-artifacts
- Epic: N/A
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## User Narrative
As a runtime maintainer, I want meld execution to consume Phase 9/10 artifacts so that
behavior is centralized in SpellCrafter phases and the runtime stays lean without
changing outcomes.

## Value / MRP Alignment
Preserves current behavior while consolidating responsibility into phase artifacts,
reducing runtime duplication and keeping the execution path predictable.

## Requirements (Functional)
- Phase 9 InjectionPlan encodes dependency wiring plus override and SpellContract sources.
- Phase 10 patch maps drive override and mutation targeting (no runtime fallback to
  SpellOverrider or GraphMutator).
- MeldRuntime/MeldEngine use phase artifacts and do not recompile logic that already
  exists in phases.
- All behavior mirrors current runtime behavior (no semantic changes).

## Requirements (Non-Functional)
- No public API changes.
- Preserve error messages and failure modes where feasible.
- Keep runtime allocations minimal (use precompiled artifacts).

## Scope Boundaries
- In scope:
  - Phase 9 InjectionPlan expansion.
  - Phase 10 patch map wiring and runtime removal of duplicate logic.
  - MeldRuntime/MeldEngine cleanup to rely on phase artifacts.
  - Tests that prove behavior parity.
- Out of scope:
  - New features or behavior changes.
  - Refactors outside meld/runtime and SpellCrafter phases 8-10.

## Dependencies / Related Work
- Audit: context_compass/artifacts/README.md
- Archived audit ticket: context_compass/tasks/archive/2026-01-28_phase8-10-migration-audit_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-28-phase9-injection-plan-sources - Expand Phase 9 InjectionPlan sources.
- [x] Task: TASK-2026-01-28-phase10-patch-map-wiring - Wire Phase 10 patch maps into runtime.
- [x] Task: TASK-2026-01-28-meld-runtime-phase-artifact-gating - Remove runtime fallbacks and require artifacts.
- [x] Task: TASK-2026-01-28-meld-runtime-phase-artifact-tests - Add regression tests for parity.

## Acceptance Criteria
- MeldRuntime/MeldEngine use Phase 9/10 artifacts for overrides, contracts, and mutation rewires.
- Runtime no longer duplicates Phase 8-10 compilation logic.
- Existing behavior and error semantics are preserved.
- Tests cover phase artifact wiring and key runtime paths.

## Validation / Test Plan
- PYTHONPATH=/workspace/melder_private pytest -q

## UX / API / Data Notes
- Internal runtime behavior only; no external API changes.

## Risks / Mitigations
- Risk: behavior drift when removing runtime fallback logic.
  Mitigation: parity tests and evidence-based mapping from audit.

## Open Questions
- None yet. Track discoveries in task tickets.

## Decision Log
- 2026-01-28: Move override/mutation behavior into Phase 9/10 artifacts with no semantic changes.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created after archiving existing tickets. Implementation to proceed via task tickets.
