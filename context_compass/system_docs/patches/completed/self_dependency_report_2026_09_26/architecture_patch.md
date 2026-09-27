# Architecture patch: self-referencing constructors refused through the readable report (2026-09-26)

Ticket: tickets/tasks/completed/2026-09-26_report_self_referencing_constructor_as_validation_error_task.md (owner delegated the
choice; option A). PROCESS NOTE: written after the implementation - the patch gate was missed before the edits and
this lane records it instead of back-dating it.

## Objective
A constructor that takes its own class is refused at conjure (or at a late dynamic bind/meld) with the
SpellbookValidationError report - spell, parameter, fix - instead of PhaseExecutionError "DagNode cannot depend on
itself" or a bare ValueError.

## Non-goals
- No change to validation results: the spell still carries SELF_DEPENDENCY and CIRCULAR_DEPENDENCY (pinned by tests).
- No change to longer cycles or to how a cycle's consumers are reported (listed as "part of" a cycle; open).
- No treatment of a self-typed parameter as a caller input (option C, rejected).

## Changed components
- CompilerPhase3 (fable_0's C-C lane, landed there on request, F0-16): a self-resolution is recorded as a dependency
  (dependency ids, socket targets, SpellSystemStates, Spell.dependencies) outside the frame order.
- SelfDependencyStrategy: names the self-resolving parameter(s) from the Phase-3 topology; details gain
  `parameter_names`.
- SpellbookValidationError: SUPERSEDED_BY hides CIRCULAR_DEPENDENCY when SELF_DEPENDENCY is reported for the spell.

## Invariants
- A self-dependent spell never enters its own frame order; walks over dependents stay finite (visited sets).
- Report rule chain: BINDING_RESOLUTION_CYCLE behind CIRCULAR_DEPENDENCY behind SELF_DEPENDENCY, per spell.

## Interface deltas
- Additive: SELF_DEPENDENCY `details["parameter_names"]` when known.

## Rollback
Restore the three files; Phase 3's part rolls back with C-C.

## Coverage matrix
| change | validation |
| --- | --- |
| Phase 3 record | fable_0's unit test (records self dependency out of the frame) |
| parameter naming | strategy unit tests (one, several, no topology) |
| report dedupe | report unit test; integration: message has SELF_DEPENDENCY only, result keeps both codes |
| end to end | integration: single, collection, consumer, default control, late dynamic bind |
