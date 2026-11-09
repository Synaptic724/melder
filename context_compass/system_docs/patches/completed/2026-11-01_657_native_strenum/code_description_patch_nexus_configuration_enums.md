# Nexus configuration enum boundary control flow

<!-- BEGIN ENTRY: "Enum projection and dynamic alias validation" -->
## Emission path
In NexusConfiguration.emit_configured_twin_when_recording, classify an Enum before checking
primitive string/int/float/bool values. Store property_value.name for an enum, preserve the
existing scalar, collection and fallback branches and keep the same emission owner and order.
This makes a StrEnum a plain name in NexusCrystal and the checkpoint payload.

## Input path
In each configuration's existing space-type normalization, recognize the exact legacy
"dynamic" spelling only when the input is a str and not an Enum; map that spelling to
RiftSpaceType.codegen. Pass all other values to EnumHelpers unchanged. A foreign StrEnum
with value "dynamic" therefore reaches the existing foreign-family refusal rather than
being translated. Ordinary str subclasses remain accepted as before.

## Validation and failure
No new cache, state, lock, lifecycle or rollback mechanism. Retain the helper's same-family
passthrough, unknown-name error, type-sensitive cache and original string matching. Exercise
raw alias success, foreign alias refusal and real record/reload values in both directions.
<!-- END ENTRY: "Enum projection and dynamic alias validation" -->