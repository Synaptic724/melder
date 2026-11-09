# Conduit Runtime contract
<!-- BEGIN ENTRY: "ConduitState terminal name" -->
## Purpose and boundary
ConduitState declaration and native public resolve/string boundary.
## Before and after
Rename only cleaned to CLEANED; normal, lesser, pooled_lesser and values1-4 remain.
## Interface and errors
No lowercase Python alias. str(CLEANED) MUST remain cleaned. resolve accepts canonical and
legacy/mixed-case input names through EnumHelpers; foreign members and invalid values refuse.
## State and lifecycle
No lifecycle transition, pooling, root/lesser ownership, cleanup or lock change.
## Failure delta
Changing declaration casing must not break supported external string resolution.
## Dependencies and order
Qualify EnumHelpers first; land definitions and direct typed references together.
## Validation and unknowns
Run the complete ConduitState module and name/value regressions. Discover actual runtime references;
do not create a lifecycle consumer from a search lead. Declaration/source94 is fully read.
<!-- END ENTRY: "ConduitState terminal name" -->
