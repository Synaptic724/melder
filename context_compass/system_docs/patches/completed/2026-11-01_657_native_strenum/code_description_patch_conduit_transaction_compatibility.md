# Conduit transaction comparison flow

<!-- BEGIN ENTRY: "Preserve transaction posture and dispatch" -->
## Trigger and flow
Posture gates and specialized transaction dispatch depend on direct transaction comparisons.
Project the value only for these comparisons. Route bind to the owning Spellbook, link/unlink
and transfer to their existing strategies, and all other inputs down the existing generic path.
For active contract windows project the stored request only for the existing link-family check.

## Errors, rollback and checks
Keep the original request argument and metadata, fail before admission for disabled operations,
and preserve all existing close and exception paths. No change to transfer stewardship, session
ownership or lock order. Test legacy/member/canonical forms, mixed close, blocked dynamic/disabled
cases, real link-family contract mutation and transfer regressions.
<!-- END ENTRY: "Preserve transaction posture and dispatch" -->
