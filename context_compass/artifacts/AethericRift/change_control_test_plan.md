# Change-Control Test Expansion Plan

## Target
- Add ~300 new pytest test cases focused on change-control/devops changes.

## Allocation (Initial)
- Unit: 120 tests
- Component: 100 tests
- Integration: 80 tests

## Coverage Map
### Unit
- ChangeControlConflictManager
  - hash/key overlap paths
  - conflict rejection ordering
- ChangeControlEmbargoManager
  - open/extend/close flows
  - advisory hints and scope key normalization
- ChangeControlOrchestrator
  - admit/commit/abort paths
  - staged mutation registration
- ChangeControlTransactionManager
  - request normalization, audit logging
  - link mirror registry behavior

### Component
- Spellbook begin/end transaction
  - binding transaction gating
  - staged scope refresh updates
- Conduit begin/end transaction
  - link transaction validation
  - contract add/remove under link transaction
- Change-control staged metadata
  - scope/binding/contract key propagation

### Integration
- Multi-conduit link/contract flows
  - admission rejections on embargo/overlap
  - staged update effects on later meld
- Post-conjure bind/scan under change-control
- Revalidation lifecycle (dirty roots) after transactions

## Notes
- Focus on deterministic fixtures; avoid flaky concurrency.
- Track counts per suite to hit 300 target.
