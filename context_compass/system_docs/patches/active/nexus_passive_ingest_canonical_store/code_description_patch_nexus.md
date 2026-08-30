# code_description_patch_nexus

## Trigger justification (why this file is required)
This patch introduces a non-trivial internal control-flow split:
- producers publish directly into private Nexus methods
- frame posture gates whether publication is accepted
- passive canonical record hosting must remain separate from interactive
  `Nexus.enable(...)`
- canonical store mutation and index maintenance must stay centralized in
  Nexus

That is implementation-guiding enough to warrant a code-description patch.

## Control-flow description (pseudocode level, not production code)
1. Producer reaches a stable mutation point:
   - frame posture bound during conjure
   - root conduit created / linked / severed / cleaned
   - spell bound after conjure
   - spell version advanced
   - spell ownership transferred or removed
2. Producer optionally short-circuits on its local cached
   `_nexus_publish_enabled` flag.
3. Producer calls one private Nexus publish/remove method.
4. Nexus resolves the frame posture from its fast frame-posture cache.
5. If no posture exists, or `rift_enabled` is false:
   - return early
   - do not mutate the canonical store
6. If publishable:
   - ensure the canonical store / frame grouping exists
   - upsert/remove the relevant primary record
   - update secondary indexes
7. Interactive `Nexus.enable(...)` remains untouched by this path.

## Edge/error behavior and rollback semantics
- No bound frame posture:
  - publication returns early
- `rift_enabled=False`:
  - publication returns early
- malformed record payload:
  - fail fast inside Nexus private methods
- record/index mismatch:
  - fail fast during the private Nexus mutation path

## Invariants and idempotency expectations
- `FrameRecord` publish should be idempotent for the same frame posture
- repeated root-conduit publish/update should overwrite the canonical record
  deterministically
- repeated spell publish for the same `(spellbook_id, spell_id)` key should
  overwrite deterministically
- `spell.spell_id` should remain aligned with `spell_index.selected_spell_id`
- secondary indexes must always match the primary stores after each mutation
- passive ingest must never require `_require_enabled()`

## Explicit non-goals
- This file does not define viewer/query semantics
- This file does not define eventstream mechanics
- This file does not define ACL filtering
- This file does not define backfill scanning after interactive enablement

## Validation focus points
- validate passive publication before `Nexus.enable(...)`
- validate `rift_enabled` gating
- validate root-only conduit publication in the first slice
- validate index consistency after update/remove paths
- validate spell version/removal/ownership continuity when that extension lands
