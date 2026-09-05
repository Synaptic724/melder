# Survey first, then choose detail

Prerequisite: [opening a Rift](nexus.md). Start at `rift.space.frame_viewer`.
The host-level multi-frame view can enumerate frames without selecting one.
The frame, conduit, and spell views require a frame name.

## Control the amount you read

Use `list_*` to discover names and IDs, a brief description to decide what matters,
then detail or a specific facet for the selected object. For spells, the ladder is
`describe_spell_brief`, `describe_spell`, `describe_spell_detail`, and
`describe_spell_payload`. Source, binding, identity, resolution, and research reads
let a caller request a particular concern.

The viewer lessons inspect the method surface and show that a fresh Rift can have
an empty assigned-frame set. An empty survey is different from a frame-local
request that lacks the required target.

## Missing is not always absent

A visibility-filtered description may omit a section because it does not exist
or because this Rift may not see it. Use the missing-section/visible-surface probes
to understand that boundary. They report withheld section names without exposing
their hidden payload bodies.

On the facade, `frame_name` selects the frame. On a view already bound to a frame,
an optional frame name can instead be an assertion that it matches. Read the
specific signature rather than treating those two surfaces as interchangeable.
