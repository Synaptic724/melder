# Terminal lifecycle enum legacy readers

<!-- BEGIN ENTRY: "Preserve terminal old inputs and replay" -->
## Lookup behavior
SpellValidity maps numeric 1-6 to the original members and ConduitState maps 1-4.
RecordedUnitState maps only the old lowercase cleaned value to CLEANED; enabled and
disabled use their unchanged names. Unknown inputs still refuse. EnumHelpers resolves
names and rejects foreign members before string handling, with type-sensitive caching.
ConduitState.resolve still refuses raw numbers even though direct enum construction
supports legacy numbers; its string rendering remains lowercase.

## Replay behavior
No restore code changes: folded legacy cleaned and canonical CLEANED states continue
to skip Nexus and MutationResearch reconstruction, with existing shortfalls; live
states and major admission remain unchanged. Verify actual cached records on both
sequential and parallel drivers.
<!-- END ENTRY: "Preserve terminal old inputs and replay" -->