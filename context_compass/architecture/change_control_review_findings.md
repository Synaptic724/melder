# Change-Control + DevOps Review Findings

## Findings (Ordered by Severity)
### Low: Link mirror registry is not used for admission decisions
- Evidence: `ChangeControlTransactionManager.register_link` stores borrower/provider
  relationships but no admission path consults it.
- Risk: Link topology does not affect conflict/embargo decisions, so linked
  conduits can proceed with changes as long as scope keys do not overlap.
- Decision: Keep link mirror informational for now; admission relies on explicit
  scope keys and conduit ids supplied by callers.
- References:
  - `src/melder/aether/dev_ops/change_control_manager/transaction_manager/transaction_manager.py`:460-542
  - `src/melder/aether/dev_ops/change_control_manager/conflict_manager/conflict_manager.py`:74-112

### Low: Scope hash/key mismatch can bypass conflict/embargo checks
- Evidence: Conflict detection uses `request.scope_hashes or request.scope_keys`,
  and embargo checks accept only scope keys. If any request is built with hashes
  only (no scope keys), it will not conflict with requests that only set keys.
- Risk: A caller that bypasses `build_request` normalization could avoid overlap
  detection, allowing concurrent changes that should be serialized.
- References:
  - `src/melder/aether/dev_ops/change_control_manager/conflict_manager/conflict_manager.py`:100-111
  - `src/melder/aether/dev_ops/change_control_manager/embargo_manager/embargo_manager.py`:160-214
  - `src/melder/aether/dev_ops/change_control_manager/transaction_manager/transaction_manager.py`:165-180

## Residual Risks / Testing Gaps
- No integration tests exercise admission decisions based on link topology; only
  scope-key overlap is currently covered.

## Notes
- Findings assume all requests are created via `ChangeControlTransactionManager.build_request`.
  If all callers supply scope keys, the mismatch risk is theoretical.
