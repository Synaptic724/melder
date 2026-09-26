# Task: Hoist the phase-8 pool digest into the pass cache and test the analysis slot first

## Metadata
- Task ID: TASK-2026-09-26-hoist-phase8-pool-digest
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T10:42:09Z

## Objective
In `SpellOccurrenceGraphAnalyzerStrategy.analyze`: test `artifact._occurrence_graph_analysis is None`
before any key work; hash the pass-invariant rows (spell rows, topology rows, contracted rows, system
state) once per pass into `analysis_pass_cache["phase8_pool_digest"]`; build the root rows once and
combine them with the digest for both the fast key and the input signature, so per-root work is
proportional to the root's own blueprint (C-A).

## Ticket Contract
- ENTRY_GATE: Task 2 in review (single serializer) or the owner confirms C-A may land first; patch docs
  linked; the owner confirmed the Propose -> Confirm message; active board row routes here.
- EXECUTION_BOUNDARY: `spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
  (`analyze`, `_build_occurrence_graph_fast_key`, `_build_occurrence_graph_input_signature`, one new
  helper `_get_pool_digest`) and its tests. No other file.
- DEPENDENCIES: task 1 patch docs; the pass-cache lifetime contract (dies with the pass units); the
  key semantics: `id(path_registry)` stays a per-root process-local part.
- EXIT_GATE: the pool-wide rows are hashed once per pass; root rows built once per root; the None
  check precedes key work; unit tests for digest reuse, None-first skip and key equality across roots;
  breakdown harness before/after recorded (owner-run); status review.
- FAILURE_ESCALATION: CONFLICT if updater_1 or melder_0 edit the strategy file concurrently; RISK if
  the JIT path shows a memo hit that the new key shape would miss (none expected: hash of hash).

## Scope Boundaries
- In scope: the key/signature path of the strategy and its tests.
- Out of scope: the occurrence graph build, contract-defaults reading (C-K), phases 9-11, emitters.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Created with the story; opens after task 2 (or on owner direction) and the
  confirmed proposal.
- from_state: ready
- to_state: in_progress
- transition_reason: Task 2 in review; owner confirmed H1 ("do the recommended send it", 2026-09-26).
- from_state: in_progress
- to_state: review
- transition_reason: H1-H4 complete on the task boundary (one strategy file, one test file); nothing
  executed here ("Not run."); breakdown harness before/after is owner-run.

## Steps / Checklist
- [x] H1: Propose -> Confirm (file, symbols, the digest cache key, the None-first rule) and owner
      confirmation.
- [x] H2: implement `_get_pool_digest` (pass-cache memo, benign last-writer-wins like the two existing
      slots), single `_build_root_blueprint_rows` call, key = (root rows..., pool digest), signature =
      hash(root rows..., pool digest); None-first skip of the compare.
- [x] H3: tests - digest built once per pass over N roots; analysis None -> no compare, keys still
      stored; identical key/signature for the same root across two passes with equal inputs; different
      digest when a topology row changes.
- [x] H4: docstring ritual; notes; task -> review with "Not run." and the harness command.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The strategy change; tests; before/after breakdown harness rows (owner-run) recorded here.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py
- tests (unit tests for the strategy's key path)

## Validation
- Not run. (VM interpreter is 3.10 against a 3.14 floor.)
- Recommended commands (owner-run, 3.14t):
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook`
  - `BENCH_BREAKDOWN_WORKERS=1,5 BENCH_BREAKDOWN_REPEATS=7 python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`
    (before = commit 6fc9af345 bytes, after = this working tree; record plan_group busy/wall and the
    per-spell plan_group rows per measurement_plan.md M5/M6)

## Risks / Rollback Notes
- Rollback: restore the two key builders (pure functions) and drop the helper.
- Phase 8 is inside updater_1's review-stage proposals: the change is confined to ~40 lines of the key
  path and rebases trivially; NOTICE sent at story open.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [x] No edit under `src/` before the owner confirms the file/symbol proposal.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked (harness rows pending, owner-run)
- [x] Documentation updated (if needed) - patch docs already carry the key path; promotion at closure
- [x] Validation status recorded ("Not run.")
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/
  - artifacts/codegen_signature_determinism_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: phase-8 key path; pass cache; pool digest.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T09:05:00Z
  TYPE: PLAN
  CLAIM: The digest is a hash of the same rows the key carried, so the signature remains a function of
    the same inputs; the None-first check only removes a compare that cannot succeed on the conjure
    path. Root rows are built once and shared by key and signature.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:118-372
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:182-216
  IMPACT: Removes the cold path's O(spells^2) step without changing what invalidates the analysis.
  NEXT: Wait for the confirmed proposal (H1).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T09:50:00Z
  TYPE: FACT
  CLAIM: Mailbox M1-10 (melder_1) consumed: an owner-approved commit landed in the strategy file this
    task targets. `_iter_spell_contract_defaults` now calls `inspect.signature(spell.spell,
    annotation_format=Format.FORWARDREF)` with `Format` imported from `annotationlib` (line 2); the
    file is 1193 lines, and every range below `import` shifted by +1 (`analyze` :119, fast key :268,
    input signature :304, root rows :347, defaults :995-1032). `analyze` and the two key builders are
    untouched; melder_1 makes no further edits there. H2 rebases on the current device bytes.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:2-2
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1022-1022
  - tickets/tasks/2026-09-26_fix_inspect_signature_nameerror_on_type_checking_annotations_task.md
  IMPACT: No conflict with H2 (disjoint hunks); the PLAN note's :118-372 range now reads :119-373.
  NEXT: H1 after task 2 reaches review: restate file/symbols against the current bytes and proceed on the
    owner's blanket approval unless redirected.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T10:06:13Z
  TYPE: PLAN
  CLAIM: H1 proposal, read against the current bytes (1193 lines). Today `analyze` :119-266 builds
    the fast key :268-301 and the input signature :303-345 separately, each calling
    `_build_root_blueprint_rows` :347-373 (twice per root) and each carrying the pool-wide
    `spell_rows`/`topology_rows`/`contracted_rows`/`system_state` (memoized per pass at :477-508 and
    :375-475), so the signature hashes pool-sized rows once per root (O(spells^2) per pass); the skip
    compare :206-212 tests the analysis slot LAST. H2 change, confined to this file: (1) new
    `_get_pool_digest(*, spell_rows, graph_shape, analysis_pass_cache) -> Optional[str]` = one
    `hash_codegen_signature(spell_rows, topology_rows, system_state, contracted_rows)` per pass,
    memoized in `analysis_pass_cache["phase8_pool_digest"]` (benign last-writer-wins like the two
    existing slots; per root when no cache is supplied); (2) `analyze` builds `root_rows` ONCE and
    passes `root_blueprint`, `root_rows`, `pool_digest` (keyword-only) to both builders; (3) fast key
    = `(root_spell_id, ordered_node_ids, id(path_registry), blueprint_socket_rows, pool_digest)` and
    input signature = `hash_codegen_signature(...same five parts...)`; (4) the skip reads
    `artifact._occurrence_graph_analysis` first and compares key/signature only when it is not None.
    Both key and signature are artifact-local (reset at `shared_compiler_executions.py:1469-1470` and
    `spell_compiler_artifact.py:319-320`, never persisted), so the byte change carries no cache
    generation consequence. H3: update the pinned key shape in
    `test_spell_occurrence_analyzer_strategy.py:156-235` (five parts, digest last), keep the reuse
    test's `lambda self, **kwargs` monkeypatches valid (builders stay keyword-only), add digest-once-
    per-pass, None-first and topology-change tests.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:119-266
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:268-373
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:375-508
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1465-1472
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:316-321
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:156-273
  IMPACT: Per-root key work becomes proportional to the root's blueprint plus one 64-char digest;
    the pool rows are hashed once per pass.
  NEXT: Owner confirms H1 (file, four symbols, key shape, cache slot); then H2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:16:28Z
  TYPE: FACT
  CLAIM: H2 and H3 landed on the working tree (not run). Strategy file now 1261 lines: `analyze`
    :119-290 builds `pool_digest` then `root_rows` once (:190-206) and reads the analysis slot first
    in the skip check (:216-223); `_build_occurrence_graph_fast_key` :292-323 returns the five-part
    key `(root_spell_id, ordered_node_ids, id(path_registry), blueprint_socket_rows, pool_digest)`;
    `_build_occurrence_graph_input_signature` :325-361 hashes the same five parts; new
    `_get_pool_digest` :363-409 hashes `(spell_rows, topology_rows, system_state, contracted_rows)`
    once per pass into `analysis_pass_cache["phase8_pool_digest"]` (None inputs never touch the
    memo); `_build_root_blueprint_rows` :411-439 and `_build_graph_shape_rows` :441-459 docstrings
    updated. `git diff -w --stat`: 107 insertions, 39 deletions, one file. Tests
    (`test_spell_occurrence_analyzer_strategy.py`, 452 lines): shared keyed fixture :159-227; the
    pinned key re-pinned to the five-part shape with the digest's inputs made explicit :229-273;
    new: digest memoized once per pass :276-302, digest tracks a topology change :305-341, None
    inputs yield no digest/key/signature and leave the memo empty :344-362, rebuild when no analysis
    is retained despite matching key/signature :365-413; the existing reuse test :416-452 keeps its
    `lambda self, **kwargs` patches unchanged.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:119-290
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:292-459
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:159-452
  IMPACT: Per pass the pool-wide rows are hashed once instead of N times; each root pickles only its
    own blueprint rows plus one 64-character digest. No persisted format changes (key and signature
    are artifact-local).
  NEXT: H4: task -> review with "Not run." and the harness command; then open task 4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:42:09Z
  TYPE: MEASURE
  CLAIM: Owner-run, 3.14.7t, GIL disabled, task-3 bytes in place (AFTER). Breakdown harness (29 classes,
    repeats 7): workers=1 plan_group wall 19.424ms / busy 26.398ms; workers=5 wall 8.588ms / busy
    18.895ms, par_eff 0.44. Scaling probe (forest, workers 1, repeats 5): N=27 median 10.276ms
    (380.6us/spell), N=99 32.132ms (324.6us), N=300 108.808ms (362.7us) - per-spell cost flat across
    N, i.e. the cold path is linear with the digest in place. The BEFORE runs are INVALID: `git stash
    push` failed with "could not write index" (a stale 0-byte `.git/index.lock` from 09:45Z, left by a
    `git status` issued from this VM, whose mount forbids unlink), so both harness runs measured the
    same bytes: 12.128ms vs 19.424ms at workers=1 for identical code is the noise band of that harness
    on this machine (~60%). The probe's two identical-code runs agree within 4% (9.865 vs 10.276ms;
    32.147 vs 32.132ms; 108.143 vs 108.808ms), so the probe is the usable instrument.
  EVIDENCE:
  - artifacts/codegen_signature_determinism_20260926/measurement_plan.md:51-63
  - artifacts/codegen_signature_determinism_20260926/scaling_conjure_probe.py:1-197
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:256-285
  IMPACT: No before/after delta can be claimed yet (M5/M6/M7 all lack a BEFORE). The pre-task-3 file is
    staged for the owner at `build/_fable_stage/spell_occurrence_graph_analyzer_strategy.BEFORE.py`
    (`git show HEAD:` bytes; git-ignored) so the BEFORE runs need no git index write. Lesson recorded:
    never run index-writing git commands (`status`, `stash`, `checkout`) from this VM; use
    `git --no-optional-locks` reads only.
  NEXT: Owner deletes the stale lock, runs BEFORE with the staged file (probe first, harness with
    repeats 15 interleaved A/B), restores the working file; fable_0 files the deltas per M5-M7.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T09:05:00Z: ready; opens after task 2 is in review (or on owner direction) and H1 is confirmed.
STATE 2026-09-26T10:06:13Z: task 2 in review; H1 proposal recorded (note 10:06:13Z) and put to the owner; H2
waits for confirmation.
STATE 2026-09-26T10:12:00Z: H1 confirmed; H2 in progress on the strategy file.
STATE 2026-09-26T10:16:28Z: REVIEW. Owner-run: unit file, compiler suites, breakdown harness before/after
(M5/M6). Successor: task 4 (cache-faithful payload gate).
STATE 2026-09-26T10:42:09Z: REVIEW. AFTER numbers filed (note 2026-09-26T10:42:09Z); BEFORE still owed (stale index.lock broke the
stash); unit file passed in the owner's suite run.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
