# Architecture patch: a cycle's consumers read as consumers (2026-09-26)

Ticket: tickets/tasks/completed/2026-09-26_word_cycle_consumers_in_circular_dependency_report_task.md (owner approved).

## Objective
When conjure refuses a spell because a dependency cycle is reachable from it but the spell is not in the cycle, the
CIRCULAR_DEPENDENCY message says so: "Spell 'Consumer' cannot be built: it needs 'A', which is part of a dependency
cycle: 'A' -> 'B' -> 'A'. Break that cycle (...); 'Consumer' itself is not part of that cycle." Members keep
their message.

## Non-goals
- No change to which spells are reported or broken, to codes, severities or `details` (`{"cycle": [...]}`).
- No change to BINDING_RESOLUTION_CYCLE (hidden behind CIRCULAR_DEPENDENCY in the report for the same spell).

## Changed components
- CircularDependencyStrategy: the DFS also keeps the spell's direct dependency on the route to the cycle; a
  message helper words member, consumer (through a member or through an intermediate) and self-loop cases.

## Invariants
- A spell is a member exactly when the reported cycle segment starts at the spell (`path.index(node) == 0`); the
  DFS path holds each node once, so a consumer never appears in its own reported cycle.

## Rollback
Restore the file; message text only.

## Coverage matrix
| change | validation |
| --- | --- |
| consumer via member | unit: Gamma -> Alpha <-> Beta |
| consumer via intermediate | unit: Delta -> Gamma -> Alpha <-> Beta |
| consumer of a self-loop | unit: Tree -> Node -> Node |
| member unchanged | existing unit test on 'Alpha' -> 'Beta' -> 'Alpha' |
| end to end | integration: CycleA <-> CycleB with a consumer |
