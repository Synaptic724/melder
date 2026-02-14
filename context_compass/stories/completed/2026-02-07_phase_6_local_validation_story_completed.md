- Completed: 2026-02-07
- Summary: Phase 6 local-validation behavior and state-write handling were delivered and accepted; story archived.

# Story: Scope Phase 6 Validation to Target Closure Effects

## Metadata
- Story ID: STORY-2026-02-07-phase-6-local-validation
- Epic: EPIC-2026-02-07-phase-5-7-spell-isolated-revalidation
- Status: done
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime maintainer, I want Phase 6 validation to evaluate target closure effects in non-escalated meld revalidation, so that one dirty spell does not force frame-wide validation work.

## Value / MRP Alignment
This story keeps correctness checks close to the impacted spell closure on the hot path while preserving explicit escalation to full-frame validation when required.

## Requirements (Functional)
- Add Phase 6 local-validation mode for target closure revalidation path.
- Ensure conduit validity updates in `SpellSystemStates` are correct for target closure outputs.
- Preserve full-frame Phase 6 path for escalated full revalidation.
- Ensure diagnostics handling remains stable and useful.

## Requirements (Non-Functional)
- No spellbook-global lock.
- Validation path must not block unrelated meld requests beyond closure-specific lock windows.
- Maintain deterministic state transitions for `unknown -> gated -> valid/invalid`.

## Scope Boundaries
- In scope:
- Local Phase 6 mode + state write semantics.
- Non-escalated routing updates.
- Out of scope:
- Rewriting all validation strategies in one pass.
- Contract system redesign.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/spell_crafter.py` (`run_phase_system_validation`)
- `src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py`
- `src/melder/aether/dev_ops/spell_system_states/*`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-phase6-local-mode - Implement local-validation mode and strategy selection/routing.
- [x] Task: TASK-2026-02-07-phase6-state-writes - Update conduit validity writes for local scope semantics.
- [x] Task: TASK-2026-02-07-phase6-diagnostics - Ensure diagnostics remain coherent in local and full modes.

## Acceptance Criteria
- Non-escalated meld revalidation runs Phase 6 in local scope for the target closure.
- `SpellSystemStates` validity and dirty transitions are correct for affected closure.
- Escalated path still runs full-frame Phase 6 validation.

## Validation / Test Plan
- Add unit/integration tests for local-mode validity updates.
- Validate non-escalated and escalated behavior routes with explicit assertions.
- Run regression tests for spellbook/conduit validation flows.

## UX / API / Data Notes
- No public API change expected.
- Internal validation result structures may include scope metadata (`local` vs `full`).

## Risks / Mitigations
- Risk: Local mode misses strategy prerequisites.
- Mitigation: Define strategy eligibility matrix and enforce escalation when prerequisites are absent.
- Risk: Conduit validity map becomes inconsistent between modes.
- Mitigation: Add deterministic reconciliation checks in tests.

## Open Questions
- UNKNOWN: Exact strategy subset that is safe in local mode without full-frame context.

## Decision Log
- 2026-02-07: Phase 6 will support local validation mode for non-escalated meld path and retain full mode for escalations.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Completed. Phase 6 now supports local validation semantics for target closure revalidation while retaining an explicit full-frame validation path for escalations.
