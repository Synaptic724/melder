# Task: Add PhaseState propagation to the phase pipeline

## Metadata
- Task ID: TASK-2026-01-31-phase-state-pipeline
- Story:
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Introduce a per-run PhaseState object in PhaseScheduler and pass it through all phase work so phases can share data (including cancellation) without global state.

## Scope Boundaries
- In scope:
  - Add a PhaseState object (ephemeral, per PhaseScheduler run) that carries the cancellation event and a shared data bag.
  - Pass PhaseState into every phase unit of work and down into phase entrypoints (Spell.run_phase_* / SpellCrafter.run_phase_*).
  - Update phase factories to construct and pass PhaseState consistently across all phases.
  - Update validation strategy usage to consume shared data via PhaseState where needed.
- Out of scope:
  - Long-lived caches or global registries.
  - Behavioral changes to phase ordering or policy gates beyond wiring PhaseState.

## Steps / Checklist
- [ ] Define PhaseState (location TBD; likely `src/melder/utilities/synchronization/phase_state.py`).
- [ ] Wire PhaseState creation in PhaseScheduler (per scheduler instance or per run).
- [ ] Update UnitOfWork creation to pass PhaseState into phase functions (and remove direct cancel_event arg where appropriate).
- [ ] Update all phase entrypoints (Spell.run_phase_* and SpellCrafter.run_phase_*) to accept `phase_state` and use `phase_state.cancel_event`.
- [ ] Update Phase 4 validation to store/reuse shared views via PhaseState.
- [ ] Update any call sites that invoke phases directly (e.g., `run_structural_phases`, `run_all_phases`).
- [ ] Update docs or comments that describe phase execution inputs.

## Deliverables
- PhaseState object and wiring through PhaseScheduler and phase entrypoints.
- Phase entrypoints updated to accept/use PhaseState (cancel_event via PhaseState).
- Shared per-run data plumbing available to validation and other phases.

## Files / Paths Impacted
- `src/melder/utilities/synchronization/phase_scheduler.py`
- `src/melder/utilities/synchronization/unit_of_work.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `src/melder/spellbook/spell_crafter/validation/validation_system.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/*`

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/spellbook/spell_crafter`

## Risks / Rollback Notes
- Touches core phase plumbing; signature changes will be wide. Rollback is to revert PhaseState wiring and restore cancel_event-only signature.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
New task requested by user to add a per-run PhaseState object (ephemeral; not global) that carries the cancellation event and shared data across all phases. This requires PhaseScheduler and all phase entrypoints to accept PhaseState and use it instead of passing CancellationEvent directly.
