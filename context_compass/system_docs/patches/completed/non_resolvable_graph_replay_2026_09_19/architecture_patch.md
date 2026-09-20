# Architecture Patch: Non-resolvable graph publication and replay

- Patch ID: non_resolvable_graph_replay_2026_09_19
- Owner: updater_0
<!-- BEGIN ENTRY: Native graph policy and durable replay -->
## Scope and Interfaces
Publish immutable capability and value-only selected dependency/reference/base relationships in the
existing Nexus binding payload. Expose incoming/outgoing relationships through ACL-filtered ViewSpell
and its FrameViewer facade. Keep existing source/history and version identity; do not infer internal-use
or lifecycle ownership edges. Metadata publication is outside the meld hot path.

Capture Spell.resolvable in SpellCrystal; replay it through active/staged and graft bind verbs. Legacy
absence means True. The existing record major gate advances to 2 because old readers must not silently
ignore False and enable construction. No package version or new invalidation system is introduced.

## Invariants and Migration
1. Native lookup/constructor behavior remains as already qualified; no argument preflight.
2. Nexus describes registrations; graph navigation exposes only visible source/target nodes.
3. Crystal payloads contain plain values only. Graph sockets reconstruct through normal compilation
   of restored bindings and selected versions; recorded runtime ULIDs are never reused.
4. Add red graph/capture/replay tests, implement publication and forwarding, then qualify existing
   Nexus/research/record/graft behavior and regenerate assets.

## Rollback and Coverage
Revert only this patch's fields/publication and replay forwarding; preserve existing work. The task
TASK-2026-09-19-publish-and-replay-non-resolvable-definitions covers S5/S6 under the active epic.
Unknown broader source-history limitations retain existing behavior; no automatic body-versioning.
<!-- END ENTRY: Native graph policy and durable replay -->
