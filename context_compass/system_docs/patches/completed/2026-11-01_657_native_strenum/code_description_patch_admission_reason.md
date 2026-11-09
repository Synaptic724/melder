# AdmissionReason exact legacy reader

<!-- BEGIN ENTRY: "Old reason values and stable descriptions" -->
## By-value read
On a missing enum value, map only the five explicitly listed old lowercase reason strings
to their matching members. Accept ordinary string subclasses and refuse other enum
families in this fallback. Return None for all other values, preserving normal ValueError.

## Diagnostic projection
AdmissionResult.describe renders each selected reason's original lowercase token from its
name. Retain the current evidence ordering, admitted/refused output shape and cleanup owner.

## Evidence
Test the five captured old pickle bytes, exact old/new strings, rejected unknowns and
the actual diagnostic strings, followed by the full mediator unit directory.
<!-- END ENTRY: "Old reason values and stable descriptions" -->
<!-- BEGIN ENTRY: "AdmissionReason stable value control" -->
## Superseding control flow
Retain the original Enum constructor and reason.value diagnostic projection. No legacy
fallback or uppercase conversion is installed. The regression pins original tokens and old
pickle payloads; any future value-contract change requires a compatible owner disposition.
<!-- END ENTRY: "AdmissionReason stable value control" -->

<!-- BEGIN ENTRY: "AdmissionReason exact-string compatibility control" -->
The stable-value control is superseded by Mark's correction. Use the earlier exact
legacy-reader and lower-case diagnostic projection; do not change admission logic.
Test old/new strings, captured old pickle bytes, unknown inputs and verdict output.
<!-- END ENTRY: "AdmissionReason exact-string compatibility control" -->