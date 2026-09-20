# Architecture Patch: Current-run cancellation for local compiler phases

- Patch ID: local_phase_cancellation_2026_09_19
- Owner: updater_0
<!-- BEGIN ENTRY: Local phase cancellation scope -->
## Scope and Changed Components
SpellbookCreationSystem alone changes how local Phase-5/6 call arguments receive cancellation.
PhaseScheduler still owns a fresh signal per run and the persistent worker pool. No scheduler,
locking, ownership, exception policy, retry or steady-state meld change is proposed.

## Boundary and Invariants
Local phase registration MUST defer reading scheduler.cancel_event until its unit factory executes.
The callable and UnitOfWork MUST therefore observe the same active run scope. Previous failed-run
signals MUST NOT poison a later run; active-run cancellation MUST still stop cooperative phase work.

## Migration, Validation and Rollback
First reproduce recovery after a real failed scheduler run and cooperative current-run cancellation.
Then wire deferred event injection, run owner failures and affected scheduler/compiler tests, and
refresh source documentation and normal generated assets. Rollback reverts only this wiring delta.

## Ticket Coverage and Decisions
TASK-2026-09-19-fix-feature-turn-in-failures, S7 of the non-resolvable registration epic, owns this
repair. No unresolved product decision remains: run-scoped cancellation is the existing contract.
<!-- END ENTRY: Local phase cancellation scope -->
