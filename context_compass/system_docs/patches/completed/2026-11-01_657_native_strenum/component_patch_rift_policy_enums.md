# Nexus Rift policy enum contract

<!-- BEGIN ENTRY: "RiftAccessMode and RiftCreationMode" -->
## Purpose and boundary
The two concrete modules declare distinct public string-valued policy vocabularies.
Their Python family identities remain separate.

## Before and after
Before: each is an Enum whose explicit values match its lower-case member names.
After: each is a StrEnum with the same names, values, module paths and member order.
String conversion, comparison to equal strings, cross-family equality for equal values,
and JSON encoding follow Python StrEnum semantics; none is misreported as unchanged.

## Interfaces, failures and data
Each existing value constructs its original member. Unknown values still raise ValueError.
The native EnumHelpers public boundary continues to accept only a same-family member or a
raw name string and reject a foreign family, including after cache warming in both orders.
Existing value-based serialized and pickled tokens are accepted only to the extent proved
with actual pre-change data and final-source tests. No new broad alias or fallback is added.

## State, lifecycle and dependencies
Enum members remain immutable singleton values with no cleanup owner. No policy runtime,
permission check, shared logger or ownership-transfer implementation is changed. Preserve
the current helper's type-sensitive bounded cache and its foreign-family rejection.

## Validation
Exercise both complete existing test modules and a focused contract module covering all
members, name/value and order, direct value construction, unknown values, JSON encoding,
pre-change pickle readback, current pickle round trip, and real helper family/cache cases.
Record interpreter, natural exit, source witnesses and failures. User-owned persisted
fixtures beyond these tested representations remain UNKNOWN.

## Ordering and rollback
Read and map the patch before source changes. Add causal regressions, establish their red
baseline without weakening existing tests, then change only the two imports, bases and enum contract docstrings.
A rollback keeps values/module paths and restores both bases; disclose the intentionally
different string semantics instead of promising unchanged equality.
<!-- END ENTRY: "RiftAccessMode and RiftCreationMode" -->