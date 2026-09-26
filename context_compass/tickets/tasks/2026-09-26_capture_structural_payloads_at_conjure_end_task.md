# Task: Capture per-spell structural payloads (phase 3-4 rows) beside the executor payloads at conjure end

## Metadata
- Task ID: TASK-2026-09-26-capture-structural-payloads-at-conjure-end
- Story: STORY-2026-09-26-structural-snapshot
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T16:47:56Z
- Updated: 2026-09-26T17:29:25Z

## Objective
The capture half of I-1 (architecture patch deltas 1-4 and 6; code description step 8): a stateless snapshot
seam beside the compiler phases builds, for every spell whose phase 3 ran live in a conjure, a marshal-safe
structural payload `{"key", "world_stamp", "replayable", "phase3", "phase4"}` from the artifact, the registered
topology and the lineage verdict; `CachingSystem` gains a top-level `structural_payloads` map (upsert / get /
remove / cached ids; transfer drops it) at generation 15; the conjure-end staging writes the payloads next to
the executor payloads through the existing emit. Nothing reads the payloads yet (hydrate is the next task).

## Ticket Contract
- ENTRY_GATE: patch docs approved; C-C landed (task 2 in review or done); melder_0's answer on the cache-path
  files (F0-17) or the owner's ruling; the active board row routes here; Propose->Confirm before any src edit.
- EXECUTION_BOUNDARY: a new module beside the phases (`spell_compiler/structural_snapshot/`), the
  `CachingSystem` envelope (`utilities/caching_system/caching_system.py`: key enumeration, four store methods,
  `CACHE_VERSION_HISTORY` 15, transfer), the conjure-end staging in `spellbook_creation_system.py`
  (`_activate_conjured_conduit` / `_stage_spell_payloads_at_conjure_end` neighbourhood), unit tests for the row
  builders, key, stamp, verdict and envelope, one component test (cold conjure writes a payload per spell), the
  patch docs at review. NOT in scope: reading the payloads (hydrate task), the conjure reorder, phases 4-11.
- DEPENDENCIES: the patch docs; task 2 rows (frame order, topology sockets); melder_0's generation 14 commit;
  the T1 signature leaf (hashing of the key digest reuses `CodegenSignature` only if it fits; otherwise sha256
  over a marshal of value rows).
- EXIT_GATE: owner-confirmed file list; edits with CRLF; unit tests (row builders deterministic and value-only,
  key/stamp composition, verdict, envelope round trip, generation gate, transfer drop) and the component test
  green owner-run; a cold conjure emits `.melc` bundles carrying `structural_payloads` for every spell; task in
  review.
- FAILURE_ESCALATION: CONFLICT if melder_0 is mid-edit on `caching_system.py` or the creation system at patch
  time (sequence after them); DECISION_REQUEST if a phase-3/4 row needs a non-value; BLOCKER if the bind-time
  profile requirements are absent for a spell kind in a way that makes the key undefined (a miss is the
  fallback, so only a crash blocks).

## Scope Boundaries
- In scope: payload schema as rows, per-spell key and world stamp, replayability verdict, envelope map and
  generation, conjure-end capture and emit, tests.
- Out of scope: classification/hydrate (next task), parity suites, measurement, the canonical maps (promotion).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's standing go for the lane (2026-09-26T16:47:56Z) while task 2 waits for the owner's
  rerun; reads start now, src edits wait for the Propose->Confirm and melder_0's answer on the shared files.
- from_state: in_progress
- to_state: review
- transition_reason: Seam, envelope generation 15, conjure-end capture and 33 tests landed on the device tree after green
  worktree runs; patch docs aligned (2026-09-26T17:27:47Z). Owner-run suites (C6) and acceptance remain.

## Steps / Checklist
- [x] C1: read `caching_system.py` whole, the creation system's conjure-end staging and cache classification, the
      compiler artifact / resolution frame / topology descriptor / lineage-state surfaces the rows read, and the
      bind-time profile requirements (annotation refs for the key).
- [x] C2: Propose->Confirm (files/symbols, schema as landed rows, tests); wait for the owner's go and melder_0's
      answer.
- [x] C3: implement the snapshot seam (rows, key, stamp, verdict), the envelope map + generation 15, the
      conjure-end capture.
- [x] C4: tests (unit first; one component test); worktree run; apply to the device tree.
- [x] C5: align the patch docs with the landed shape; note the emitted envelope size delta.
- [ ] C6: owner-run suites; "Not run." until then.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The snapshot seam module; envelope generation 15 with `structural_payloads`; conjure-end capture; tests.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/structural_snapshot/ (new)
- src/melder/utilities/caching_system/caching_system.py
- src/melder/aether/spellbook/spellbook_creation_system.py
- tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py (new, 25 tests)
- tests/unit/melder/utilities/test_caching_system.py (+5 tests, +1 rejection row)
- tests/integration/melder/spellbook/test_cache_schema_version_integration.py (history pin 15)
- tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py (new, 3 tests)
- release_docs/next_version_release.md (bullet "Creation caches now record each spell's structural result", generation 15)
- system_docs/patches/active/structural_snapshot_2026_09_26/ (three docs aligned at C5)

## Validation
- Owner-run suites: Not run.
- Worktree (VM, CPython 3.14.7t, copy of src/tests): unit spellbook+utilities 3019 passed, 2 skipped, 7 xfailed;
  component+integration spellbook 1361 passed, 2 skipped, 2 xfailed, 2 xpassed; unit aether+crystallizer,
  component aether+utilities, integration aether+conduit 6919 passed, 43 skipped, 1 xfailed. The two failures in
  tests/unit/melder/build_assets/test_system_documents_builder.py are environmental (the copy has no
  context_compass/, which that builder ingests).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook tests/unit/melder/utilities tests/component/melder/spellbook tests/integration/melder/spellbook`

## Risks / Rollback Notes
- Shared files with melder_0's lane: sequence after their commit; anchored edits refuse on drift.
- Envelope growth per spell (rows are small; measured at C5). Rollback: drop the key and the generation bump
  (a cold reset), delete the module, remove the capture call.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [x] No src edit before the owner confirms the file/symbol list and the shared files are free.
- [x] No row that carries an index ULID, an object or a repr of an object.

## Done Checklist
- [x] Steps complete and checked off (C6 owner-run pending)
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md
  - system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure (the patch folder is shared by the story's tasks).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: structural payload rows; snapshot key and world stamp; envelope generation 15.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T16:47:56Z
  TYPE: PLAN
  CLAIM: Opened while task 2 waits for the owner's rerun. C1 reads first (the code this task changes, whole), then
    the Propose->Confirm. Shared-file gate: QUESTION F0-17 to melder_0 asks whether caching_system.py,
    spellbook_creation_system.py and spellbook.py are free and generation 14 is committed; no edit to those files
    before the answer or an owner ruling.
  EVIDENCE:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:26-70
  - system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md:44-52
  IMPACT: Keeps the lane moving during the owner's validation without touching shared files.
  NEXT: C1 - read caching_system.py whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:51:47Z
  TYPE: FACT
  CLAIM: C1 reads done; one correction to the patch docs' capture step. (1) The phase 1-4 artifacts are RESET
    before conjure end: `run_resolution_phases_for_conduit` calls `cleanup_phase_artifacts_after_resolution`
    (all spells) before returning, and `_activate_conjured_conduit` runs after it - so at conjure end
    `artifact._resolution_frame` and the phase-4 result are None. Capture must read DURABLE state only:
    `Spell.dependencies` (direct ids incl. a recorded self id), the registry topology
    (`SpellSystemStates.get_local_topology_by_id(spell_id).sockets`, eleven value fields), the lineage state
    (`get_by_index_id(spell.spell_index.id)`: `validity`, `flags` -> `contract_unvalidated`), the bind-time
    requirements (`spell.profile.resolution_profile.requirements.parameters`: `annotation`, `di_shape`,
    `collection_element_annotation`, `spellmap_default`) for the key's annotation refs, and the pool. Issue codes
    are not available at conjure end and nothing replays them: dropped from the schema. `ordered_node_ids` is
    derivable (C-C law) and is not stored. (2) Replayability is a POOL property (`CompilerPhase3._eq_safe_object`
    over every pool spell's `spell` and `spellframe`; a custom `__eq__` disables the candidate index for the
    pass) - recomputed at capture, book-wide, no pass state needed. (3) World stamp inputs (phase_04.md world
    reads; D3): sorted `_spell_id_pool` ids, `system_state` posture name, sorted borrowed spell ids over
    `spellbook._contracted_spells` values. (4) Envelope: `_build_empty_cache_data`, `_normalize_loaded_cache_data`
    and `_write_current_cache_to_disk_locked` enumerate the keys; tests write current-version envelopes without
    the new key (unit fixture :92-97, schema-version integration :57-66), so the loader reads
    `structural_payloads` leniently (`.get(..., {})`, entries must be bytes) and the schema-history pin gains
    15. `transfer_spell_payload_to` moves executor bytes; the structural payload of the source is dropped.
    (5) Staging pattern to mirror: `_emit_spell_cache` (per-spell `_caching_enabled` bit, upsert, sets
    `_cache_emit_required`), `_stage_spell_payloads_at_conjure_end` (runs only on non-full-hit executor paths;
    the structural capture must run on EVERY conjure since phases 1-4 ran live, so it sits outside those
    branches, before `_emit_conduit_cache_file_at_conjure_end`). Structural phases run over `spellbook._spells`
    (owned spells) - payloads are per owned spell.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:1-640
  - src/melder/aether/spellbook/spellbook_creation_system.py:207-333
  - src/melder/aether/spellbook/spellbook_creation_system.py:506-614
  - src/melder/aether/spellbook/spellbook_creation_system.py:875-1083
  - src/melder/aether/spellbook/spellbook_creation_system.py:1420-1484
  - src/melder/aether/spellbook/spellbook_creation_system.py:2341-2380
  - src/melder/aether/spellbook/spellbook.py:949-1025
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:12-100
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:160-230
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:252-347
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:349-421
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1320-1362
  - artifacts/ir_phase_survey_20260925/phase_04.md:20-36
  - artifacts/ir_phase_survey_20260925/summary.md:62-101
  - tests/unit/melder/utilities/test_caching_system.py:85-120
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:30-80
  IMPACT: Payload schema (landed shape): {"key": {"spell_id", "annotation_refs"}, "world_stamp", "replayable",
    "phase3": {"dependency_ids", "sockets"}, "phase4": {"validity", "contract_unvalidated"}}; the hydrate task
    will have no artifact writes at all (registry replay + `_add_build_details`), simpler than the code
    description's step 3c-d.
  NEXT: C2 - Propose->Confirm to the owner; wait for melder_0 on the two shared files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:05:32Z
  TYPE: DECISION
  CLAIM: Owner go for the capture task and the rest of the lane ("continue go ahead and finish your work its all
    good", after the C2 Propose->Confirm). Mailbox M0-36 (melder_0, 16:59:52Z) consumed: generation 14 is committed
    (caching_system.py:165 in HEAD), melder_0 has no uncommitted content in caching_system.py or
    spellbook_creation_system.py (device files differ from HEAD by CRLF only - verified here: 0 changed lines
    ignoring CR), both files are mine now; S2b-1 does not touch them and S2b-2 is planned without a generation
    change; they will message before touching either again. Procedure unchanged: worktree first (fresh copy of
    src/tests from the device tree), anchored scripts, then the device tree, then owner-run suites.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:151-168
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: C3 can start on all three files; the shared-file blocker on the board row clears.
  NEXT: C3 - write the seam module, the envelope changes and the conjure-end call in the worktree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:23:47Z
  TYPE: FACT
  CLAIM: C3+C4 landed, worktree-tested, applied to the device tree byte-identically (cmp on all 7 files). Seam:
    `StructuralSnapshot` (slot-only static helper, `PAYLOAD_FORMAT` 1) in the new namespace package
    `spell_compiler/structural_snapshot/` (no `__init__.py`, like its siblings): `type_refs` (address-free rows),
    `annotation_refs` (sorted unique refs by DI shape), `bind_time_requirements` (phase-1 borrow rule),
    `structural_key`, `world_stamp` (sha256 over sorted pool ids + posture name + sorted borrowed ids),
    `pool_replayable` (`CompilerPhase3._eq_safe_object` over every pool spell and spellframe), `build_payload`
    (durable state only: `Spell.dependencies`, registered topology socket rows, lineage validity + the
    `contract_unvalidated` flag), `capture_at_conjure_end` (owned spells in sorted id order, best-effort per spell,
    stale ids dropped, returns whether bytes changed). Envelope: generation 15 `structural_snapshot_rows`;
    `structural_payloads` map read leniently (bytes entries only), written by the emit; new store methods
    `has/get/upsert(->bool)/remove_structural_payload`, `structural_payloads`, `cached_structural_spell_ids`;
    `transfer_spell_payload_to` drops the source's structural payload. Creation system: capture runs on every cache
    path after ownership wiring and executor staging; sets `_cache_emit_required` only when bytes changed, so an
    unchanged world still leaves the bundle file untouched (restage contract kept: file bytes and mtime equal).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:24-105
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:318-461
  - src/melder/utilities/caching_system/caching_system.py:165-184
  - src/melder/aether/spellbook/spellbook_creation_system.py:928-934
  - src/melder/aether/spellbook/spellbook_creation_system.py:1056-1108
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py:99-166
  IMPACT: The hydrate task has its input: one value-only payload per owned spell, keyed and stamped, beside the
    executor payload. Resolved UNKNOWN: `SpellLocalTopology(spell_id, sockets)` takes descriptor objects and
    `SpellSocketDescriptor` is a frozen dataclass, so socket rows rebuild into descriptors directly at hydrate.
  NEXT: C5 - align the patch docs (code description step 8 -> durable-state capture, no artifact writes); MEASURE
    note for the envelope delta; then review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:23:47Z
  TYPE: MEASURE
  CLAIM: Envelope size delta on the component world (Engine + Car, one annotation socket): bundle 2849 B; executor
    tier 1708 B (Car 1367, Engine 341); structural tier 825 B (Car 518, Engine 307). Rows are a few hundred bytes
    per spell and grow with socket count and annotation refs, not with the executor payload; the structural tier
    is bounded by the same id set as the executor tier (stale ids dropped each conjure).
  EVIDENCE:
  - src/melder/tests/component/melder/spellbook/_cache_structural_capture_rows/__conjure_cache__/structural-capture/root.melc (worktree, marshal-decoded)
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py:99-128
  IMPACT: Growth is small in absolute terms; no compaction needed for this generation.
  NEXT: C5 patch-doc alignment.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:27:47Z
  TYPE: FACT
  CLAIM: C5 done: the three patch docs now describe the landed capture (key gains `format`; no stored
    `ordered_node_ids`, `is_broken` or `issue_codes`; world stamp over pool ids + posture name + borrowed spell
    ids; replayability as a pool property; capture from durable state on every cache path with change-gated
    emit), mark the C-C and capture rows LANDED, correct the C-C self-dependency text to the owner's option A
    (recorded, reported by Phase 4 as SELF_DEPENDENCY) and resolve the constructor UNKNOWN
    (`SpellLocalTopology(spell_id, sockets)` takes frozen descriptors). Hydrate deltas stay design-only.
  EVIDENCE:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:46-84
  - system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md:47-60
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md:64-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:930-934
  IMPACT: The hydrate task can be opened against docs that match the bytes on the device tree.
  NEXT: task to review; owner-run command reported; then open the hydrate task.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T16:47:56Z: IN_PROGRESS. C1 reads not started; F0-17 sent to melder_0. Next: read caching_system.py whole, then the
creation system's conjure-end staging and cache classification; then C2.
STATE 2026-09-26T16:51:47Z: IN_PROGRESS. C1 done (FACT note: capture reads durable state only; schema trimmed). Waiting on the
owner's go for C2 and on melder_0 (F0-17) for the two shared files.
STATE 2026-09-26T17:05:32Z: IN_PROGRESS. Owner go received; shared files cleared by melder_0 (M0-36). C3 in the worktree next.
STATE 2026-09-26T17:23:47Z: IN_PROGRESS. C3+C4 done: seam, generation 15, conjure-end capture and 33 new tests on the device tree
(worktree green). Next: C5 patch-doc alignment, then review and the owner-run command.
STATE 2026-09-26T17:27:47Z: REVIEW. C1-C5 done; patch docs aligned. Waiting on the owner-run suites (C6) and acceptance; the hydrate
task is the successor.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
