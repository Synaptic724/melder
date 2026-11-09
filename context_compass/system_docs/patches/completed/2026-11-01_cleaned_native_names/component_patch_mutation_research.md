# MutationResearch Root contract
<!-- BEGIN ENTRY: "MutationResearch recorded cleanup name" -->
## Purpose and boundary
MutationResearch.cleanup recorded state emission, using RecordedUnitState.
## Before and after
Use RecordedUnitState.CLEANED for the same cleanup emission.
## Interface and errors
Preserve public activation, reload, composition and recording semantics.
## State and lifecycle
No borrowed logger, hosted root, research set or teardown order changes.
## Failure delta
Only the emitted enum name becomes canonical; readers must retain legacy compatibility.
## Dependencies and order
Read complete root implementation before editing; pair with RecordedUnitState/read guards.
## Validation and unknowns
Run complete relevant MutationResearch and persistence modules. Full root read remains pending.
<!-- END ENTRY: "MutationResearch recorded cleanup name" -->
