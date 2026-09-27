# Component patch: SpellCompiler and Validation Pipeline - self-dependency (2026-09-26)

## Before
- Phase 3 raised on a parameter resolving to its own spell; conjure aborted with PhaseExecutionError and a late
  dynamic bind raised a bare ValueError. SelfDependencyStrategy existed but never ran on real pipelines.

## After
- Phase 3 records the self id; Phase 4 reports SELF_DEPENDENCY ("Spell 'Node' depends on itself: its constructor
  parameter 'parent' resolves to this same spell. Remove that parameter or give it a default.") and
  CIRCULAR_DEPENDENCY; the report shows SELF_DEPENDENCY only.

## Interface / state / failure deltas
- Exception type at conjure/meld changes from PhaseExecutionError / ValueError to SpellbookValidationError.

## Validation expectations
- Unit, component and integration suites green on a worktree sync; new tests fail on the unpatched base.
