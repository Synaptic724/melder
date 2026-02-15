- Completed: 2026-02-07
- Summary: Phase 7 target-focused routing and full-path preservation were delivered and accepted; story archived.

# Story: Make Phase 7 Target-Focused in Non-Escalated Meld Path

## Metadata
- Story ID: STORY-2026-02-07-phase-7-target-change-control
- Epic: EPIC-2026-02-07-phase-5-7-spell-isolated-revalidation
- Status: done
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime maintainer, I want Phase 7 change-control work to be target-focused for non-escalated meld revalidation, so that we avoid frame-wide wiring churn for local repairs.

## Value / MRP Alignment
This story reduces avoidable control-plane work in hot paths while preserving change-control correctness and escalation behavior.

## Requirements (Functional)
- Split Phase 7 behavior into:
- target-focused operations for non-escalated meld revalidation.
- full-frame operations for escalated full revalidation.
- Preserve revalidator registration behavior correctness.
- Preserve transaction/change-control dirty root behavior.

## Requirements (Non-Functional)
- Keep lock scope tight and avoid global serialization.
- Maintain deterministic ordering of phase operations.

## Scope Boundaries
- In scope:
- Phase 7 routing + behavior split.
- Change-control integration adjustments required for local path.
- Out of scope:
- Full redesign of ChangeControlManager internals.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/spell_crafter.py` (`run_phase_change_control`, `_ensure_change_control_ready`)
- `src/melder/spellbook/spellbook.py` (`_phase_change_control_factory`)
- `src/melder/aether/dev_ops/change_control_manager/*`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-phase7-local-path - Implement target-focused Phase 7 behavior for non-escalated path.
- [x] Task: TASK-2026-02-07-phase7-full-path - Preserve explicit full-frame Phase 7 path for escalation.
- [x] Task: TASK-2026-02-07-phase7-regression - Add regression coverage for change-control behavior continuity.

## Acceptance Criteria
- Non-escalated meld revalidation does not run full-frame Phase 7 wiring.
- Escalated path still performs full-frame Phase 7 behavior.
- Change-control outcomes (dirty root handling/revalidation hooks) remain correct.

## Validation / Test Plan
- Add tests for local vs escalated Phase 7 routing.
- Run integration tests covering transactions, link/contract changes, and dirty-root paths.

## UX / API / Data Notes
- No public API changes expected.

## Risks / Mitigations
- Risk: Local path under-wires change-control data needed later.
- Mitigation: Add explicit fallback/escalation to full path on missing prerequisites.

## Open Questions
- UNKNOWN: Minimal change-control data required in local path for full correctness guarantees.

## Decision Log
- 2026-02-07: Phase 7 is split by scope: target-focused for default meld path, frame-wide for escalation path.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Completed. Phase 7 now supports target-focused behavior for non-escalated meld revalidation and preserves full-frame behavior where escalation requires it.
