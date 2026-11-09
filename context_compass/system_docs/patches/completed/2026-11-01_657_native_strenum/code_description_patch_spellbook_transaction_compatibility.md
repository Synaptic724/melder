# Spellbook transaction comparison flow

<!-- BEGIN ENTRY: "Match binding and close without changing session ownership" -->
## Trigger and flow
The bind lifecycle and mismatched-close safety check require an explicit comparison rule.
Project the caller input at the existing bind comparison. On close, compare the projected
expected value with bind or with the projected stored request; pass the original argument to
the mediator. Start, join, finalize and clear state in the existing order.

## Errors, rollback and checks
Different types still refuse before finalization. Preserve exceptional exit and existing
success propagation. No changes to bound-spell ownership, disposal, claims or locking. Test
real legacy/member/canonical forms, mixed entry/close forms and a mismatched close.
<!-- END ENTRY: "Match binding and close without changing session ownership" -->
