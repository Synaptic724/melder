# AdmissionReason canonical value contract

<!-- BEGIN ENTRY: "Admission reasons and diagnostic evidence" -->
## Before and after
Five uppercase AdmissionReason names currently have lowercase string values. After the
change their values equal their names; class identity, member order and reason meaning stay.

## Compatibility and output
The five exact old lowercase values and their old pickle representations remain readable.
Unknown, whitespace and mixed-case inputs remain ValueError. AdmissionResult.describe
continues rendering the prior lowercase code strings, preserving machine-readable evidence;
direct enum .value, str and JSON now use uppercase names by the owner's selection.

## Lifecycle and validation
Admission verdict construction, cleanup ownership, wait/claim logic and evidence ordering
are unchanged. Test every old and new token, old pickle, unknown values, real verdict
description and complete native mediator unit consumers.
<!-- END ENTRY: "Admission reasons and diagnostic evidence" -->
<!-- BEGIN ENTRY: "AdmissionReason stable value hold" -->
## Superseding disposition
The earlier uppercase-value selection is superseded. Preserve all five original lowercase
values and their documented stability contract; no enum or verdict source modification is
selected. Verify direct JSON, old pickle and real verdict output on the restored source.
<!-- END ENTRY: "AdmissionReason stable value hold" -->

<!-- BEGIN ENTRY: "AdmissionReason exact-string owner disposition" -->
Mark selected exact member-name values, superseding the stable-value hold. Apply the
original canonical-string entry: keep the five lowercase inputs and captured pickles
readable, keep verdict descriptions lowercase, and document the direct value change.
The existing component boundaries, ownership, lifecycle and failure behavior stay.
<!-- END ENTRY: "AdmissionReason exact-string owner disposition" -->