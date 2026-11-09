# Frame system-state enum compatibility

<!-- BEGIN ENTRY: "Frame posture exact strings and recording" -->
## Component and interface
SystemState selects automatic or dynamic frame posture. It currently uses integer
Enum values 1 and 2. It becomes StrEnum with exact member-name values, while old
numeric inputs and captured enum pickles remain readable. Direct .value changes from
integer to string and is release-noted.

## State, failure and persistence boundaries
AethericFrameConfiguration normalizes typed inputs using EnumHelpers. Its recording
loop must project a SystemState member to its plain .name before checking primitive
strings; the emitted in-memory twin and JSON keep the old plain strings. The actual
frame posture, freeze lifecycle, rejection paths, automatic/dynamic link and ownership
transfer gates, locks and record-major admission remain unchanged.

## Order, validation and rollback
Read the enum, frame configuration, twin and relevant tests. Test old pickles and
numeric input, exact values, foreign enum rejection, actual emitted type and record,
checkpoint replay and posture/ownership behavior. Roll back enum and projection
together. External direct numeric-output consumers remain UNKNOWN.
<!-- END ENTRY: "Frame posture exact strings and recording" -->