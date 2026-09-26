# Story: Structural snapshot - a creation-cache full hit skips phases 1-7 by hydrating value rows (I-1)

## Metadata
- Story ID: STORY-2026-09-26-structural-snapshot
- Epic: EPIC-2026-08-03-comptime-ir-phase-pipeline
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T15:03:58Z
- Updated: 2026-09-26T15:37:00Z

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
- [ ] Task: TASK-2026-09-26-author-structural-snapshot-patch-docs - architecture, SpellCompiler component and
  hydrator code-description patches after the four rulings and a re-read of the S3b cache path
  tickets/tasks/2026-09-26_author_structural_snapshot_patch_docs_task.md
- [ ] Task: C-C - phase-3 DAG object to id rows; presence strategy repointed (opened after the patch docs)
- [ ] Task: capture on miss - per-spell phase 1-4 rows beside the executor payload; replayability verdicts;
  world stamp; key extension; generation bump
- [ ] Task: hydrate on hit - registry replay through the helpers, Spell flags, structural run only for the
  regenerating set, phase-4 rerun rule; 5-7 and the 8-11 load unchanged
- [ ] Task: invalidation parity - the D5 table as a test list (cold vs hydrated verdicts)
- [ ] Task: restore parity and measurement - fresh index ULIDs, gauntlet parity, warm conjure before/after
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery.

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

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/structural_snapshot_2026_09_26/ (to be authored by the first task)
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

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-26T15:03:58Z: opened on the owner's I-1 selection; task 1 (patch docs) routed and waiting on the four
rulings (a)-(d); no edit under src/. Resume from task 1's latest STATE line.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
