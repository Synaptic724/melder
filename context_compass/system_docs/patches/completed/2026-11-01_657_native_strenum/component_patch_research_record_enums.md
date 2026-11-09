# Research record enum contract

<!-- BEGIN ENTRY: "LaneState, LaneType and TransitionAct" -->
## Before and after
All three classes currently use names identical to explicit string values. StrEnum adds
string rendering/equality without changing those declared strings, class paths or ordering.
LaneState and TransitionAct share joined and archived: equality must never grant a foreign
member authority in a family-sensitive constructor or payload reader.

## Lifecycle and data
ResearchLane state remains open -> joined or archived; lane type retains its existing policy
meaning and missing-type back-compat. TransitionEntry keeps its strictly typed act and
forward-only journal behavior. Both describe paths return plain values and their ordinary
JSON/from_payload round trips remain byte-compatible for the same fixed inputs.

## Errors and ordering
The direct lane-type constructor refuses foreign enum families but accepts LaneType and
raw supported string tokens. On payload reload, foreign state/type values follow the
existing wrong-type fallback; foreign entry acts raise the existing ValueError. Same-family
members may use the selected string-backed value surface. Unknown raw tokens retain their
existing errors. No new state, ownership, lock or cleanup rule is introduced.

## Validation
Use real pre-change fixed JSON and representative protocol-4 pickles, family-collision
controls and actual ResearchSet creation/journal. Run complete lane, lane-type, transition,
journal and ResearchSet tests and the real cached MutationResearch checkpoint replay.
<!-- END ENTRY: "LaneState, LaneType and TransitionAct" -->