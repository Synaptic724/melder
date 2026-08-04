# Control Plane Gates

## Purpose
Define mandatory runtime gates for mutation operations.

## Gate Set

### Gate 1: Permission Gate
- Evaluate ACL intersection:
- object mutation permissions
- domain mutation permissions
- profile mutation permissions
- Deny if any layer denies.

### Gate 2: Lock Gate
- Acquire mutation lock for targeted structural region.
- Prevent concurrent structural edits on same target set.

### Gate 3: State Gate
- SpellState must allow mutation transition.
- Block if target is embargoed or policy-blocked.

### Gate 4: ChangeControl Gate
- Determine blast radius (`dirty_spells`, `dirty_roots`).
- Mark affected regions before promotion decisions.

### Gate 5: Validation Gate
- Run required checks for the selected domain policy.
- Collect pass/fail and confidence artifacts.

### Gate 6: Promotion Gate
- Explicit decision:
- promote
- rollback
- branch-only
- discard

### Gate 7: Incident Gate
- Emit incidents on failures, denies, lock conflicts, and validation regressions.

## Invariant
- No mutation can skip lock, validation, and incident pathways.

