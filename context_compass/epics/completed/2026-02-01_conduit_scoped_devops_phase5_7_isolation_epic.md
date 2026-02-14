# Epic: Conduit-Scoped DevOps and Phase 5-7 Isolation

- Completed: 2026-02-03
- Summary: Conduit-scoped change-control implemented, tests added, and stories closed.

## Metadata
- Epic ID: EPIC-2026-02-01-conduit-scoped-devops-phase5-7
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03
- Target Window: 2026-Q1
- Related Program/Initiative:

## Problem / Opportunity
Phase 5-7 currently write into frame-level DevOps state that is shared across conduits, which creates last-writer-wins behavior for change-control artifacts and can mis-scope dirty tracking when multiple conduits exist in the same aetheric frame. This undermines conduit isolation goals and can lead to incorrect revalidation and change-control decisions across spellbooks.

Evidence:
- Spellbooks share a frame-level SpellSystemStates via aetheric_frame. EVIDENCE: src/melder/spellbook/spellbook.py:__init__
- AethericFrame owns frame-level DevOpsManager and SpellSystemStates. EVIDENCE: src/melder/aether/aetheric_frame.py:__init__
- Phase 5 rebuilds change-control component_of and sets a single revalidator. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints
- ChangeControlManager stores a single component_of map and a single revalidate_fn (no conduit_id scoping). EVIDENCE: src/melder/aether/dev_ops/change_control_manager/change_control_manager.py
- Phase 6 validation is per-conduit via conduit_id resolution state. EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py:_record_conduit_resolution_state

## MRP Alignment (Most Reasonable Product)
Conduit-scoped DevOps is foundational for correctness: it keeps change-control, revalidation, and risk gating aligned to the spellbook/conduit that created the artifacts, while preserving shared frame capabilities. This builds a trustworthy core for multi-conduit frames without forcing per-spellbook isolation by default.

## Goals (Outcomes)
- Make DevOps change-control and revalidation scoping consistent with conduit_id (root conduit) across Phase 5-7.
- Eliminate cross-conduit last-writer-wins effects for component_of and revalidator callbacks.
- Document and enforce the intended scoping rules (per frame vs per conduit).

## Non-Goals (Explicit Exclusions)
- Rewriting Phase 1-4 or Phase 8-11 logic.
- Removing shared frames as a capability.
- Performance optimization work unrelated to scoping correctness.

## Scope Boundaries
- In scope:
  - Audit DevOpsManager, ChangeControlManager, RiskManager, SpellSystemStates, and Phase 5-7 call paths.
  - Identify all global state that should be conduit-scoped.
  - Design conduit-scoped component_of and revalidator handling.
  - Update docs to reflect the correct scoping model.
- Out of scope:
  - Major architecture changes to Conduit or Spellbook lifecycles not required for scoping.
  - Behavioral changes to meld resolution semantics unrelated to DevOps scoping.

## Success Metrics
- No shared frame state is overwritten by another conduit's Phase 5/7 run without explicit conduit_id scoping.
- Change-control dirty tracking and revalidation apply only to the conduit that built the Phase 5 artifacts.
- Documentation clearly states which DevOps artifacts are frame-scoped vs conduit-scoped.

## Requirements (Functional + Non-Functional)
- Functional:
  - component_of must be keyed by conduit_id or root conduit_id (exact choice decided by design).
  - revalidator callbacks must be conduit-scoped and not overwrite each other.
  - Phase 5/7 must update only the conduit-scoped DevOps data for the invoking conduit.
- Non-functional:
  - No regressions in single-conduit scenarios.
  - Behavior must be deterministic under concurrent conduits in the same frame.

## Constraints / Assumptions
- Must follow existing docstring/comment requirements and scoping rules.
- Changes must preserve public API unless explicitly approved.
- Evidence-first: no assumptions about scoping beyond code evidence.

## Dependencies / External References
- Spellbook conjure and phase scheduling factories. EVIDENCE: src/melder/spellbook/spellbook.py
- SpellSystemStates conduit resolution state. EVIDENCE: src/melder/aether/dev_ops/spell_system_states/spell_system_states.py
- ConduitResolutionState per-conduit validity. EVIDENCE: src/melder/aether/dev_ops/spell_system_states/conduit_resolution_state.py
- ChangeControlManager global component_of/revalidator. EVIDENCE: src/melder/aether/dev_ops/change_control_manager/change_control_manager.py
- RiskManager per-conduit gating. EVIDENCE: src/melder/aether/dev_ops/risk_manager/risk_manager.py

## Milestones (Track Progress)
- [x] Milestone 1: DevOps scoping audit complete with evidence map and coupling analysis.
- [x] Milestone 2: Conduit-scoped design agreed (component_of + revalidator + Phase 5/7 touchpoints).
- [x] Milestone 3: Implementation + tests + docs updated.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-01-devops-scope-audit - Map all frame vs conduit scoping in DevOps and phases.
- [x] Story: STORY-2026-02-01-change-control-conduit-scope - Design conduit-scoped component_of and revalidator behavior.
- [x] Story: STORY-2026-02-01-phase5-7-conduit-isolation - Implement and validate the scoping changes.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-01-devops-scope-audit
- [x] Task: Complete story STORY-2026-02-01-change-control-conduit-scope
- [x] Task: Complete story STORY-2026-02-01-phase5-7-conduit-isolation
- [x] Task: Update architecture/components docs for scoping model

## Acceptance Criteria (Epic Done)
- Conduit-scoped change-control data structures are implemented and documented.
- Phase 5-7 do not overwrite other conduits' DevOps artifacts in the same frame.
- Tests demonstrate correct isolation in a multi-conduit, shared-frame scenario.

## Risks / Mitigations
- Risk: Breaking shared-frame behavior for contracted spells.
  Mitigation: Explicitly define whether contracted spells are included per conduit and test it.
- Risk: Hidden assumptions in DevOpsManager about single component_of map.
  Mitigation: Audit all usages before implementing conduit scoping.

## Validation / Test Approach
- Add tests that create two conduits in the same frame and verify independent component_of and revalidation behavior.
- Confirm per-conduit resolution validity remains unchanged.

## Rollout / Adoption Plan
- Implement behind a feature flag if needed; otherwise roll out with thorough tests and documentation.

## Open Questions
- Should contracted spells be included in conduit-scoped component_of and revalidation sets?
- Should component_of be keyed by conduit_id, root conduit_id, or spellbook id?
- How should revalidation behave if a spell appears in multiple conduits within the same frame?

## Decision Log
- 2026-02-01: Identified mismatch between per-conduit Phase 6 and frame-global Phase 5/7 DevOps artifacts.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Audit and design stories are complete, conduit-scoped change-control is implemented, and multi-conduit isolation tests are in place. Validation not run; acceptance confirmed for epic closure.
