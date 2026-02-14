- Completed: 2026-02-07
- Summary: Phase 5 target-closure routing work was delivered and accepted; story archived.

# Story: Scope Phase 5 to Target Spell Closure

## Metadata
- Story ID: STORY-2026-02-07-phase-5-local-closure
- Epic: EPIC-2026-02-07-phase-5-7-spell-isolated-revalidation
- Status: done
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime maintainer, I want Phase 5 root blueprint generation to execute on the target spell closure, so that meld-time revalidation avoids unrelated spell rebuilds.

## Value / MRP Alignment
This story reduces avoidable frame-wide work on the hot path while preserving deterministic blueprint generation for the spell closure that is actually being resolved.

## Requirements (Functional)
- Add a target-closure Phase 5 path that builds only the closure for the requested spell/root.
- Ensure closure artifacts remain compatible with downstream Phase 6/8/9/11 consumers.
- Preserve existing transaction-driven invalidation semantics in `SpellSystemStates`.
- Keep existing full-frame Phase 5 behavior available for escalated full revalidation.

## Requirements (Non-Functional)
- Do not use a spellbook-global lock.
- Keep lock scope spell-local or closure-local.
- Avoid increasing allocations on each meld call beyond current baseline for target closure size.

## Scope Boundaries
- In scope:
- Phase 5 target-closure blueprint/index generation behavior.
- Internal method wiring needed to invoke target-closure Phase 5.
- Out of scope:
- Full rewrite of system adjacency builders.
- Public API changes.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/spell_crafter.py` (`run_phase_root_blueprints`)
- `src/melder/spellbook/spellbook.py` (`_phase_root_blueprints_factory`, `_run_resolution_phases_for_conduit`)
- `src/melder/aether/conduit/meld/meld.py` (revalidation call path)

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-phase5-closure-builder - Implement closure-scoped blueprint/index builder path.
- [x] Task: TASK-2026-02-07-phase5-routing - Route meld-triggered revalidation to closure-scoped Phase 5.
- [x] Task: TASK-2026-02-07-phase5-compat - Verify downstream artifact compatibility for Phase 6/8/9/11.

## Acceptance Criteria
- Meld-triggered revalidation for a target spell only constructs Phase 5 artifacts for that target closure.
- Unrelated spells are not rebuilt in the non-escalated path.
- Existing escalated/full path still supports frame-wide Phase 5.

## Validation / Test Plan
- Add targeted tests/instrumentation that detect closure vs unrelated rebuild behavior.
- Run affected integration tests for meld and conduit revalidation.
- Report command outputs and durations; if not run, mark `Not run`.

## UX / API / Data Notes
- No user-facing API changes expected.
- Internal data ownership may move toward closure-scoped artifact handles.

## Risks / Mitigations
- Risk: Closure boundary is computed incorrectly.
- Mitigation: Add closure-shape assertions in tests for deep/wide/diamond graphs.
- Risk: Downstream phases assume frame-wide artifact presence.
- Mitigation: Add compatibility assertions before switching default routing.

## Open Questions
- UNKNOWN: Final closure identity source for Phase 5 (`SpellSystemStates` topology only vs mixed blueprint/index basis).

## Decision Log
- 2026-02-07: Phase 5 is split to support target-closure default path while retaining full-frame escalation path.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Completed. Phase 5 now supports target-closure behavior for meld-time revalidation, while frame-wide behavior remains available for escalated full revalidation.
