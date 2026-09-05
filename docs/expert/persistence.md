# Record structure before you need to restore it

Prerequisites: [checkpoint entry points](../advanced/checkpoints.md) and
[configuration ownership](../advanced/posture.md). Crystallizer records structural
information and source custody. A checkpoint is not a serialization of your live
application objects or their arbitrary mutable state.

## Setup order is part of the example

For the recorded dynamic-world examples, activate custody and research first,
finalize the `SpellbookConfiguration`, configure dynamic frame posture, and then
bind and conjure. This makes recording available when the structural events occur.
Activating a recorder afterward does not imply it observed earlier bindings.

## Profiles, checkpoints, and research sets

| Name | Partitions or identifies |
| --- | --- |
| Persistence profile | The content window receiving recorded emissions |
| Checkpoint ID | A particular checkpoint in ledger creation order |
| Research set | An independent body of declared version history and residency |
| Aetheric frame | A live runtime world |

Switching the active profile moves a pointer. It does not copy the previous
profile's content, and `list_checkpoint_ids()` remains a process-wide ledger read.
The profile lesson compares explicit and active-profile descriptions and exercises
clear versus delete.

## Know where the source came from

Synthetic modules carry recorded source and can be imported without a file.
File-backed source can be retained or read from the recorded path, depending on
policy. The source-view lesson reports kind, origin, availability, and drift rather
than treating all source text as the same evidence.

Continue to [restore](restore.md), [external storage](external-storage.md), or
[recorded source and diffs](research.md) according to the next operation you need.
