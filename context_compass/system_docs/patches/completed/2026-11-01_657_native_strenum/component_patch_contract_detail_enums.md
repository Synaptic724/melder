# Contract detail enum compatibility

<!-- BEGIN ENTRY: "Contract perspectives and detail reasons" -->
## Component and before/after
ContractTypes marks initiated/received perspectives and DetailReason marks why a detail
exists. Both currently use numeric Enum values. Their exact current names become string
values under StrEnum without changing which rows are granted, borrowed or removed.

## Interfaces and invariants
Historic integer by-value construction and captured numeric pickles remain readable;
unknown values raise ValueError. Direct .value changes to string and is release-noted.
Detail and IndexDetail MUST retain strict enum-family validation despite string equality.
Ward rollback snapshots retain members; Crystallizer emits identical plain name fields.
Grant/borrow ownership, sources, rollback, teardown and lock order are unchanged.

## Ordering, validation and rollback
Read both enum definitions, Detail, ward snapshot/restore and actual Crystallizer
projection. Run causal tests before modifying definitions. Validate old numeric
pickles, exact strings and real strict detail construction, then relevant ward/transfer
and real contract record/restore tests. Roll back both enum bases, strings and legacy
readers together. Unknown external direct numeric consumers remain UNKNOWN.
<!-- END ENTRY: "Contract perspectives and detail reasons" -->