# Nexus Root contract
<!-- BEGIN ENTRY: "Nexus recorded cleanup name" -->
## Purpose and boundary
Nexus.cleanup recorded state emission, using RecordedUnitState.
## Before and after
Use RecordedUnitState.CLEANED for the same cleanup emission.
## Interface and errors
Preserve the existing public cleanup, reconfiguration and recording contracts.
## State and lifecycle
No borrowed logger, hosted owner, manager, frame or teardown order changes.
## Failure delta
Only the emitted enum name becomes canonical; readers must retain legacy compatibility.
## Dependencies and order
Read complete Nexus implementation before editing; pair with RecordedUnitState/read guards.
## Validation and unknowns
Run complete relevant Nexus and persistence modules. Full Nexus read remains pending.
<!-- END ENTRY: "Nexus recorded cleanup name" -->
