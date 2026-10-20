# Component patch: call sites renamed to the spell_id lookups (find_spell_by_spell_id_2026_10_17)

## Before / after behavior
- `AmbiguousProviderStrategy._describe_candidates`, `GraftRunner._bind_selected` and
  `RestoreEngine._bind_one_active` pass a spell_id that is active (a Phase-3 candidate, a spell just bound), so
  `find_spell_by_spell_id` answers what `find_spell_by_id` did.
- `RestoreEngine._live_index_for` passes recorded member ids and reads only `.spell_index`: a parked member's own
  index is the index the old answer's spell belonged to; a member split off into an index with no active spell now
  resolves to its index (was a miss).
- `GraftRunner._merge_members`: its TRIAGE comment (2026-07-12) explains that the old lookup returned the index's
  active spell for any member id, which made graft adoption notch to itself; the comment is kept and corrected to
  say the lookup is exact since this landing's notch. The code keeps `_get_owned_spell`.
- The Rift room lookups are renamed and made exact in their own component patch
  (component_patch_rift_command_lookups).
- Every caller of `Conduit.get_spell_by_id` calls `get_spell_by_spell_id` (ConduitWard, TransferOfOwnership,
  Conduit); `docs/expert/bind-hooks.md` and `agents/MELDER_AGENT_OPERATIONS.md` name the new methods, and the
  latter's "critical lookup trap" (the old answer for a parked spell_id) is rewritten as the exact answer.
- The UX examples that name the old methods (ten under `UX_and_AIX_experiences/`) call the new names. Two taught
  and asserted the old answer for a parked spell_id and now state and assert the exact one: expert 17 (its header's
  "Every public spell_id->object lookup ... resolves any lineage spell_id to ... the currently ACTIVE member" and
  its lookup block) and expert 26 (its closing lookup of the staged spell_id). `04_expert/_concept_map.txt` keeps
  its dated 2026-08-03 retraction record as written: it is history.

## Interface deltas
- None of these surfaces change.

## Validation expectations
- The crystallizer restore and graft suites, the Rift command-surface suites and the ambiguity-report tests, GIL off
  and on; the UX example harness (`UX_and_AIX_experiences/pytest_examples`).
