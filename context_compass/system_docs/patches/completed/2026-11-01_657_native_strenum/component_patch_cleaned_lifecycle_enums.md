# CLEANED lifecycle enum compatibility

<!-- BEGIN ENTRY: "Terminal name values and recorded intent" -->
## Component and before/after
SpellValidity, ConduitState and RecordedUnitState carry the #656 terminal name
CLEANED. They currently use Enum with numeric or lowercase string values; they become
StrEnum with each value exactly equal to its existing member name. Member order and
canonical Python names remain unchanged.

## Interface and persistence
Old numeric by-value inputs and old recorded-unit lowercase cleaned input/pickles
remain readable; direct .value changes to a string and is release-noted. ConduitState
continues rendering lowercase for diagnostics. The native helper retains strict family
checks and type-sensitive caching. Both restore drivers still treat old cleaned and
canonical CLEANED as terminal; enabled/disabled and record-major admission stay.

## Validation and rollback
Update the old #656 direct-value/base oracle to assert new exact strings plus all old
input mappings without dropping name/order or family checks. Add captured old pickle
fixtures, then run native unit and real sequential/parallel cached restore controls.
Do not change lifecycle, ownership, locks or restore logic. Roll back all three enum
bases, values/readers and the test oracle together. External numeric consumers UNKNOWN.
<!-- END ENTRY: "Terminal name values and recorded intent" -->