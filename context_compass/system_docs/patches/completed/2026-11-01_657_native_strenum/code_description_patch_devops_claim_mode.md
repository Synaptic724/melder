# DevOps claim-mode projection

<!-- BEGIN ENTRY: "Retain scope-claim and blocking wire tokens" -->
## Flow
Exact-name enum values represent live claims. The missing-value hook reads old
x/s/ix tokens. Strategies project each member to its prior token, the request
manager normalizes tokens through the enum and projects them again, and the
embargo converts incoming claim tokens to members before its identity matrix.
Blocking evidence projects held members back to the original token.

## Contract
Unknown values keep raising. Existing claim modes, ordering, all-or-nothing
semantics and ownership remain unchanged. Tests must cover live contention and
the request and strategy boundaries, not only enum conversion.
<!-- END ENTRY: "Retain scope-claim and blocking wire tokens" -->
