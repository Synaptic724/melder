# Story: binding_manifest_hash - the bind signature becomes a binding manifest with its own SHA256

- Completed: 2026-10-18T23:31:15Z
- Summary: notched 0.2.8258: the binding manifest and its hash (Spell.binding_manifest, Spell.binding_hash) key both creation-cache tiers (generation 23) and ride the SpellCrystal (record 4.3.0); a restore reports binding_changes; the release-note section "A spell's binding is a manifest with its own hash".

## Metadata
- Story ID: STORY-2026-10-18-binding_manifest_hash
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T23:31:15Z

## User Narrative
As an agent, I want how a spell is kept - its address, lifetime, teardown, capability and settings - recorded as a
binding manifest with its own SHA256 beside the spell_id, so that Melder knows exactly when a spell's binding
changed and never reuses what it built for the old binding.

## Value / MRP Alignment
Once the spell_id is the code (S1), the binding needs its own identity: the creation cache and the record rely on
the spell_id covering the binding today (`StructuralSnapshot.structural_key`: "the spell id already covers the
spell's own signature, names, existence and resolvability"). The owner's design keeps that structure as a manifest.

## Ticket Contract
- ENTRY_GATE: S1's component patch approved; this story's component patch approved; the board row.
- EXECUTION_BOUNDARY: the binding manifest and its hash (the Spell builds and carries it, its `describe()` gives it
  as data), the SpellCrystal record, the creation cache's structural key and world stamp, the cache generation;
  tests and docs. Not revalidation (S3).
- DEPENDENCIES: S1 (lands with it).
- EXIT_GATE: a binding change without a code change misses both cache tiers; the SpellCrystal records the
  binding hash and a restore or graft rebuilds the same manifest from the record; byte-identical across
  processes; docs.
- FAILURE_ESCALATION: CONFLICT if another lane takes spell.py; DECISION_REQUEST on which fields the binding
  hash covers.

## Requirements (Functional)
- The manifest holds the spellframe (with its kind and contract), the binding name, the existence, the resolved
  disposal names in order, resolvable and the managed settings; its binding hash is a SHA256 over it, address-free
  and deterministic.
- The Spell carries the manifest and its hash, read-only (`BindingManifest.describe()` gives them as data). The
  SpellCrystal records the binding hash beside the fields it already records, and a restore or graft rebuilds the
  manifest through bind (the owner, 2026-10-18: "make sure you land the binding hash going into crystallizer too");
  the record patch says what a rebuilt manifest whose hash differs from the recorded one does.
- The structural cache keys a payload by spell_id and binding hash, and the world stamp carries every spell's
  binding hash, so the executor tier's full hit needs them too; a cache generation retires the old bundles.
- Nothing else identifies a spell by its binding.

## Requirements (Non-Functional)
- No new lock; the hash is computed once at bind.
- Byte-identical across processes and GIL modes.

## Scope Boundaries
- In scope: the manifest, its hash, the record and the caches' keys.
- Out of scope: revalidation and the store (S3), the refusals (S4), the migration (S5).

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the owner's word to land S1 now, which lands with this story's cache keys (the
  epic's DECISION note of 2026-10-18T15:01:53Z); his confirmation of the conduit-manifest reading (DECISION note
  of 2026-10-18T14:14:10Z).

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-spell_id_hashes_the_object_code
- STORY-2026-10-18-revalidate_on_binding_change

## Tasks (Implementation Checklist)
- [x] Task: the component patches - the manifest (Binding Pipeline, S2 section) and the creation cache's keys
  (component_patch_creation_cache.md), written 2026-10-18.
- [x] Task: the record patch - the binding hash in the SpellCrystal (the owner's word, DECISION note of
  2026-10-18T16:18:35Z), written as component_patch_crystallizer_record.md.
- [x] Task: inventory every spell_id-keyed cache and store (FACT note; the Creations slot goes to S3).
- [ ] Task: red tests; implement; docs; notch with S1; the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Changing only a spell's existence, disposal list, address or resolvable changes its binding hash and not its
  spell_id, and the next conjure misses both cache tiers for it.
- The SpellCrystal records the binding hash, and a restore or graft rebuilds the same manifest and binding
  hash from the record.

## Validation / Test Plan
- `test_changing_only_the_binding_changes_the_binding_hash_not_the_spell_id`,
  `test_a_binding_change_misses_the_creation_cache`; the record round-trip; GIL off and on.

## UX / API / Data Notes
- `Spell` gains the manifest and its binding hash (read-only).

## Risks / Mitigations
- A cache or store keyed by spell_id alone is missed: the inventory task lists them before code.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- The four managed settings are in the binding hash (DECISION note); whether a change of them revalidates or
  only rebinds the pool is S3's question.
- The owner's "conduit manifest" reading is confirmed (the epic's DECISION note of 2026-10-18T14:14:10Z): the
  binding hash is recorded in what the conduit builds and caches the spell from.

## Decision Log
- 2026-10-18T11:45:58Z: filed under EPIC-2026-10-18-spell_identity_is_the_code (the epic's DECISION note).
- 2026-10-18T12:01:17Z: melder_1's files are free (M1-28; the epic's FACT note of 2026-10-18T12:01:17Z); the entry gate
  no longer waits on a release.
- 2026-10-18T14:14:10Z: the conduit-manifest reading confirmed by the owner (the epic's DECISION note).
- 2026-10-18T15:01:53Z: in_progress on the owner's word to land S1 with this story (the epic's DECISION note).
- 2026-10-18T15:45:30Z: the inventory (FACT note), the record field moved to S5 and the managed settings in the hash
  (DECISION note), the component patches and the mapping (PLAN note).
- 2026-10-18T16:18:35Z: the binding hash goes into the SpellCrystal in this landing on the owner's word; point (1)
  of the DECISION note of 15:45:30Z is superseded (DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_binding_pipeline.md (S2 section)
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_creation_cache.md (cache keys)
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_crystallizer_record.md (record)
  - the design's probes are rowed under the epic
- DISPOSITION: promote_to_documentation (the patch docs, at landing)
- CLEANUP_TRIGGER: the patch docs are promoted to the system documents at landing and archived at turn-in

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a spell's identity (its code) versus its binding (how it is kept)
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-10-18T11:45:58Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T11:45:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction (the epic's DECISION note of 2026-10-18T11:45:58Z); the evidence it
    starts from is the epic's FACT note and its probes. Nothing in src/ moves before this story's component patch is
    approved.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:220-270
  IMPACT: The scope, requirements and acceptance above are the plan the patch docs refine.
  NEXT: the component patch with S1's.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T15:45:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The spell_id-keyed caches and stores, read on 0.2.8255 (the inventory task). Both creation-cache tiers
    trust the spell_id to cover the binding: the structural key is {format, spell_id, annotation_refs}, its
    docstring saying "the spell id already covers the spell's own signature, names, existence and
    resolvability"; the world stamp hashes the sorted pool ids, the posture and the sorted borrowed ids; a
    structural hit needs a well-formed payload, the live stamp, replayable and the live key. The executor tier
    classifies with that same stamp: a full hit needs every live payload-eligible id cached and the bundle's
    recorded stamp equal to the live one, else mixed (some ids cached) or full miss; a non-full-hit conjure
    removes every package, restages every live id and records the stamp after them. A meld stages a package
    only for an id the bundle lacks. So under S1 a binding changed under one spell_id would hit both tiers;
    the binding hash in the key and the stamp closes it (component_patch_creation_cache.md). The in-process
    stores need nothing: a fast meld door holds its Spell object and checks its door epoch and context, so a
    cleaned Spell misses (AttributeError) and the full lane rebuilds; per-conduit verdicts are retired on
    register_index and unregister_index (0.2.8219). The record needs no new field in this landing: the
    SpellCrystal records every manifest field and a restore replays them through bind, which rebuilds the
    manifest. UNKNOWN, S3's: whether a slotted store entry kept under a spell_id hands the old object to a
    rebind with another existence (the 2026-10-03 surviving-product ruling); the blast-radius run probes it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:258-287
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:289-323
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:428-482
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:566-622
  - src/melder/aether/spellbook/spellbook_creation_system.py:615-710
  - src/melder/aether/spellbook/spellbook_creation_system.py:1113-1189
  - src/melder/aether/spellbook/spellbook.py:990-1067
  - src/melder/utilities/caching_system/caching_system.py:84-88
  - src/melder/aether/conduit/meld/conduit_meld.py:413-472
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1369-1404
  - src/melder/crystallizer/crystals/spell_crystal.py:1332-1443
  IMPACT: S2's component patches can state the cache keys exactly and leave the record, the doors and the
    verdicts alone; the Creations-slot question goes to S3 with a probe.
  NEXT: The DECISION and PLAN notes below; then the blast-radius run with S1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T15:45:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Within the owner's word to land S1 with S2's cache keys: (1) the binding hash joins the SpellCrystal in
    S5, with the record's other changes and its RecordVersion, not in this landing - the crystal already
    records every field the manifest holds and a restore rebuilds the same manifest through bind, so "the
    record round-trips the manifest" holds without a format change; the Requirements, Acceptance Criteria
    and EXIT_GATE say so. (2) The four managed settings are in the binding hash: a change of them is a
    binding change and misses both cache tiers once (conservative; no emitted plan reads them); whether such
    a change revalidates or only rebinds the pool stays S3's question. (3) Spell builds its manifest in
    `__init__` from its own arguments, so bind, restore and graft need no new keyword.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_binding_pipeline.md:116-143
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_creation_cache.md:1-100
  IMPACT: S2 stays inside spell.py, the new binding_manifest.py and the cache files; S5 owns the record change.
  NEXT: The PLAN mapping below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T15:45:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch section -> implementation -> validation. (1) Binding Pipeline, S2 section -> binding_manifest.py
    (BindingManifest: value fields, `build`, `binding_hash`, `describe`) and spell.py (the `binding_manifest`
    slot appended last, built at the end of `__init__`, the `binding_hash` property, `describe`, kept through
    cleanup like spell_id) -> test_binding_manifest.py: each field moves the hash, nothing else does, two
    processes and GIL modes agree; a bound, a staged and a restored Spell carry the manifest their bind implies.
    (2) Creation-cache patch, Interface Deltas -> structural_snapshot.py (`PAYLOAD_FORMAT` 2, `structural_key`
    with `binding_hash`, `world_stamp` lines `<id>=<binding_hash>`, `payload_well_formed`, the docstrings) ->
    the structural-snapshot tests moved to format 2, a stamp test per binding field. (3) The same patch's
    generation -> caching_system.py (23 "binding_manifest_keys" with its history comment) -> a generation-22
    bundle loads cold. (4) Its docstring rows -> spellbook_creation_system.py (`_build_conjure_cache_state`'s
    comment), generalized_manifest_no_overrides_compiler.py and generalized_manifest.py -> the docstring
    audit. (5) Its integration expectation -> `unique` then `many` in a fresh Aether: structural miss,
    executor mixed, a new provider per meld; the same world twice a full hit. (6) The bind-guard manifest
    regenerated (628 -> 630, with SpellCodeDigest) at the rebuild. spell.py waits for M1-37 (M1-36).
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_binding_pipeline.md:116-143
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_creation_cache.md:52-59
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_creation_cache.md:81-89
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:47-58
  IMPACT: The patch gate's consumption mapping is in place before any S2 code.
  NEXT: The blast-radius run with S1 in a /tmp mirror; read the mailbox for M1-37.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T16:18:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-18): "make sure you land the binding hash going into crystallizer too please".
    Point (1) of the DECISION note of 2026-10-18T15:45:30Z is superseded: the binding hash joins the
    SpellCrystal record in this landing, not in S5; the Requirements, Acceptance Criteria and EXIT_GATE say so
    again. A record patch - the field on the crystal, its RecordVersion, and what restore and graft do with a
    recorded hash, including a rebuilt manifest whose hash differs because the receiving Book's policy
    changed (its disposal order, for one) - is written and linked before any crystallizer code. Points (2)
    and (3) stand.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:629-654
  - context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:194-212
  IMPACT: S2 adds spell_crystal.py and the record version, and restore_engine.py and graft_runner.py where they
    replay the crystal; the PLAN mapping gains the record's row.
  NEXT: Read the crystal, the record version and both replays whole; write the record patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T16:24:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The blast-radius run shows S1 cannot land without S2's keys (the architecture patch's invariant 7): with
    the code digest alone (the unit and component tiers, the GIL off) 12 more component tests failed - 11 in
    test_conduit_component_purge.py, one in test_conduit_component_spellspace_creations.py - and all pass with
    the binding hash in the structural key and the world stamp (test_conduit_component_purge.py 79 of 79).
    Their parametrizations bind one class under several existences, so one spell_id named several bindings
    and a creation-cache bundle built for one binding was replayed for another: purges found nothing to
    remove (0 for 1) and a store came back None. With S2's keys the run's only other S2 effect is the 5
    tests that pin format 1 and the old stamp text, which move to format 2 and the new stamp lines.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/blast_radius/triage.md:141-148
  - context_compass/artifacts/spell_identity_20261018/blast_radius/triage.md:114-120
  - context_compass/artifacts/spell_identity_20261018/blast_radius/mirror/mirror_structural_snapshot.diff:1-31
  IMPACT: The creation-cache patch's interface (format 2, the stamp lines, generation 23) is confirmed by the run;
    S1 and S2 stay one landing.
  NEXT: The crystallizer record patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T16:32:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch section -> implementation -> validation for the record (component_patch_crystallizer_record.md),
    beside the PLAN note of 2026-10-18T15:45:30Z. (1) Interface Deltas, SpellCrystal -> spell_crystal.py:
    the `_binding_hash` slot appended, captured from `spell.binding_hash` with the bind-signature fields, the
    `binding_hash` property, the `describe()` key, `cleanup`'s del, the class and `__init__` contracts -> the
    crystal of a class, a staged version and a managed spell carries its spell's binding hash; cleanup
    deletes it. (2) RecordVersion -> record_version.py: CURRENT 4.3.0 and its history comment -> CURRENT is
    4.3.0 and a 4.2.0 payload passes `check_readable`. (3) RestoreReport and RestoreEngine -> restore_engine.py:
    `_binding_changes`, `record_binding_change`, `describe()["binding_changes"]` and its cleanup; the engine's
    `_record_binding_change`, called by `_bind_one_active` and `_bind_one_staged` -> a restore under the
    recording policy reports none; under another disposal priority one per changed binding, the spell_ids
    unchanged and grants and selections found. (4) The docstring rows -> restore_engine.py and
    graft_runner.py -> the documentation ritual. Row (1) of the earlier mapping (spell.py's `binding_hash`)
    comes first.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_crystallizer_record.md:1-99
  - context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:214-240
  IMPACT: The patch gate's consumption mapping for the record is in place before any crystallizer code.
  NEXT: S1 and S2 built in a /tmp working mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:05:55Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: BindingManifest is written from the S2 section of the Binding Pipeline patch and staged with the digest
    (src/melder/aether/spellbook/bind/binding_manifest.py; the mirror too): twelve value fields in hash order,
    `binding_hash` the SHA256 of "v1-binding" and one `<field>=<repr>` line each, `build(...)` from a Spell's
    arguments (enums by name, the spellframe as text, the name sequences as tuples, the queue timeout as a
    float, so equal settings written differently hash alike), read-only properties, `describe()` and no
    cleanup (a value record). The patches said `Spell.describe()` shows both; a Spell has no `describe()`
    (spell.py searched), so the Binding Pipeline and architecture patches and this story say: the Spell
    carries `binding_manifest` and `binding_hash` read-only, and `BindingManifest.describe()` gives the data.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/staged/src/melder/aether/spellbook/bind/binding_manifest.py:1-408
  - src/melder/aether/spellbook/spell.py:1-1972
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_binding_pipeline.md:133-137
  IMPACT: S2's Spell edit is the slot, the build call and the `binding_hash` property; no describe method.
  NEXT: spell.py's manifest in the mirror; then the creation-cache keys.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:51:07Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S2 is applied with S1 to the /tmp working mirror in the same pass. The cache keys (edits_cache):
    structural_snapshot.py 8 - PAYLOAD_FORMAT 2, the key's `binding_hash`, the world stamp's
    `<spell_id>=<binding_hash>` lines for the pool's and the borrowed spells, the class, key and stamp
    docstrings; caching_system.py 3 - generation 23 "binding_manifest_keys" and its history comment;
    spellbook_creation_system.py 2; the generalized compiler's comment and the manifest's docstring. The
    crystal's record (edits_crystal): spell_crystal.py 7 - the `_binding_hash` slot captured from
    `spell.binding_hash`, its property, `describe()`'s key and cleanup's del; record_version.py CURRENT
    4.3.0; restore_engine.py 20 - RestoreReport's `binding_changes` (`record_binding_change`, its describe
    key and cleanup) and the engine's `_record_binding_change`, called from `_bind_one_active` and
    `_bind_one_staged`, with the docstrings; graft_runner.py 3 docstrings. The smoke's bound class
    carries its manifest and binding hash, the GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/scripts/edits_cache.py:1-164
  - context_compass/artifacts/spell_identity_20261018/scripts/edits_crystal.py:1-303
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_s1s2_src.diff:1-2018
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_smoke_s1s2_gil0.txt:1-6
  IMPACT: S2's source edits are complete in the mirror; its tests follow S1's in the same tranche.
  NEXT: The red tests for the manifest, the cache keys and stamp (format 2, generation 23), the record (4.3.0)
    and restore's binding_changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T18:44:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S2's share of the whole-tree run (S1's MEASURE note of this time): 213 failing tests faked or pinned
    what S2 changed - the fake Spells of the crystal harness, the crystallizer tests and the structural
    snapshot tests had no `binding_hash`, and the pins of PAYLOAD_FORMAT (2), the cache generation history
    (23, "binding_manifest_keys") and RecordVersion (4.3.0; 4.1-4.3 records readable) had moved.
    tests_edits_doubles.py rewrites them: the fakes take a binding hash derived from their spell_id, and
    two new structural-key tests prove the key and the world stamp follow the binding hash under one
    spell_id. The ten files with the new test_spell_crystal_binding_hash.py pass, 350 tests, GIL off.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_doubles.py:1-234
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_doubles_gil0.txt:1-6
  - context_compass/artifacts/spell_identity_20261018/staged/tests/unit/melder/crystallizer/test_spell_crystal_binding_hash.py:1-79
  IMPACT: S2's own tests are green in the mirror; its remaining failures are the ordered-disposal replay's
    (category c, 22), whose restores now report binding changes, and the reversed premises (d).
  NEXT: With S1's tranche: categories (b) to (e), the replay rewrite among them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T19:17:19Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The ordered-disposal replay asserts S2's restore report end to end: a Book restored under another
    disposal policy keeps both members' spell_ids (none enters the identity map), reports each member's
    binding change - recorded and live hash, live equal to the restored spell's `binding_hash` - and
    resolves the requested parked selection and the regranted contract; a restore under the recorded
    policy reports no binding change. The captured index's staged member is a second version of the
    service (`StagedDisposalService`, module level, bound under the service's address), because staging
    the service again is refused; restore and graft import it by module and qualname. Two tests that
    asserted translated ids are renamed for what they assert now (`..._under_another_policy_...`).
    Batch ordered_replay (15 edits) closes the file's 23 failed ids: 23 pass, the GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_ordered_replay_gil0.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_ordered_replay_gil1.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_ordered_replay.py:1-159
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_s1s2_src.diff:1597-1877
  IMPACT: S2's restore contract (record 4.3.0: kept ids, binding changes reported, never a shortfall) is
    under test; S2's remaining failure is the managed reversed premise (d).
  NEXT: With S1's tranche: (c) in the 20 other files, then (d) and (e).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T19:59:24Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S2's last failure is closed: the managed reversed premise is rewritten (batch one_object_b) - the same
    class bound unique, managed and managed with a limit is one spell_id and three bindings, each with its
    own binding hash (`test_a_managed_binding_keeps_the_spell_id_and_moves_the_binding_hash`). With the
    tranche done, the whole tree on the mirror fails only melder_1's 18 S8 tests, the GIL off and on (S1's
    MEASURE note of 2026-10-18T19:59:24Z).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_one_object_b.py:1-472
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_one_object_b_gil0.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_one_object_b_gil1.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2_run2/summary.txt:1-14
  IMPACT: S2's tests are green in the mirror; it lands with S1.
  NEXT: The landing pass with S1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T23:18:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S2's half of the tests documents landed with S1's (S1's MEASURE note of this time): the binding manifest's
    and the crystal's binding-hash tests, the ordered-disposal replay's binding changes, the managed binding's
    three binding hashes, the harness's binding hash and cache generation 23.
  EVIDENCE: context_compass/system_docs/tests_components.md:3734-3747
  IMPACT: S2's documents are current with S1's.
  NEXT: With S1: the graph, the notches, the release note, the docs checks, the closure, the rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:26:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S2 notched 0.2.8258 with S1's 0.2.8257 (S1's FACT note of this time); the running note's S2 section,
    "A spell's binding is a manifest with its own hash", names the two read-only properties, both cache tiers'
    key, record 4.3.0 and the restore report's binding_changes.
  EVIDENCE: release_docs/next_version_release.md:1-3
  IMPACT: S2's source is versioned and documented for users.
  NEXT: With S1: the docs checks, the closure, the rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:31:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: State transition in_progress -> done (notched 0.2.8258): the owner's word to land S1 with
    S2 and the crystallizer call are met - source, tests (whole tree green but melder_1's 18 S8 tests, the GIL
    off and on), examples, docs and their checks, the four system documents, the graph, the release note -
    and the rebuild follows as the landing's last step.
  EVIDENCE: context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:462-488
  IMPACT: The story moves to completed/; S3-S5 continue under the epic.
  NEXT: The rebuild for 0.2.8258.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: the binding becomes a manifest with its own SHA256, recorded and part of the caches' keys.
- State: in_progress (melder_0), implementation: lands with S1 on the owner's word (the epic's DECISION note of
  2026-10-18T15:01:53Z), the binding hash in the SpellCrystal included (his word, DECISION note of
  2026-10-18T16:18:35Z); spell.py is back since S9 landed as 0.2.8256 (M1-38).
- Done: the inventory (FACT note), the component patches (Binding Pipeline S2 section, creation cache), the
  managed settings in the hash (DECISION note), the mapping (PLAN note); the record deferral superseded
  (DECISION note).
- Done since: the blast radius recorded (MEASURE note of 2026-10-18T16:24:12Z); the record patch written and
  mapped (PLAN note of 2026-10-18T16:32:46Z).
- Done since: BindingManifest written; the patches corrected - a Spell has no `describe()` (FACT note of
  2026-10-18T17:05:55Z).
- Done since: the cache keys (format 2, generation 23) and the crystal's record (4.3.0, the binding hash,
  restore's binding_changes) applied with S1 to the /tmp working mirror (FACT note of 2026-10-18T17:51:07Z).
- Done since: the doubles of S2's fields and pins rewritten and green in the mirror (FACT note of
  2026-10-18T18:44:20Z).
- Done since: the ordered-disposal replay rewritten - kept ids and the reported binding changes,
  23 green with the GIL off and on (MEASURE note of 2026-10-18T19:17:19Z).
- Done since: the managed reversed premise rewritten - one spell_id, three binding hashes - and the
  whole tree green but melder_1's 18 S8 tests, the GIL off and on (FACT note of 2026-10-18T19:59:24Z).
- Done since: applied to the repository with S1 and committed by the owner (5e3800c7a); promoted
  into the source system documents (S1's FACT note of 2026-10-18T21:51:31Z).
- Done since: the examples rewritten with S1 (S1's MEASURE note of 2026-10-18T22:52:11Z).
- Done since: the tests system documents (FACT note of 2026-10-18T23:18:31Z).
- Done since: notched 0.2.8258 with S1's 0.2.8257 (FACT note of 2026-10-18T23:26:28Z).
- Closed: 2026-10-18T23:31:15Z - notched 0.2.8258; landed on the owner's word
  (the epic's DECISION notes of 2026-10-18T15:01:53Z and 16:18:35Z).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
