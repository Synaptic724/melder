# Component patch: call sites renamed to the spell_id lookups (find_spell_by_spell_id_2026_10_17)

## Before / after behavior
- `AmbiguousProviderStrategy._describe_candidates`, `GraftRunner._bind_selected`, `RestoreEngine._bind_one_active`
  and `CommandSystem.get_spell_by_id` pass a spell_id that is active (a Phase-3 candidate, a spell just bound, a
  published spell record's id), so `find_spell_by_spell_id` answers what `find_spell_by_id` did.
- `RestoreEngine._live_index_for` passes recorded member ids and reads only `.spell_index`: a parked member's own
  index is the index the old answer's spell belonged to; a member split off into an index with no active spell now
  resolves to its index (was a miss).
- `GraftRunner._merge_members`: its TRIAGE comment (2026-07-12) explains that the old lookup returned the index's
  active spell for any member id, which made graft adoption notch to itself; the comment is kept and corrected to
  say the lookup is exact since this landing's notch. The code keeps `_get_owned_spell`.
- `CommandSystem.get_spell_by_id`'s comment says the id maps answer the spell_id lookup. Nexus publishes active
  spells only (conjure, bind, the notch's record swap), so the published-id check passes active spell_ids; a
  projection not yet refreshed after a notch can still list the outgoing spell_id, which now answers that spell,
  as its record names it (before: the incoming one). The room command keeps its name (asked, not decided).
- Every caller of `Conduit.get_spell_by_id` calls `get_spell_by_spell_id` (ConduitWard, TransferOfOwnership,
  Conduit); `docs/expert/bind-hooks.md` and `agents/MELDER_AGENT_OPERATIONS.md` name the new methods, and the
  latter's "critical lookup trap" (the old answer for a parked spell_id) is rewritten as the exact answer.

## Interface deltas
- None of these surfaces change.

## Validation expectations
- The crystallizer restore and graft suites, the Rift command-surface suites and the ambiguity-report tests, GIL off
  and on.
