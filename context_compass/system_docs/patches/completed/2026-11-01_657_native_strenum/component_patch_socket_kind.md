# Socket kind string and numeric row compatibility

<!-- BEGIN ENTRY: "Exact names and stable numeric compiler codes" -->
## Before and after
SocketKind becomes an exact-name StrEnum; original 1-5 numeric construction and
captured pickles resolve to the same members. A bounded class projection returns
those old numeric codes for real SocketKind members and preserves other objects'
.value behavior. A missing .value still raises AttributeError to its caller.

## Consumers
Phase 5 edge and Phase 10 override rows, Phase 8 topology signature, the site graph
parameter rows and the unresolved-input comparison use the numeric projection.
Their emitted values and signature inputs stay numeric. The site parameter field's
docstring states this rather than identifying its integer with the new .value.

## Validation
Test all five codes, old pickles, real row producers and fallback behavior, then
existing site-plan, unresolved-input and cached replay tests. Direct numeric .value
and default str rendering are breaking representation changes and are disclosed.
<!-- END ENTRY: "Exact names and stable numeric compiler codes" -->
