# Nexus configuration enum migration contract

<!-- BEGIN ENTRY: "Frame mode, room type and validation mode" -->
## Boundary and before/after
NexusFrameMode, RiftSpaceType and RiftValidationMode currently carry string values identical
to their declared names. Convert only their bases to StrEnum and document the new string and
cross-family equality; keep all values, member names, order and module paths.

## Configuration and state contracts
NexusConfiguration and RiftConfiguration continue to normalize raw names through the native
family-sensitive helper. The raw historical "dynamic" room selector still maps to codegen.
A foreign enum equal to "dynamic" must not use that special case to bypass family validation.
Nexus configuration emission must convert every enum to its name before primitive string
handling, so the in-memory NexusCrystal and detached checkpoint contain plain strings.
Reload keeps its existing recorded-name normalization and frozen-state behavior.

## Persistence and errors
Current major-5 recorded names remain readable; new emissions use the same plain strings.
Direct RiftSpaceType("dynamic") remains ValueError, and unknown/foreign configuration values
remain rejected. Do not narrow accepted ordinary string subclasses or alter other fields.
A checkpoint/JSON/reload test must use the real hosted recorder rather than a mock record.

## Validation and risks
Test all declared names and values, ordinary constructor and JSON behavior, old pickle
representatives, both config setters with legacy raw dynamic and foreign equal StrEnum,
typed same-family inputs, and a real in-memory checkpoint/reload. Preserve the existing
CLEANED old/new cache tests and major-version admission. Run full existing config/enum
modules. External data formats beyond the exercised contracts remain UNKNOWN.
<!-- END ENTRY: "Frame mode, room type and validation mode" -->