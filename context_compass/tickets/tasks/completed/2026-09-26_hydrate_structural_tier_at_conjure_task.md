# Task: Hydrate the structural tier at conjure (full structural hit replays phase 3-4 rows, skips phases 1-4)

## Metadata
- Task ID: TASK-2026-09-26-hydrate-structural-tier-at-conjure
- Story: STORY-2026-09-26-structural-snapshot
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T17:35:55Z
- Updated: 2026-09-26T18:18:08Z

## Objective
The hydrate half of I-1 (architecture patch delta 5; code description steps 1-4 and 6): before `run_structural_phases`,
classify every owned spell against the structural tier of the conduit bundle (key, world stamp, replayable flag,
well-formed rows). When EVERY owned spell hits, replay phase 3's durable writes (`update_dependencies`,
`register_local_topology` from rebuilt descriptors, `_add_build_details`, Nexus publication) and phase 4's verdict
(`clear_dirty` + `set_validity` with the recorded validity and the `contract_unvalidated` flag) and skip the
structural scheduler run; otherwise run today's phases 1-4 unchanged. v1 scope: the full-hit and miss paths only;
the partial path (replay hits, live phase 3 for misses, phase 4 for all) is a DECISION_REQUEST to the owner
because it saves only the misses' share of phase 3 while still running phases 1, 2 and 4 for every spell.

## Ticket Contract
- ENTRY_GATE: capture task in review (rows exist on disk); the owner's standing go for the lane
  (2026-09-26, "continue go ahead and finish your work its all good"); the active board row routes here; the
  file/symbol list is posted to the owner with the capture report before src edits land on the device tree.
- EXECUTION_BOUNDARY: `structural_snapshot.py` (classify + hydrate; a row-to-descriptor rebuild; well-formedness
  checks), `spellbook_creation_system.py` (`conjure` passes the resolved conduit name into
  `_prepare_spellbook_for_conjure`; that helper classifies and either hydrates or runs the phases; the opt-in
  warning report forces the live run), unit tests for classify/hydrate over stubs, component tests (cold conjure
  -> fresh world -> full hit: no structural phase unit runs, registry state equal field by field, first meld
  behaves as after a cold conjure; a changed spell is a miss and runs cold; `validation_warnings=True` runs cold),
  the patch docs at review. NOT in scope: `spellbook.py` (the existing-conduit route keeps today's structural
  run - it calls the helper without a conduit name), the partial path, parity table, measurement, promotion.
- DEPENDENCIES: capture task rows (`PAYLOAD_FORMAT` 1); `SpellLocalTopology(spell_id, sockets)` +
  `SpellSocketDescriptor` (frozen dataclass); `SpellSystemStates.update_dependencies` /
  `register_local_topology` / `get_by_index_id`; `SpellSystemState.clear_dirty` / `set_validity`.
- EXIT_GATE: edits with CRLF; worktree suites green; owner-run suites green; a fresh process over an unchanged
  world conjures without a structural scheduler run and melds as after a cold conjure; task in review.
- FAILURE_ESCALATION: CONFLICT if melder_0 or melder_2 announce edits to `spellbook_creation_system.py`
  (sequence after them); DECISION_REQUEST on the partial path; BLOCKER if any phase 5-11 reader needs a phase
  1-4 artifact on the hydrated path (none found at discovery, see Notes).

## Scope Boundaries
- In scope: structural classification, full-hit replay (phase 3 durable writes + phase 4 verdict), the
  conjure wiring, tests, patch-doc alignment.
- Out of scope: the partial path (decision), parity suite (next task), measurement, `spellbook.py`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's standing go for the lane (2026-09-26T17:35:55Z); the capture task is in
  review with its rows on disk, so the successor task starts at discovery.
- from_state: in_progress
- to_state: review
- transition_reason: Classify/replay seam, conjure wiring, marshal-format-2 fix and 30 tests landed on the device tree
  after green worktree runs; patch docs aligned (2026-09-26T18:13:08Z). Owner-run suites (H6) and acceptance remain.
- from_state: review
- to_state: done
- transition_reason: Owner ran the suites and accepted ("yeah runs good", 2026-09-26T18:18:08Z); the partial path was not requested, so
  v1 stands (decision recorded); closure sync run; the parity task is the successor.

## Steps / Checklist
- [x] H1: discovery reads - conjure sequence, `run_structural_phases`, phase 3/4 writes, registry helpers, every
  phase 5-11 reader of phase 1-4 artifacts (must be none on the hydrated path).
- [x] H2: seam - `classify(spellbook, caching_system)` (path, hits, misses; well-formedness), `hydrate_full_hit`
  (per-spell replay in one deterministic order), descriptor rebuild from rows.
- [x] H3: creation system - conduit name into `_prepare_spellbook_for_conjure`; structural state; skip or run.
- [x] H4: tests (unit stubs; component full hit / miss / warnings / meld parity); worktree run; device tree.
- [x] H5: align the patch docs (delta 5 landed shape; partial path recorded as a decision).
- [x] H6: owner-run suites; "Not run." until then.
- [x] Run Ticket Microcycle during execution:
  - Note before the next tranche; `SCORE_0_TO_10` >= 7; evidence as `path:start-end`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Classify + hydrate in the seam; the conjure wiring; tests; aligned patch docs; the partial-path decision.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py (+payload_well_formed,
  _socket_row_well_formed, rebuild_topology, classify, hydrate_full_hit)
- src/melder/aether/spellbook/spellbook_creation_system.py (conjure passes the conduit name;
  _prepare_spellbook_for_conjure; +_build_structural_cache_state, +_hydrate_structural_tier_for_conjure)
- src/melder/utilities/caching_system/caching_system.py (+STRUCTURAL_MARSHAL_VERSION = 2 for the structural tier)
- tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py (+25 tests, 50 total)
- tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_hydrate.py (new, 5 tests)
- release_docs/next_version_release.md (capture bullet rewritten for the warm-conjure skip)
- system_docs/patches/active/structural_snapshot_2026_09_26/ (three docs aligned at H5)

## Validation
- Owner-run suites: green (owner, 2026-09-26T18:18:08Z: "yeah runs good"; the recommended command below).
- Worktree (VM, CPython 3.14.7t): unit spellbook+utilities 3044 passed, 2 skipped, 7 xfailed; component+integration
  spellbook 1366 passed, 2 skipped, 2 xfailed, 2 xpassed; unit aether+crystallizer, component aether+utilities,
  integration aether+conduit 6919 passed, 43 skipped, 1 xfailed; crystallizer/mutation_research/top-level unit
  799 passed, 3 xfailed; multithreading 42 passed; live_sim 1 passed, 1 xfailed.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook tests/unit/melder/utilities tests/component/melder/spellbook tests/integration/melder/spellbook`

## Risks / Rollback Notes
- A stale replay because the stamp missed a world input: guarded by the stamp (pool ids, posture, borrowed ids)
  and the per-spell key; the parity task is the detector. Rollback: make `classify` return `miss`
  unconditionally (one line) - the capture stays.
- Shared file with melder_0's lane (`spellbook_creation_system.py`): anchored edits refuse on drift.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No replay of a row set that failed a well-formedness check (a malformed payload is a miss).
- [x] No phase logic in the seam (replay calls the registry helpers phases 3-4 call; no matching, no validation).

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

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: structural classification; phase 3-4 replay; conjure wiring.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T17:35:55Z
  TYPE: FACT
  CLAIM: H1 discovery. (1) `conjure` runs `_prepare_spellbook_for_conjure` (freeze/bind configuration, then
    `run_structural_phases`, then the opt-in warning report) BEFORE the executor classification, which is where
    the caching system is first created (`_get_or_create_caching_system(conduit_name=...)`, memoized). The
    structural classification therefore runs inside the helper after the binds and creates the same memoized
    utility earlier; the existing-conduit route in `spellbook.py:6770` calls the helper without a conduit name
    and keeps today's run. (2) Phase 3's durable writes are `update_dependencies(index, ids)` (set semantics:
    duplicates irrelevant, reverse edges resolve because every spell's state exists from bind
    `register_index`), `register_local_topology(index, SpellLocalTopology(spell_id, descriptors))` (also
    refreshes the collection and contract indexes from the descriptors), `spell._add_build_details(deps)`
    (sets `dependencies`, cleans the creation context) and `_publish_spell_record_to_nexus` when enabled.
    Phase 4's durable writes are `state.clear_dirty(time.time())` then `set_validity(valid,
    validation_passed, flags_to_remove=[contract_unvalidated])` or `set_validity(gated, contract_unvalidated,
    flags_to_add=[contract_unvalidated])`; a broken spell (`invalid`) never reaches conjure end, so only
    `valid`/`gated` rows exist. (3) No phase 5-11 reader needs a phase 1-4 artifact: phase 6 keys
    `phase4_results` by pool id and its missing-phase-4 strategy tests key presence only; the phase2_5 IR
    capture (`shared_compiler_executions.py:236-345`) has no production caller; phases 5, 7-11 do not touch
    `_requirements`/`_symbolic_graph`/`_resolution_frame`; `_requirements_shape_profile_phase1` has no reader
    outside phase 1. (4) The opt-in `validation_warnings` report reads phase-4 results right after the
    structural run, so it forces the live run (documented) rather than replaying diagnostics.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:210-333
  - src/melder/aether/spellbook/spellbook_creation_system.py:509-583
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:936-961
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1042-1057
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:118-178
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:299-352
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1262-1318
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:365-373
  - src/melder/aether/spellbook/spell_compiler/system/validation/missing_phase4_strategy.py:81-89
  - src/melder/aether/spellbook/spell.py:1472-1502
  IMPACT: The full-hit replay is four registry/Spell calls per spell plus the verdict; nothing downstream needs
    the skipped artifacts; the design's step 3c (frame on the artifact) is needed only on the partial path.
  NEXT: H2 - classify/hydrate in the seam (worktree), then H3 wiring, then tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T18:09:45Z
  TYPE: FACT
  CLAIM: Mailbox M0-37 (melder_0, 18:06:53Z, QUESTION) consumed: their S5 stops the Phase-5 per-path socket overlay
    (no SocketRefs on compiled RootResolutionBlueprints; path ids minted by Phase 8 only) and they ask whether this
    lane uses `SharedCompilerExecutions.capture_phase2_5_codegen_ir` or the Phase-5 socket rows. Answer (F0-18): no -
    the snapshot reads phase-3 topology sockets from the registry and the phase-4 lineage verdict; it never calls the
    phase2_5 capture (no production caller, verified at H1) nor `build_phase5_socket_rows`; the owner-gated
    retirement of those helpers and fields is clear from this lane.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:318-420
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:179-185
  IMPACT: No coupling between the structural tier and Phase-5 socket rows; melder_0's S5 can proceed independently.
  NEXT: H2/H3 landed in the worktree; tests green; apply to the device tree.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:10:41Z
  TYPE: FACT
  CLAIM: H2-H4 landed, worktree-tested, applied to the device tree byte-identically (cmp on 8 files). Seam:
    `payload_well_formed` (value-shape check: format, id, stamp/replayable types, dependency ids, 10-field socket
    rows with a SocketKind name and str-tuple id fields, validity in valid/gated), `rebuild_topology` (rows ->
    frozen descriptors -> `SpellLocalTopology`), `classify` (disabled/full_hit/partial/miss with decoded hits),
    `hydrate_full_hit` (sorted id order: `update_dependencies`, `register_local_topology`, `_add_build_details`
    with de-duplicated ids, Nexus publication, `clear_dirty` + `set_validity` mirroring phase 4's two branches;
    KeyError before any write when a payload is missing; RuntimeError on a missing lineage state). Creation
    system: `conjure` resolves the conduit name first and passes it to `_prepare_spellbook_for_conjure`, which
    calls `_build_structural_cache_state` (disabled without a name, with `validation_warnings`, or with caching
    off; else `classify` over the memoized cache utility) and on `full_hit` `_hydrate_structural_tier_for_conjure`
    (documented best-effort: a replay failure is logged and the phases run live); every other path runs
    `run_structural_phases` unchanged. The existing-conduit route (spellbook.py:6770) passes no name and keeps
    today's run - spellbook.py untouched. Found and fixed at H4: the default marshal format flags objects by live
    refcount, so equal payloads from a replay differed byte-wise from the cold capture and re-emitted the bundle
    on every warm conjure (the restage no-rewrite contract broke); the structural tier now encodes with marshal
    format 2 (`CachingSystem.STRUCTURAL_MARSHAL_VERSION`, no back-references) so equal values give equal bytes.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:424-699
  - src/melder/aether/spellbook/spellbook_creation_system.py:226-240
  - src/melder/aether/spellbook/spellbook_creation_system.py:303-443
  - src/melder/utilities/caching_system/caching_system.py:186-189
  - src/melder/utilities/caching_system/caching_system.py:539-556
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_hydrate.py:146-274
  IMPACT: A fresh process over an unchanged world skips phases 1-4; the component test pins registry parity field
    by field (dependencies, direct dependencies, dependents by spell id, validity, flags, socket rows) and the
    first meld; the changed-world, warnings, caching-off and replay-failure paths all run the phases live.
  NEXT: MEASURE note; H5 patch docs; task to review; owner report with the partial-path decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T18:10:41Z
  TYPE: MEASURE
  CLAIM: VM (CPython 3.14.7t, workers=1, 29 gauntlet spells, caching on, executor full hit on the warm worlds),
    scratch script outside the repo, medians: warm conjure 5.09 -> 3.66 ms (-28%, 15 repeats) and 5.57 -> 4.09 ms
    (-27%, 25 repeats) with the structural tier replayed instead of run live; the structural preparation alone
    2.22 -> 0.69 ms and 2.54 -> 0.72 ms (-69..-72%). The remaining ~0.7 ms is classification (29 payload decodes
    + key computation) plus the replay writes. Cold conjure unchanged in kind (it now also captures).
  EVIDENCE:
  - benchmarks/testing_other_di/melder_gauntlet_support.py (ALL_CLASSES; the cycle shape of the breakdown harness)
  - tickets/tasks/2026-09-26_hydrate_structural_tier_at_conjure_task.md (this note; script kept in the VM home)
  IMPACT: The owner-run measurement task can expect roughly a quarter off a warm conjure at 29 spells; the share
    grows with book size because phases 1-4 scale with spells while the replay is a few registry writes per spell.
  NEXT: H5 - align the patch docs; then review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:13:08Z
  TYPE: FACT
  CLAIM: H5 done: the three patch docs mark hydrate v1 LANDED (delta 5 paths (a) and (c), `payload_well_formed`,
    the replay order, the documented fallback, the marshal-format-2 finding, the warning-report and
    existing-conduit exclusions) and carry the partial path (b) as DESIGN ONLY behind a DECISION_REQUEST; the
    release note's capture bullet now describes the warm-conjure skip and the measured quarter. Task to review.
  EVIDENCE:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:76-94
  - system_docs/patches/active/structural_snapshot_2026_09_26/code_description_patch_structural_hydrator.md:13-57
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md:43-52
  - release_docs/next_version_release.md:103-111
  IMPACT: Docs match the bytes; the owner has the partial-path decision in one place.
  NEXT: owner-run suites (H6); the parity task next unless the owner lands the partial path first.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:18:08Z
  TYPE: DECISION
  CLAIM: Owner acceptance ("yeah runs good") after running the recommended suites on the device tree; the partial
    path (b) was offered with a recommendation to leave it out and was not requested, so hydrate v1 (full hit
    replays; anything else runs today's phases) is the landed shape. The patch docs keep (b) as DESIGN ONLY.
  EVIDENCE:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:76-94
  IMPACT: Tasks 3 and 4 close; the lane continues with parity, measurement (owner-run) and promotion.
  NEXT: parity task.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T17:35:55Z: IN_PROGRESS. H1 done (FACT note); H2 seam work starts in the worktree. Partial path is a
decision for the owner; v1 = full hit or today's run.
STATE 2026-09-26T18:10:41Z: IN_PROGRESS. H2-H4 done on the device tree (worktree green; -27% warm conjure at 29
spells). Next: H5 patch docs, review, owner report (partial-path decision).
STATE 2026-09-26T18:13:08Z: REVIEW. H1-H5 done; owner-run suites pending; DECISION_REQUEST open on the partial path.
Successor: the parity task under the story.
STATE 2026-09-26T18:18:08Z: DONE. Owner-run suites green and accepted; v1 stands (partial path not requested); moved to completed/.
Successor: the parity task.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
