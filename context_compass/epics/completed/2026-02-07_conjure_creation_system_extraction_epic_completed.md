- Completed: 2026-02-07
- Summary: Conjure orchestration was extracted into `SpellbookCreationSystem`, Spellbook now delegates only the required phase facades, and targeted + full-suite validation passed.

# Epic: Extract Spellbook Conjure Pipeline into SpellbookCreationSystem

## Metadata
- Epic ID: EPIC-2026-02-07-conjure-creation-system-extraction
- Status: done
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07
- Target Window: 2026-Q1
- Related Program/Initiative: Spellbook architecture simplification + conjure lifecycle hardening

## Problem / Opportunity
`Spellbook` currently owns binding, transaction orchestration, conjure construction, and full phase scheduler orchestration in one class (`src/melder/spellbook/spellbook.py`). Conjure-specific orchestration and phase factory code is tightly coupled to unrelated Spellbook concerns, increasing maintenance cost and making cleanup/lifecycle boundaries harder to reason about.

Evidence:
- Conjure orchestration and conduit creation are inline in `Spellbook.conjure` (`src/melder/spellbook/spellbook.py:2936`).
- Structural and resolution phase orchestration live inside Spellbook (`src/melder/spellbook/spellbook.py:3392`, `src/melder/spellbook/spellbook.py:3523`, `src/melder/spellbook/spellbook.py:3631`).
- Phase factory methods are all Spellbook members (`src/melder/spellbook/spellbook.py:3947`, `src/melder/spellbook/spellbook.py:4304`).
- Runtime components call these Spellbook phase methods directly (for example `src/melder/aether/conduit/conduit.py:2858`, `src/melder/aether/conduit/meld/meld.py:550`, `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:720`).

## MRP Alignment (Most Reasonable Product)
The minimum durable core is a dedicated `SpellbookCreationSystem` that owns conjure-phase orchestration and scheduler wiring while preserving current Spellbook behavior and call contracts. This gives a stable ownership boundary for conjure lifecycle and idempotent teardown without changing public API shape.

## Goals (Outcomes)
- Extract conjure orchestration and phase scheduling responsibilities out of `Spellbook` into a dedicated class.
- Keep Spellbook public behavior stable (`conjure`, bind transaction behavior, post-conjure revalidation behavior).
- Keep compatibility for existing internal callers that currently invoke Spellbook private phase methods.
- Ensure `SpellbookCreationSystem` cleanup is deterministic, idempotent, and explicit (`cleanup()` plus reference nulling).
- Reduce Spellbook complexity while preserving current validation and error semantics.

## Non-Goals (Explicit Exclusions)
- No public API redesign for `Spellbook`, `Conduit`, or `Meld`.
- No rewrite of `PhaseScheduler` internals in this epic.
- No behavior changes to phase algorithms in `SpellCrafter`.
- No large transaction/change-control redesign.

## Scope Boundaries
- In scope:
- Add `SpellbookCreationSystem` under `src/melder/spellbook/`.
- Move conjure-phase orchestration methods and phase factory methods from Spellbook into the new class.
- Add Spellbook delegation wrappers where runtime components currently call Spellbook phase methods.
- Add deterministic idempotent cleanup for `SpellbookCreationSystem` and ensure references are nulled after use.
- Update tests impacted by method movement and ensure contract coverage remains.
- Out of scope:
- Changing phase semantics or ordering.
- Refactoring unrelated Spellbook registry/linking logic.
- Broad package/module reorganization outside conjure extraction.

## Success Metrics
- `Spellbook` no longer directly owns the moved phase scheduling implementation body.
- Existing integration call sites continue to work without public API changes.
- Conjure path and runtime revalidation path pass existing relevant tests after migration.
- `SpellbookCreationSystem.cleanup()` is called per use path and is safe to call multiple times.

## Requirements (Functional + Non-Functional)
- Functional:
- `Spellbook.conjure()` must use `SpellbookCreationSystem` for structural and resolution phase orchestration.
- Post-conjure runtime paths that currently call Spellbook phase methods must remain operational through delegation.
- Conjure lifecycle hooks (`pre/activated/post`) must keep current call order and error behavior.
- `SpellbookCreationSystem` must expose orchestration entrypoints needed by Spellbook and runtime revalidation wrappers.
- Non-functional:
- Keep reviewable migration slices (avoid one-shot giant move).
- Preserve deterministic cleanup and no hidden mutable globals.
- Maintain current logging style and error model.

## Constraints / Assumptions
- Existing tests assert private Spellbook phase factories/methods directly; migration must account for this compatibility surface.
- Runtime paths still require phase orchestration after initial conjure; cleanup-after-conjure cannot remove future revalidation capability.
- Assumption: delegation wrappers on Spellbook are acceptable to preserve current call sites while ownership moves.

## Dependencies / External References
- `src/melder/spellbook/spellbook.py`
- `src/melder/utilities/synchronization/phase_scheduler.py`
- `src/melder/spellbook/spell.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `tests/unit/melder/spellbook/test_spellbook.py`

## Milestones (Track Progress)
- [x] Milestone 1: Define extraction boundary and compatibility contract.
- [x] Milestone 2: Introduce `SpellbookCreationSystem` skeleton with lifecycle and cleanup contract.
- [x] Milestone 3: Move structural/resolution orchestration and phase factories into `SpellbookCreationSystem`.
- [x] Milestone 4: Wire Spellbook delegation facades and idempotent per-use cleanup/nulling.
- [x] Milestone 5: Update tests and docs to match new ownership.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-07-conjure-system-boundary - Define moved symbols and compatibility surface.
- [x] Story: STORY-2026-02-07-conjure-system-implementation - Implement `SpellbookCreationSystem` orchestration and cleanup.
- [x] Story: STORY-2026-02-07-spellbook-delegation - Replace Spellbook inline phase logic with delegation and lifecycle wiring.
- [x] Story: STORY-2026-02-07-conjure-system-tests - Update/add unit and integration coverage for behavior parity and idempotent cleanup.
- [x] Story: STORY-2026-02-07-conjure-system-docs - Update ticketing/docs to match new ownership.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-07-conjure-system-boundary
- [x] Task: Complete story STORY-2026-02-07-conjure-system-implementation
- [x] Task: Complete story STORY-2026-02-07-spellbook-delegation
- [x] Task: Complete story STORY-2026-02-07-conjure-system-tests
- [x] Task: Complete story STORY-2026-02-07-conjure-system-docs

## Acceptance Criteria (Epic Done)
- `SpellbookCreationSystem` exists and owns conjure-phase orchestration previously implemented in Spellbook.
- Spellbook delegates to `SpellbookCreationSystem` for conjure and phase orchestration paths without public API changes.
- Conjure lifecycle retains existing behavior (configuration validation/bind, phase runs, hooks, conduit creation).
- Cleanup contract is explicit and idempotent: system instance cleanup can be called multiple times safely and references are nulled after use.
- Existing runtime revalidation callers continue to function via Spellbook phase facades.

## Risks / Mitigations
- Risk: Breaking runtime revalidation callers that use Spellbook private methods.
- Mitigation: Keep only required Spellbook phase facades stable and delegate internally.
- Risk: Behavior drift in phase ordering or validation gates during extraction.
- Mitigation: Move logic in small slices with parity tests before removing old bodies.
- Risk: Cleanup ordering bugs that cause use-after-clean in delayed revalidation.
- Mitigation: Separate per-run ephemeral system instances from long-lived Spellbook state and enforce idempotent cleanup checks.

## Validation / Test Approach
- Unit coverage updated in `tests/unit/melder/spellbook/test_spellbook.py` to exercise moved behavior via `SpellbookCreationSystem`.
- Component coverage updated in `tests/component/melder/spellbook/test_spellbook_component_conduit_definition.py`.
- Integration checks for runtime callers:
  - `tests/integration/melder/multithreading/test_multithreading_link_bind_contract_features.py`
- Full regression validation run:
  - `python -m pytest -q` (4365 passed, 129 skipped, 4 xfailed, 3 warnings on 2026-02-07).

## Rollout / Adoption Plan
- Implement extraction with Spellbook phase facades for caller compatibility.
- Keep behavior parity as the default until tests pass.
- Follow with doc ownership updates in architecture/components context.

## Open Questions
- Resolved: instantiate `SpellbookCreationSystem` per `Spellbook.conjure()` run and cleanup in `finally`.
- Resolved: tests that targeted moved methods now assert `SpellbookCreationSystem` behavior directly.
- Resolved: `_set_policy_state` remains on `Spellbook`.

## Decision Log
- 2026-02-07: New epic created to isolate conjure-phase orchestration into `SpellbookCreationSystem` with behavior parity and idempotent cleanup.
- 2026-02-07: Final compatibility contract narrowed to Spellbook phase facades only (`_run_structural_phases`, `_run_post_conjure_structural_phases`, `_run_resolution_phases_for_conduit`, `_run_resolution_phases_for_target_spell`).
- 2026-02-07: Tests for moved behavior were updated to target `SpellbookCreationSystem` directly.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Extraction is complete. `SpellbookCreationSystem` now owns conjure orchestration and moved phase scheduling implementation; Spellbook retains only the required phase facades. Unit/component/integration coverage passed for the refactor surface, and a full-suite run passed on 2026-02-07.
