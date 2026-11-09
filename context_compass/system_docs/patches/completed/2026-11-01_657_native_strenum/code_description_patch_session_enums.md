# Session enum compatibility control flow

<!-- BEGIN ENTRY: "Exact old values and stable session projections" -->
## Enum by-value reads
Each enum's missing-value handler maps only its explicit historical lowercase strings to
the corresponding member. Ordinary string subclasses are allowed; other enum families
are not coerced by this fallback. All other missing values return None and raise ValueError.

## Session projections
Replace the session's status/policy .value projections used by its own snapshot and error
messages with the equivalent historical lowercase member-name tokens. Do not change
transaction-type projections or any state-machine condition.

## Test oracle
The existing BROKEN-versus-ABORTED test retains its identity assertion, changes only the
direct value expectation to the selected uppercase name and adds the old lowercase
constructor check. The new tests verify real session lifecycles and captured old pickles.
<!-- END ENTRY: "Exact old values and stable session projections" -->