# Phase 6 Investigation (System Validation)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase06-system-validation-investigation

## Scope
Analyze system-level validation behavior, required inputs, and per-conduit resolution validity updates.

## Key Questions
- What inputs are required from Phase 5 and Phase 4?
- How is per-conduit resolution validity recorded?
- Which validation strategies run and what do they gate?

## Evidence
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_system_validation
- src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py: SpellSystemValidationSystem.validate
- src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py: SpellSystemValidationSystem._record_conduit_resolution_state
- src/melder/aether/dev_ops/spell_system_states/conduit_resolution_state.py: ConduitResolutionState

## Findings
- Phase 6 requires Phase 5 artifacts (entire_dag_blueprint_phase5 and spell_system_index_phase5). If missing, it raises RuntimeError.
- Phase 6 builds phase4_results by scanning SpellCrafters; if a spell was validated but Phase 4 results were cleaned, it inserts a placeholder so MissingPhase4Strategy can treat the spell as validated. It also tracks broken_spell_ids.
- Phase 6 runs a fixed strategy list (CycleDetectionStrategy, BrokenSpellInDagStrategy, GraphConsistencyStrategy, MissingPhase4Strategy, RootReachabilityStrategy, RootCoverageStrategy, IndexDependencySanityStrategy, VisibilityGapStrategy, TopologyDependencyMismatchStrategy, IdentityMixingStrategy, ContractedVersionDriftStrategy, LineageAlignmentStrategy, IndexCoverageStrategy, LineageVersionConflictStrategy, RootLineageConflictStrategy, OwnershipConsistencyStrategy, DependencyTypeSanityStrategy, ScopeOrderingStrategy, ContractGraphCycleStrategy, RootScaleLimitStrategy, RootViabilityStrategy, SocketRefSanityStrategy).
- SpellSystemValidationSystem.validate executes strategies in order, collects diagnostics, and records per-conduit resolution validity for all spell ids and root ids. Any error diagnostic marks all spells/roots invalid for that conduit; no errors mark all spells/roots valid and clear the conduit dirty flag with a validation timestamp.
- Global structural validity is not modified by Phase 6; per-conduit resolution validity is stored in ConduitResolutionState.

## Risks / Concerns
- Phase 6 treats any error diagnostic as invalid for all spells and roots in the conduit (coarse gating).
- Placeholder Phase 4 results may hide detail when Phase 4 artifacts are cleaned.

## Unknowns
- Strategy-specific semantics are not yet reviewed. Investigate each strategy under src/melder/spellbook/spell_crafter/system/validation/.
- Whether per-conduit validity should be computed per-root vs per-spell is a design decision.

## Next Steps
- Review strategy implementations to document exact diagnostics and failure modes.
- Confirm how Phase 6 diagnostics are surfaced to callers and UIs.
