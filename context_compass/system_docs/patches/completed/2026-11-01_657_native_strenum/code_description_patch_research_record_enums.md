# Research record enum family control flow

<!-- BEGIN ENTRY: "Family-aware lane and entry hydration" -->
## Direct lane-type input
In ResearchLane.__init__, before by-value LaneType construction, reject an enum from a
different family through the existing unknown-lane-type ValueError path. Preserve raw
strings, same-family members, defaults, existing wording shape and side-effect order.

## Payload input
ResearchLane.from_payload treats a foreign enum lane_type like another wrong-typed value,
using the existing default-lane/freeform fallback. It treats a foreign enum state as a
wrong-typed state and keeps the default open state. A same-family string enum is accepted.
TransitionEntry.from_payload rejects an enum from another family as an invalid act, while
accepting plain strings and same-family string-backed acts. Keep existing missing/unknown
error paths and do not replace ordinary JSON conversion.

## Evidence
Causal tests cover an actual LaneState/TransitionAct joined collision in both readers, a
foreign equal lane-type input and existing plain JSON payloads. A real cache/reload case
checks that record behavior remains intact.
<!-- END ENTRY: "Family-aware lane and entry hydration" -->