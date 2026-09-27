# Story: Structural snapshot - a creation-cache full hit skips phases 1-7 by hydrating value rows (I-1)

## Metadata
- Story ID: STORY-2026-09-26-structural-snapshot
- Epic: EPIC-2026-08-03-comptime-ir-phase-pipeline
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T15:03:58Z
- Updated: 2026-09-26T18:43:15Z

## User Narrative
As the Melder owner, I want a conjure whose creation cache fully hits to skip the structural and resolution
phases (1-7) the way it already skips 8-11, by hydrating the registry rows, the phase-5 blueprint and the
per-conduit validity rows captured from the last valid pass, so that warm conjure and restore stop paying the
1-7 compute on every start while every invalidation event still produces the same verdicts as a cold run.

## Value / MRP Alignment
The epic's implementation entry I-1 (Decision Log 2026-09-26; owner "lets hit up ... i1"). Survey summary.md
(D1-D6) established that phases 1-7 already compute value-shaped results carried by transient objects; a full
hit's hydration reads only the Spell pool and the phase-5 path registry (D6). The snapshot is the epic's
memoization story and the Mojo hydration seam (candidates.md C-G). MRP: correctness first - capture only from
a pass that ended valid and clean, refuse the snapshot for identity-bearing frames, keep index ULIDs out of
rows - measured on the gauntlet before it is trusted.

## Ticket Contract
- ENTRY_GATE: Owner selected I-1 (2026-09-26); patch docs exist under
  `system_docs/patches/active/structural_snapshot_2026_09_26/` and are linked here before any edit under `src/`;
  the four design rulings (custom-`__eq__` frames, envelope vs sidecar, per-spell key extension, CCM dirty-root
  loop) are recorded in the Decision Log; the active board row routes to the current task.
- EXECUTION_BOUNDARY: `spellbook_creation_system.py` (cache classification and the 1-7 skip), the creation cache
  envelope (`utilities/caching_system/caching_system.py`, one generation bump coordinated with melder_0's
  generation 14) or a sidecar per ruling, a new capture/hydrate module beside the compiler phases,
  `SpellSystemStates` registry replay entry points (additive), the phase-5 blueprint/index rebuild seam,
  `SpellCompilerArtifact` attach seams, tests under `tests/unit/melder/spellbook/spell_compiler/` and
  `tests/component/melder/spellbook/`, the patch docs, the canonical maps at closure. NOT in scope: phases 8-11
  emitters and manifests (melder_0's S3 lane), the meld hot path, `Creations`, MutationResearch, the Crystallizer
  restore engine beyond a parity test.
- DEPENDENCIES: artifacts/ir_phase_survey_20260925/summary.md (D1-D6) and the records it cites;
  artifacts/ir_phase_improvement_20260926/candidates.md (C-G); the T1 story (one signature leaf; determinism
  test as the guard for every signature-based skip); melder_0's S3b tree (manifest-only cache path, generation
  14) - re-read `caching_system.py` and the creation system's cache path before the patch docs.
- EXIT_GATE: patch docs promoted; a full hit hydrates rows and skips 1-7 with the existing 8-11 load unchanged;
  the D5 invalidation table passes as a parity test list (cold run vs hydrated run verdicts identical); restore
  parity with fresh index ULIDs; gauntlet parity; warm conjure measured before/after (owner-run); owner accepts.
- FAILURE_ESCALATION: BLOCKER if a phase 1-7 write cannot be replayed from rows (D2 table) without an object
  the rows cannot express; CONFLICT if `caching_system.py` or the creation system is under concurrent edit
  (melder_0) at patch time; DECISION_REQUEST for any ruling not covered by the four below.

## Requirements (Functional)
- Capture: at the end of a conjure whose pass ended valid and clean, emit value rows for phases 1-4 registry
  state (dependencies, reverse edges, topologies, structural validity), the phase-5 blueprint with its path
  registry in sequential order, the system index rows, per-conduit validity rows (phase 6) and the component-of
  map (phase 7); lineages referenced by binding key, never by index ULID (D5).
- Key: per-spell tier = spell id plus the extension ruled below; per-conduit tier = sorted visible resolvable
  ids, sorted owned ids, frame posture, sorted contracted keys (D3); envelope stamps as today (D4).
- Hydrate: on a full hit, replay the registry writes in D2 order (rows -> registry -> blueprint/index attach ->
  component-of -> revalidator -> Spell flags), then the existing 8-11 cache load; phases 1-7 do not run.
- Refusal: a book with an identity-bearing frame (per ruling) or any non-value-expressible hold is not
  snapshot-eligible and runs 1-7 as today; refusal is silent and logged at debug level.

## Requirements (Non-Functional)
- Parity: every row of the D5 invalidation table yields the same validity verdicts after a hydrate as after a
  cold run; restore re-mints ULIDs and the snapshot still hits (restore parity).
- No change to the meld hot path; no new lock on the warm path; capture cost measured on the gauntlet.
- Overlay rules: `Optional`/`Union`, no `getattr`/`hasattr` on owned code, no module constants, rich docstrings,
  pytest unit-first, "Not run." until the owner reports.

## Scope Boundaries
- In scope: capture, key, hydrate, refusal, parity tests, measurement, patch docs, canonical maps.
- Out of scope: phases 8-11 (melder_0), Mojo, MLIR, the schema story's exhaustive 8-11 survey.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner selected I-1 (2026-09-26T15:03:58Z); opened by fable_0 with the patch-doc task routed
  first per `patch_framework_gating.md`; four design rulings requested.

## Dependencies / Related Work
- tickets/stories/completed/2026-09-25_ir_phase_pipeline_survey_story.md (D1-D6)
- tickets/stories/completed/2026-09-26_signature_determinism_and_phase8_digest_story.md (I-0)
- tickets/tasks/2026-09-26_build_site_plan_lowering_task.md (melder_0; generation 14, manifest-only cache path)

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-09-26-author-structural-snapshot-patch-docs - architecture, SpellCompiler component and
  hydrator code-description patches after the four rulings and a re-read of the S3b cache path
  tickets/tasks/completed/2026-09-26_author_structural_snapshot_patch_docs_task.md (done 2026-09-26T16:12:08Z)
- [x] Task: TASK-2026-09-26-drop-phase3-dag-object-for-id-rows (C-C) - phase-3 DAG object to id rows;
  presence strategy repointed. tickets/tasks/completed/2026-09-26_drop_phase3_dag_object_for_id_rows_task.md (done 2026-09-26T16:59:15Z)
- [x] Task: TASK-2026-09-26-capture-structural-payloads-at-conjure-end - per-spell phase 3-4 rows beside the
  executor payload; replayability verdicts; world stamp; key; generation 15.
  tickets/tasks/completed/2026-09-26_capture_structural_payloads_at_conjure_end_task.md (done 2026-09-26T18:18:50Z; opened
  2026-09-26T16:47:56Z, review 17:28:31Z). Original line: capture on miss - per-spell phase 1-4 rows beside the
  executor payload; replayability verdicts; world stamp; key extension; generation bump
- [x] Task: TASK-2026-09-26-hydrate-structural-tier-at-conjure - hydrate on hit: registry replay through the
  helpers, Spell flags, phase-4 verdict replay; v1 full hit or today's run (partial path: owner kept v1).
  tickets/tasks/completed/2026-09-26_hydrate_structural_tier_at_conjure_task.md (done 2026-09-26T18:18:50Z; opened
  2026-09-26T17:36:35Z, review 18:13:08Z). Original line: hydrate on
  hit - registry replay through the helpers, Spell flags, structural run only for the regenerating set, phase-4
  rerun rule; 5-7 and the 8-11 load unchanged
- [x] Task: TASK-2026-09-26-structural-snapshot-parity - invalidation parity (D5 events cold vs hydrated), the
  two-process contract and restore parity (with the frame caching-posture fix).
  tickets/tasks/completed/2026-09-26_structural_snapshot_parity_task.md (done 2026-09-26T18:43:15Z; opened 18:30:35Z, review
  18:31:52Z).
  Original line: invalidation parity - the D5 table as a test list (cold vs hydrated verdicts)
- [ ] Task: measurement (owner-run) - breakdown harness with a caching-enabled cycle, gauntlet parity, warm
  conjure before/after. Restore parity moved into task 5. Original line: restore parity and measurement -
  fresh index ULIDs, gauntlet parity, warm conjure before/after
- [x] Task: TASK-2026-09-26-promote-structural-snapshot-docs - canonical maps + indexes; patch folder retired.
  tickets/tasks/completed/2026-09-26_promote_structural_snapshot_docs_task.md (done 2026-09-26T18:43:15Z; opened 18:36:32Z).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery.

## Acceptance Criteria
- A full cache hit runs no phase 1-7 work and the first meld behaves as after a cold conjure.
- D5 parity and restore parity tests green owner-run; gauntlet parity; measured warm-conjure delta recorded.
- Patch docs promoted into the canonical maps with indexes regenerated; owner accepts.

## Validation / Test Plan
- Unit: row builders per phase (deterministic, ULID-free), key composition, refusal predicate, registry replay.
- Component: cold conjure -> capture -> fresh process hydrate -> identical registry and blueprint rows; the D5
  table; restore parity; two-process signature equality for the snapshot key.
- Owner-run: compiler suites; `benchmarks/testing_other_di/profile_bind_conjure_cycle.py` warm conjure
  before/after; gauntlet parity. "Not run." until reported.

## UX / API / Data Notes
- No public API change intended. The cache envelope gains a structural section (or a sidecar appears).

## Risks / Mitigations
- Registry replay correctness (two validity tiers, reverse indexes, RiskManager bursts) -> D5 parity tests;
  hydrate through the registry's own helpers, never raw dict writes.
- Identity-bearing frames -> refusal per ruling.
- Index ULIDs in rows -> binding-key references only; restore parity test.
- Moving-module types keeping a rendered name -> per-spell key extension per ruling.
- Concurrent edits on the cache seam (melder_0) -> NOTICE before patching; sequence after S3b lands.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No implementation before the patch docs exist and are linked.
- [ ] No row schema that carries an index ULID or a live object.

## Open Questions
- The four rulings below (Decision Log records the answers).

## Decision Log
- 2026-09-26 (owner): I-1 selected as the next lane ("lets hit up the next thing ... i1").
- 2026-09-26 (fable_0, DECISION_REQUEST): (a) custom-`__eq__` frames; (b) envelope section vs sidecar;
  (c) per-spell key extension with the phase-1 annotation type refs; (d) CCM dirty-root loop as public API.
- 2026-09-26 (owner): snapshot = phases 1-4 only, per spell, beside the executor payload; 5-7 live. No refusal:
  non-replayable spells regenerate 3-4 through the normal phases (per-spell miss); (c) accepted; (d) moot.
- 2026-09-26 (owner): patch docs approved ("yeah ok finish off what you gotta do"); the lane proceeds task by task
  (C-C first); the release note is updated when code lands; tickets are turned in on owner-run green suites.
- 2026-09-26 (owner): C-C accepted and turned in (suites green; "it seems faster"); a self-referencing constructor
  now records its self-dependency for Phase 4 (owner option A, melder_1's lane). Capture task open, go pending.
- 2026-09-26 (owner): capture task and the rest of the lane approved ("continue go ahead and finish your work its all
  good"); capture landed the same day (task 3 in review, owner-run pending).
- 2026-09-26 (fable_0, DECISION_REQUEST): partial structural path (b) - land it (subset/phase-selective structural run)
  or keep v1 (full hit replays; anything else runs today's phases). Pending the owner.
- 2026-09-26 (owner): tasks 3-4 accepted ("yeah runs good"); partial path not requested - v1 stands.
- 2026-09-26 (owner): tasks 5-6 accepted ("running good ... it's faster for sure"); frame caching-posture fix kept;
  patch folder retired; story to review pending the owner-run measurement decision.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/structural_snapshot_2026_09_26/ (architecture, SpellCompiler component,
    structural hydrator code description; in review 2026-09-26T16:07:21Z)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: durable deltas merged into the canonical maps at closure; patch folder archived.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: structural snapshot; registry replay; snapshot key; cache envelope.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T15:03:58Z
  TYPE: DECISION_REQUEST
  CLAIM: Four rulings the survey named as prerequisites, with recommendations. (a) Frames with a custom
    `__eq__`: phase 3 matches objects by identity with an `==` fallback on frames, which a canonical
    (module, qualname) ref cannot reproduce for a custom `__eq__` - recommend REFUSE: such books are not
    snapshot-eligible and run 1-7 as today (conservative, no false hits). (b) Placement: recommend a structural
    SECTION inside the `.melc` envelope with one generation bump (14 -> 15, coordinated with melder_0), reusing
    the four exact stamps and the atomic write, over a sidecar that would duplicate admission and write logic.
    (c) Per-spell key: the spell id already hashes the spell's own module, but a referenced annotation type that
    moves module while keeping its rendered name leaves the consumer's id unchanged - recommend extending the
    per-spell tier with the sorted (module, qualname) refs of the phase-1 annotation types (value-expressible
    per D1; no source-file hashing). (d) The CCM dirty-root loop: the meld gate is armed only by
    `notify_spell_changed`, which no shipped path calls - recommend "public DevOps API, documented as
    armed-only-by-notify"; the snapshot restores the component-of map and re-registers the revalidator, and a
    capture-eligible pass has no dirty roots, so nothing else is hydrated.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/summary.md:25-45
  - artifacts/ir_phase_survey_20260925/summary.md:62-101
  - artifacts/ir_phase_survey_20260925/summary.md:130-142
  - artifacts/ir_phase_improvement_20260926/candidates.md:146-165
  - src/melder/aether/spellbook/bind/bind.py:942-953
  - src/melder/utilities/caching_system/caching_system.py:151-167
  IMPACT: The patch docs (task 1) are written against the rulings; nothing under `src/` moves before them.
  NEXT: Owner rules (a)-(d); fable_0 re-reads the S3b cache path and writes the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:12:12Z
  TYPE: TRADEOFF
  CLAIM: Owner proposes cutting the snapshot at phase 4: cache 1-4 (per spell; also what a post-conjure bind
    re-runs) and leave 5-7 live (per conduit; re-run at meld-time gates; "really fast"). Evidence for the take:
    profiled at 29 spells, 1-4 = 11.0ms (phase 1 0.50 borrowed from the bind profile, phase 2 0.46, phase 3
    5.07, phase 4 4.06) against 5-7 = 8.3ms (phase 5 5.0, phase 6 3.16, phase 7 < 0.15); unprofiled June: 5-7
    serial floor ~2.1ms of a 6.1ms warm conjure, 1-4 "tiny". So 5-7 are not negligible under the profiler
    (phase 5 is the largest single unit) but the three hardest hazards - index ULIDs in phase-5/6 rows, the
    path registry's sequential ints embedded in phase-11 manifests, the CCM revalidator/component-of restore
    plus phase 6's 23 strategies to audit - all live in 5-7, and 5-7 read only registry state (D1/D6), so they
    run unchanged on hydrated 1-4 rows. Within 1-4 the world-independent rows (1-2) cost ~1ms; the cost is
    phase 3 (pool candidate query, DAG) and phase 4 (13 strategies with cross-spell and graph-wide reads), both
    world-dependent, so per-spell 3-4 rows need a world stamp (conduit tier digest; phase-3 rows can later
    narrow to the candidate ids per frame key). Running dynamic worlds already re-run 1-4 for NEW spells only
    (registry rows persist; dependents gated by the watcher), so the payoff is the fresh process: full hit
    skips 1-4; partial hit hydrates 1-2 (and 3 where the stamp matches) and re-runs 4. Ruling (d) becomes
    moot for a 1-4 snapshot; (a), (b) [per-spell structural bytes beside the executor bytes] and (c) stand.
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/cost_model.md:19-31
  - artifacts/ir_phase_improvement_20260926/cost_model.md:47-60
  - artifacts/ir_phase_survey_20260925/summary.md:25-45
  - artifacts/ir_phase_survey_20260925/summary.md:95-101
  IMPACT: Recommend v1 = I-1a (per-spell 1-4 rows in the envelope, full and partial hits; 5-7 live) and a
    follow-up I-1b (phase-5 blueprint + path-registry rows) only if the unprofiled 5-7 share measured by the
    breakdown harness at workers=1 justifies it.
  NEXT: Owner confirms the 1-4 cut and rulings (a)-(c); optionally runs the breakdown harness at workers=1 for the
    unprofiled per-phase split before the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:18:13Z
  TYPE: MEASURE
  CLAIM: Owner-run breakdown harness (3.14t, gil=disabled, 29 spells, workers=1, repeats=7, caching disabled;
    medians): requirements_symbolic wall 1.307ms / busy 0.358ms; local_frame 1.528 / 1.351; validation 1.050 /
    0.864; root_blueprints 1.487; system_validation 0.712; change_control 0.074; plan_group 10.543 / 9.822.
    Derived: phases 1-4 wall 3.885ms (busy 2.573ms; ~1.3ms of the wall is scheduler barrier/handoff, most of
    it on the first structural phase), phases 5-7 wall 2.273ms, 1-7 wall 6.158ms, 8-11 10.543ms. The
    unprofiled split therefore matches the profiled ordering (1-4 > 5-7, ratio ~1.7 by wall) and resolves the
    cost model's UNKNOWN; the June "1-4 tiny" note was about busy time at a coarser harness. A 1-4 snapshot
    that also skips the structural scheduler run saves up to ~3.5ms per warm conjure at 29 spells (~55% of
    the 1-7 wall); C-C alone bounds at ~0.9ms (a share of local_frame busy 1.351ms).
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/cost_model.md:47-60
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:1-40
  IMPACT: The 1-4 cut is the lever on the warm path; C-C is a component of it (the phase-3 DAG object has one
    reader and must become rows for the hydrate anyway), not a substitute. Verdict to the owner: worth it as
    I-1a, with C-C as the first implementation task after the patch docs.
  NEXT: Owner confirms the 1-4 snapshot and rulings (a)-(c); patch docs follow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:37:00Z
  TYPE: DECISION
  CLAIM: Owner and fable_0 settled the design shape (2026-09-26): (1) the snapshot covers phases 1-4 only,
    per spell, stored beside each spell's executor payload in the .melc envelope (one generation bump,
    coordinated with melder_0's 14); phases 5-7 stay live and run unchanged on the hydrated registry rows.
    (2) No book-level refusal: each spell's phase 3-4 rows carry a replayability verdict (false when a
    parameter's matching involved a spellframe whose type overrides `__eq__`, or when a row cannot be
    expressed as values); a non-replayable spell hydrates its 1-2 rows and REGENERATES 3-4 through the
    normal phase code, exactly as a spell missing from the cache does on a partial hit - the snapshot never
    reimplements a phase. Phase 4 re-runs for every spell whenever any spell's phase 3 ran live (graph-wide
    strategies). (3) The 3-4 rows carry a world stamp (visible ids, owned ids, posture, contracted keys); a
    stamp mismatch regenerates 3-4 for all spells normally, 1-2 hydrate. (4) The per-spell key adds the
    sorted (module, qualname) refs of the phase-1 annotation types. (5) Hydrate order: rows -> registry
    helpers -> Spell flags; then the normal structural run for the regenerating set, then 5-7 live, then
    the existing 8-11 cache load. (6) C-C (phase-3 DAG object -> id rows, presence strategy repointed) is
    the first implementation task after the patch docs. Ruling (d) is moot for a 1-4 snapshot; the doc
    wording fix for the CCM loop is a separate authorized correction.
    To verify while writing the docs: which phase-4 strategies read other spells' phase-1 rows and whether
    those rows come from the bind-time profile (present in every process) or from the reset artifact.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/summary.md:25-61
  - artifacts/ir_phase_improvement_20260926/cost_model.md:19-31
  - artifacts/ir_phase_improvement_20260926/candidates.md:72-98
  IMPACT: Task 1 (patch docs) is unblocked; task list re-sequenced (C-C first). Rulings (a)-(d) closed.
  NEXT: fable_0 writes the three patch docs against this shape (task 1 A1-A4).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:07:21Z
  TYPE: FACT
  CLAIM: Gate transition: task 1 (patch docs) is in REVIEW. The three entry-gate artifacts exist and are
    linked from the task, this story and the artifact board; the consumption mapping (12 rows: patch
    section -> task -> validation) is in the task notes. Remaining gate item: owner review. Sequencing
    recorded in the docs: C-C first (phase 3 rows-only, no envelope touch), then capture (envelope key,
    generation 15 after melder_0's 14), hydrate, parity, measurement, promotion. NOTICE F0-15 told
    melder_0 the planned cache-path changes; a second NOTICE precedes any edit of their files.
  EVIDENCE:
  - tickets/tasks/2026-09-26_author_structural_snapshot_patch_docs_task.md
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:1-158
  IMPACT: Task 2 (C-C) can open on owner approval; nothing under src/ moves before it.
  NEXT: Owner reviews the docs; fable_0 opens the C-C task with a Propose->Confirm.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:59:33Z
  TYPE: FACT
  CLAIM: Mailbox M1-16 (melder_1, 16:58:52Z) consumed: their half of the self-referencing-constructor change is
    applied on top of C-C in the tree (self_validation_strategy.py names the parameter from the Phase-3 topology;
    spellbook_validation_error.py hides CIRCULAR_DEPENDENCY behind SELF_DEPENDENCY; unit tests; a new integration
    file tests/integration/melder/spellbook/test_spellbook_integration_self_dependency.py exercising the Phase-3
    self-resolution end to end). compiler_phase_3.py, its test and descriptor untouched by them.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_report_self_referencing_constructor_as_validation_error_task.md
  IMPACT: The C-C self branch has an end-to-end integration test from melder_1's lane; nothing for this story to do.
  NEXT: Capture task awaits the owner's go and melder_0's answer (F0-17).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T17:28:31Z
  TYPE: FACT
  CLAIM: Task 3 (capture) landed on the device tree and is in review: `StructuralSnapshot` seam
    (`spell_compiler/structural_snapshot/`), envelope generation 15 with `structural_payloads`, conjure-end
    capture from durable state on every cache path with a change-gated emit, 33 new tests; worktree suites green
    (unit spellbook+utilities 3019, component+integration spellbook 1361, wider aether/conduit/crystallizer 6919
    passed). Patch docs aligned to the landed shape. Owner-run suites pending (C6).
  EVIDENCE:
  - tickets/tasks/2026-09-26_capture_structural_payloads_at_conjure_end_task.md (Validation; notes 2026-09-26T17:28:31Z)
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:24-105
  - src/melder/utilities/caching_system/caching_system.py:165-184
  IMPACT: The hydrate task (task 4) has its input and its docs; the lane order (capture -> hydrate -> parity ->
    measurement -> promotion) holds.
  NEXT: owner-run suites for task 3; open the hydrate task on the owner's standing go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:13:08Z
  TYPE: FACT
  CLAIM: Task 4 (hydrate) landed on the device tree and is in review: classify + full-hit replay in the seam,
    conjure wiring in the creation system (`_prepare_spellbook_for_conjure` takes the conduit name), structural
    payloads encoded value-only (marshal format 2), 30 new tests; worktree suites green across unit/component/
    integration trees; VM medians at 29 spells: warm conjure -27%, structural preparation -70%. Patch docs and
    the release note aligned. DECISION_REQUEST to the owner: land the partial path (b) or keep v1.
  EVIDENCE:
  - tickets/tasks/2026-09-26_hydrate_structural_tier_at_conjure_task.md (Validation; notes 18:10:41Z)
  - src/melder/aether/spellbook/spellbook_creation_system.py:303-443
  IMPACT: The structural snapshot is end to end (capture + replay). Remaining lane work: parity task (D5 table,
    restore parity, two-process key test), measurement (owner-run), promotion into the canonical maps.
  NEXT: owner-run suites for tasks 3-4; the parity task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:18:50Z
  TYPE: DECISION
  CLAIM: Owner ran the suites and accepted tasks 3 (capture) and 4 (hydrate v1) ("yeah runs good"); the partial path
    was offered with a recommendation to leave it out and was not requested - v1 stands. Both tickets closed and
    moved to completed/; board anchors updated; the parity task is the successor.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_capture_structural_payloads_at_conjure_end_task.md
  - tickets/tasks/completed/2026-09-26_hydrate_structural_tier_at_conjure_task.md
  IMPACT: The structural snapshot ships end to end in 0.2.59 (generation 15); remaining lane work is parity,
    owner-run measurement and promotion into the canonical maps.
  NEXT: open the parity task (D5 events after a hydrated conjure vs a cold one; restore parity; two-process key).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:31:52Z
  TYPE: FACT
  CLAIM: Task 5 (parity) landed and in review: 7 component contracts (D5 events cold vs hydrated, gated contract
    verdict, two-process rows, crystallizer restore) plus a source-evidenced fix outside the lane's file list -
    `AethericFrame.bind_frame_configuration` now copies the caching posture (it dropped the recorded cache flag
    and root, so restored worlds never found their conjure cache). A notch runtime defect (first meld of a
    dependent after a provider notch) was found and reported, not fixed (other lane). Worktree green.
  EVIDENCE:
  - tickets/tasks/2026-09-26_structural_snapshot_parity_task.md (notes 2026-09-26T18:31:52Z)
  IMPACT: Lane status: capture, hydrate, parity landed; measurement (owner-run) and promotion remain.
  NEXT: owner-run suites for task 5; then promotion into src_components.md / src_architecture.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:43:15Z
  TYPE: DECISION
  CLAIM: Owner ran the recommended suites for tasks 5-6 and accepted ("running good ... it's faster for sure").
    Parity and promotion closed; the patch folder retired to system_docs/patches/completed/; the frame
    caching-posture fix stays. Every implementation task of the story is done; the only open line is the
    owner-run measurement pass, which needs no agent work unless the owner asks for the benchmarks/ edit.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_structural_snapshot_parity_task.md
  - tickets/tasks/completed/2026-09-26_promote_structural_snapshot_docs_task.md
  - system_docs/patches/completed/structural_snapshot_2026_09_26/architecture_patch.md
  IMPACT: I-1 ships in 0.2.59: cache generation 15, warm conjure skips phases 1-4 on an unchanged book.
  NEXT: story to review; owner decides on the measurement pass and story closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user (per-task reports 2026-09-26)
- [x] Acceptance criteria confirmed by user (tasks 1-6 accepted on owner-run suites)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-26T15:03:58Z: opened on the owner's I-1 selection; task 1 (patch docs) routed and waiting on the four
rulings (a)-(d); no edit under src/. Resume from task 1's latest STATE line.
STATE 2026-09-26T16:07:21Z: task 1 in REVIEW (three patch docs, consumption mapping); design settled; task 2 (C-C) opens
on owner approval. No src edit yet. Resume from task 1's latest STATE line.
STATE 2026-09-26T16:12:08Z: task 1 DONE (owner approved); task 2 (C-C) opened and routed. Resume from task 2's latest STATE line.
STATE 2026-09-26T16:40:10Z: task 2 (C-C) in REVIEW - landed on the device tree, worktree suites green; owner-run B6 pending.
STATE 2026-09-26T16:59:15Z: task 2 (C-C) DONE and turned in; task 3 (capture) in discovery with its Propose->Confirm posted;
waiting on the owner's go and on melder_0 (F0-17) for the two shared cache-path files.
STATE 2026-09-26T17:28:31Z: task 3 (capture) in REVIEW - landed on the device tree, worktree suites green, patch docs
aligned; owner-run suites pending. Next: the hydrate task (task 4).
STATE 2026-09-26T18:13:08Z: task 4 (hydrate v1) in REVIEW - landed, worktree green, -27% warm conjure at 29 spells;
partial path is an open owner decision. Tasks 3-4 await owner-run suites. Next: the parity task.
STATE 2026-09-26T18:18:50Z: tasks 3-4 DONE (owner-run suites green, accepted; v1 stands). Next: the parity task (task 5)
opens under the story on the owner's standing go.
STATE 2026-09-26T18:31:52Z: task 5 (parity) in REVIEW - landed with the frame caching-posture fix; owner-run suites
pending. Next: measurement (owner-run) and promotion.
STATE 2026-09-26T18:36:32Z: task 6 (promotion) in REVIEW - both canonical maps carry the landed shape, indexes
regenerated, system-document tests green on the device tree. Open: owner acceptance of tasks 5-6; measurement is
owner-run.
STATE 2026-09-26T18:43:15Z: REVIEW. Tasks 1-6 DONE and accepted; patch folder retired. Only the owner-run measurement
line is open; the story closes on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
