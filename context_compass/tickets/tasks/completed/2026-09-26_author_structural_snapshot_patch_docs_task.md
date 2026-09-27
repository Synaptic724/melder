# Task: Author the structural-snapshot patch docs (architecture, SpellCompiler component, hydrator control flow)

- Completed: 2026-09-26T16:12:08Z
- Summary: Three patch docs for the 1-4 per-spell structural snapshot (architecture, SpellCompiler component,
  structural hydrator code description) written, linked and consumption-mapped; owner approved 2026-09-26
  ("yeah ok"). The docs stay active under the story until its closure; task 2 (C-C) opened.

## Metadata
- Task ID: TASK-2026-09-26-author-structural-snapshot-patch-docs
- Story: STORY-2026-09-26-structural-snapshot
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T15:03:58Z
- Updated: 2026-09-26T16:12:08Z

## Objective
Write the patch-framework entry-gate artifacts for I-1 under
`system_docs/patches/active/structural_snapshot_2026_09_26/`: `architecture_patch.md` (two-tier key, placement,
capture-on-valid rule, refusal rule, no raw index ULIDs, generation coordination), `component_patch_spell_compiler.md`
(row schemas per phase from the D2 table and the dormant phase 2-5 export; hydrate = registry replay + blueprint
rebuild + one revalidator registration + Spell flags; before/after of the conjure cache path) and
`code_description_patch_structural_hydrator.md` (control flow, edge/error semantics, idempotency, non-goals),
after re-reading the S3b cache path so the docs describe the tree as it is.

## Ticket Contract
- ENTRY_GATE: The four rulings (a)-(d) recorded in the story's Decision Log; the active board row routes here.
- EXECUTION_BOUNDARY: the three patch docs and this ticket; reads of `caching_system.py`,
  `spellbook_creation_system.py` (cache classification, `_stage_spell_payloads_at_conjure_end`, the full-hit
  branch), `SpellSystemStates` write helpers, `compiler_phase_5.py` attach seams and `shared_compiler_executions.py`
  `capture_phase2_5_codegen_ir`. No edit under `src/`.
- DEPENDENCIES: summary.md D1-D6 and the records it cites; melder_0's S3b state of the cache path.
- EXIT_GATE: three patch docs present, linked from the story and this task, artifact-board row added; consumption
  mapping (patch section -> implementation task -> validation) recorded here; owner reviews before task 2 opens.
- FAILURE_ESCALATION: DECISION_REQUEST if a D2 write cannot be expressed as rows; CONFLICT if the cache path is
  under concurrent edit by melder_0 at authoring time (the docs then describe their landed shape).

## Scope Boundaries
- In scope: the three patch docs; the consumption mapping; UNKNOWN resolution by reading the named files.
- Out of scope: any `src/` or test edit; the generation bump itself.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Story opened (2026-09-26T15:03:58Z); waiting on the owner's rulings (a)-(d) before authoring.
- from_state: ready
- to_state: in_progress
- transition_reason: Design shape settled with the owner (story DECISION 2026-09-26T15:37:00Z): 1-4 only, per-spell rows, no
  refusal, normal regeneration for non-replayable spells; authoring starts at A1.
- from_state: in_progress
- to_state: review
- transition_reason: A1-A4 complete (2026-09-26T16:07:21Z): three patch docs present, linked here, on the story and
  the artifact board; consumption mapping recorded; owner review pending.
- from_state: review
- to_state: done
- transition_reason: Owner approved the docs (2026-09-26T16:12:08Z); closure sync run; the C-C task is the successor row.

## Steps / Checklist
- [x] A1: rulings recorded (story DECISION 2026-09-26T15:37:00Z); re-read the S3b cache path (caching_system.py, the creation system's
      classification/staging/full-hit branch) and the phase-5 attach seams; note the deltas since the survey.
- [x] A2: architecture_patch.md (objective/non-goals, changed components, key tiers, placement, invariants,
      migration order, rollback, coverage matrix).
- [x] A3: component_patch_spell_compiler.md (row schemas per phase; before/after of the conjure cache path;
      interface deltas; validation expectations).
- [x] A4: code_description_patch_structural_hydrator.md (control flow in D2 order; edge/error semantics; idempotency;
      explicit non-goals); consumption mapping note; artifact-board row; task -> review.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The three patch docs under `system_docs/patches/active/structural_snapshot_2026_09_26/`.

## Files / Paths Impacted
- system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md
- system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md
- system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md

## Validation
- Not run (documentation task). Read-order and mapping per `patch_artifact_consumption.md` recorded before task 2.

## Risks / Rollback Notes
- The S3b tree may still be moving (melder_0 in progress): the docs cite the landed shape and name the seam
  melder_0 owns; rollback is deleting the folder.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No behaviour claim in a patch doc without a `path:start-end` read behind it.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md
  - system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: structural snapshot patch docs.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T15:03:58Z
  TYPE: PLAN
  CLAIM: Authoring order A1-A4 after the rulings. Inputs: summary.md D1-D6 (row sources per phase, hydrate order,
    key tiers, envelope mechanics, invalidation surface, full-hit reads), candidates.md C-G, and a fresh read of
    the S3b cache path (generation 14 `override_site_plan_lanes` is the current envelope generation; the legacy
    codec is deleted and `_emit_spell_cache` stages manifest creations only, per melder_0's M0-28). The docs
    must name the rows a hydrate replays through `SpellSystemStates` helpers (never raw dict writes), the
    blueprint/index rebuild from rows including the path registry's sequential assignment (D6), and the
    refusal predicate.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/summary.md:46-61
  - artifacts/ir_phase_survey_20260925/summary.md:95-101
  - src/melder/utilities/caching_system/caching_system.py:151-167
  IMPACT: No src edit in this task; the patch gate is satisfied when the three docs exist and are linked.
  NEXT: Wait for rulings (a)-(d); then A1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T15:44:18Z
  TYPE: FACT
  CLAIM: Mailbox M2-3 (melder_2, 15:16:27Z) consumed: a new agent melder_2 (claude, synaptic_python_developer)
    is checked in on stand-by with no lane, no board rows and no production files; the owner assigns its work.
    File ownership for this lane is unchanged (melder_0 holds the cache path / creation system in S3; melder_2
    holds nothing). Owner go for this task received ("go ahead and begin do the right thing").
  EVIDENCE:
  - mailbox_board.md:93-93
  IMPACT: No collision; a stand-by peer exists if the owner wants parallel work on the snapshot tasks later.
  NEXT: A1 - read the S3b cache path (caching_system.py, creation-system cache branch, _emit_spell_cache).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T15:45:55Z
  TYPE: FACT
  CLAIM: A1 part 1, the S3b cache path from source. Envelope (`CachingSystem`): one marshal dict with explicit
    keys `version` (14 = override_site_plan_lanes), `melder_version`, `python`, `frame_name`, `conduit_name`,
    `spell_payloads` {spell_id: nested-marshal bytes}; `_normalize_loaded_cache_data` and
    `_write_current_cache_to_disk_locked` enumerate those keys, so a new top-level `structural_payloads`
    map (spell_id -> bytes, GC-untracked like the executor bytes) is a two-method envelope change plus
    generation 15; `upsert/get/remove_spell_payload`, `transfer_spell_payload_to` (bytes move) and
    `cached_spell_ids` (live keys view) are the store surface. Conjure order today: `_prepare_spellbook_for_conjure`
    runs the STRUCTURAL PHASES FIRST (config freeze -> `run_structural_phases` over every `spellbook._spells`
    entry, chunked units <= workers, then broken-spell check), and only then `_build_conjure_cache_state`
    classifies the 8-11 cache from the live resolvable id set (existing-creation and non-resolvable spells
    excluded) with the caching system created from the resolved conduit name - nothing in the classification
    depends on the structural run, so a structural tier can classify before it. Subset structural runs exist:
    `run_post_conjure_structural_phases(spellbook, spells)` runs `compiler_system.run_structural_phases(spellbook,
    spell)` sequentially per spell; the chunked path builds units from `spellbook._spells` in
    `_build_per_spell_phase_units` (a `spells` parameter makes it a subset run). Staging seam:
    `_activate_conjured_conduit` after ownership wiring -> full hit: `_load_cached_creation_contexts_for_conjure`
    (best-effort per spell; a failed load sets `resolution_required` and bumps `_door_epoch`); mixed/miss:
    `_stage_spell_payloads_at_conjure_end` removes every payload then re-stages every live eligible spell via
    `Spellbook._emit_spell_cache` (manifest-only since S3b) -> `_emit_conduit_cache_file_at_conjure_end`
    (best-effort emit). Structural rows exist for EVERY spell in `_spells` (phases 1-4 run for all), so they
    need the separate map rather than a key inside the executor payload, which only eligible spells carry.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:151-168
  - src/melder/utilities/caching_system/caching_system.py:355-435
  - src/melder/utilities/caching_system/caching_system.py:497-640
  - src/melder/aether/spellbook/spellbook_creation_system.py:207-333
  - src/melder/aether/spellbook/spellbook_creation_system.py:1303-1418
  - src/melder/aether/spellbook/spellbook_creation_system.py:1847-1892
  - src/melder/aether/spellbook/spellbook_creation_system.py:2381-2430
  - src/melder/aether/spellbook/spellbook_creation_system.py:875-1083
  IMPACT: Fixes the architecture patch's placement (top-level `structural_payloads`, generation 15), the conjure
    reorder (structural classification and hydrate before the structural run; subset run for the regenerating
    set) and the capture point (conjure end, beside the executor staging, on every conjure that ran any
    structural phase live).
  NEXT: A1 part 2 - the registry replay surface (`SpellSystemStates` write helpers), phase 3's DAG build and
    `Spell._add_build_details`, the phase-4 strategies' cross-spell reads, and the dormant 2-5 row schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:48:29Z
  TYPE: FACT
  CLAIM: A1 part 2, the replay surface and the phase-4 cross-spell question. (1) Phase 3's durable writes are
    `update_dependencies(spell.spell_index, ids)` (creates the lineage state if missing, diffs direct deps,
    maintains reverse `dependents`, marks the lineage gated + dirty) and `register_local_topology(spell.spell_index,
    SpellLocalTopology(spell_id, sockets))` (stores the LIVE topology object and rebuilds the collection/contract
    reverse indexes) - the topology is rebuilt from value rows (`SpellSocketDescriptor` fields are strings,
    ints, bools, an enum and tuples); plus `artifact._resolution_frame = SpellResolutionFrame(spell_id,
    ordered_node_ids)` and `Spell._add_build_details(dag, dependencies)` (invalidates the creation context).
    (2) Phase 4's registry write is `clear_dirty(ts)` then `set_validity(valid, validation_passed, flags_to_remove=
    [contract_unvalidated])` or `set_validity(gated, contract_unvalidated, flags_to_add=[...])`; broken never
    reaches capture (conjure raises). Phase 6 reads per spell only `_is_broken` and KEY PRESENCE of the
    phase-4 result (a None value passes). (3) The cross-spell question is answered: `Spell.requirements` is a
    read-through onto the artifact's phase-1 rows (reset after every pass), and the binding-resolution-cycle
    strategy SKIPS pool spells whose requirements are None - so if hydrated spells carried no phase-1
    artifacts while another spell ran phase 4 live, the cycle graph would be smaller than cold. Rule adopted:
    on a partial structural hit run phases 1-2 for EVERY spell (borrowed from the bind profile, ~1ms/29) and
    phase 4 for every spell live; replay only phase-3 rows for hit spells. On a full structural hit replay
    phase-3 and phase-4 rows and skip the structural run entirely (no artifacts exist after a pass anyway;
    phase 8's JIT path already re-reflects when phase-1 rows are absent). Phase 1-2 rows are therefore never
    persisted. (4) The key digest at hit time comes from the bind-time profile requirements (level 0); a
    spell without them is a structural miss.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:470-527
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1262-1318
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:56-178
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:208-246
  - src/melder/aether/spellbook/spell.py:1153-1175
  - artifacts/ir_phase_survey_20260925/phase_03.md:38-80
  - artifacts/ir_phase_survey_20260925/phase_06.md:24-34
  - artifacts/ir_phase_survey_20260925/phase_04.md:14-50
  IMPACT: The structural payload is phase-3 rows + phase-4 verdict rows + key + world stamp + replayability; the
    hydrate has exactly three registry calls, one artifact field and one Spell call per spell; parity on partial
    hits comes from running the real phase 4 over the full artifact set.
  NEXT: A2-A4 - write the three patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:07:21Z
  TYPE: FACT
  CLAIM: A2-A4 done: three patch docs under system_docs/patches/active/structural_snapshot_2026_09_26/
    (architecture 158 lines, component 116, code description 80; Status draft). Consumption mapping
    (patch section -> implementation task -> validation), read order architecture -> component -> code
    description per patch_artifact_consumption.md:
    (1) architecture Boundary delta 1 (envelope map, generation 15) + component "After (envelope)" -> capture
    task -> component item 2 (round trip, generation gate, transfer drops the payload).
    (2) architecture delta 2 (payload schema) + component "After (phase 3, C-C)" edge rows -> C-C task (rows)
    then capture task (payload builder) -> component item 1 (deterministic, values only).
    (3) architecture delta 3 (per-spell key, world stamp) -> capture (compute) + hydrate (compare) ->
    architecture item 1 (composition) + migration step 4 two-process key test.
    (4) architecture delta 4 (replayability verdict) -> capture task -> architecture item 1 (verdict unit test).
    (5) architecture delta 5 (three conjure paths) + code description steps 1-2, 5-6 -> hydrate task ->
    component item 3 (full hit runs no structural unit; partial runs 1-2 and 4 for all, 3 for misses).
    (6) architecture delta 6 (capture at conjure end) + code description step 8 -> capture task -> component
    test "cold conjure writes a payload for every spell" (migration step 2).
    (7) code description steps 3-4 (replay of one spell; verdict replay) + component "After (replay surface)"
    -> hydrate task -> component item 3 registry state equal field by field; Invariant 1.
    (8) component "Before/After (phase 3)" + matrix row 1 -> C-C task -> compiler suites + harness
    `local_frame` row (migration step 1).
    (9) architecture Invariant 1 + code description edge semantics (transfer, restore) -> parity task ->
    architecture item 3 (D5 list; restore parity).
    (10) architecture Invariants 6-7 -> hydrate task (phase-4-for-all rule) -> component item 3 partial hit.
    (11) migration step 5 + component ordering constraint 4 -> measurement task -> architecture item 4
    (owner-run harness before/after against the 2026-09-26 baseline; gauntlet parity).
    (12) component ordering constraints 1-2 -> sequencing: C-C first; NOTICE F0-15 to melder_0 sent before
    any edit of caching_system.py, spellbook_creation_system.py or spellbook.py.
    Unknowns carried: profile-requirements presence per spell kind and the row-tuple constructors (capture
    task); `Spell.dependency_graph` readers (C-C task). None blocks the C-C task.
  EVIDENCE:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:1-158
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md:1-116
  - system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md:1-80
  IMPACT: The patch entry gate is satisfied except owner review; task 2 (C-C) opens on approval with a
    Propose->Confirm naming compiler_phase_3.py, spell.py, the presence strategy and eight test files.
  NEXT: Owner reviews the three docs; on approval fable_0 opens the C-C task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T15:03:58Z: READY. Waiting on the owner's rulings (a)-(d); then A1 (re-read the S3b cache path) and
the three patch docs.
STATE 2026-09-26T15:37:00Z: IN_PROGRESS. Shape settled (1-4 per spell; no refusal; normal regeneration). Next: A1 re-read of the S3b
cache path and the phase-4 strategy reads, then A2-A4.
STATE 2026-09-26T15:45:55Z: IN_PROGRESS. A1 part 1 done (cache path, conjure order, staging seam). Next: A1 part 2 (registry
helpers, phase 3 DAG, phase-4 reads, 2-5 row schema), then A2-A4.
STATE 2026-09-26T15:48:29Z: IN_PROGRESS. A1 done. Writing A2 architecture_patch.md, A3 component patch, A4 code description.
STATE 2026-09-26T16:07:21Z: REVIEW. Three patch docs written and linked; consumption mapping recorded;
NOTICE F0-15 sent. Owner reviews the docs; task 2 (C-C) opens on approval with a Propose->Confirm. No src edit.
STATE 2026-09-26T16:12:08Z: DONE. Owner approved; moved to completed/; successor task tickets/tasks/2026-09-26_drop_phase3_dag_object_for_id_rows_task.md.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
