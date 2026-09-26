

# Task: tests_architecture and tests_components describe the current suite

## Metadata
- Task ID: TASK-2026-09-26-refresh-tests-system-docs
- Story: none
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-26T21:12:25Z
- Updated: 2026-09-26T22:14:00Z

## Objective
`tests_architecture.md` was last updated 2026-06-13 and `tests_components.md` scored 74 (C): most cluster entries do
not name the behavior they protect. Bring the architecture doc current with the suite as it is (layers, markers,
directories, new suites since June) and deepen the component entries, then regenerate both indexes.

## Ticket Contract
- ENTRY_GATE: owner approval (Notes); authoring instructions read; inventory of the suite recorded.
- EXECUTION_BOUNDARY: `system_docs/tests_architecture.md`, `system_docs/tests_components.md` and their indexes.
- DEPENDENCIES: the Phase-5 task's regression test lands first so the docs include it.
- EXIT_GATE: both docs match the tree (paths resolve, counts measured), indexes --check clean, rubric >= 80.
- FAILURE_ESCALATION: BLOCKER if the suite layout contradicts the instructions' section contract.

## Scope Boundaries
- In scope: the two tests documents and their indexes.
- Out of scope: test code changes.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner instruction to fix the reported follow-ups, 2026-09-26T21:12:25Z.
- from_state: in_progress
- to_state: review
- transition_reason: Both docs refreshed, indexed and scored >= 80 (notes 22:14:00Z).

## Steps / Checklist
- [x] Read tests_architecture_instructions.md and tests_components_instructions.md.
- [x] Inventory the suite from disk; record drift against both docs.
- [x] Author, index, verify citations, score.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Refreshed tests_architecture.md and tests_components.md with current indexes.

## Files / Paths Impacted
- context_compass/system_docs/tests_architecture.md
- context_compass/system_docs/tests_architecture_index.md
- context_compass/system_docs/tests_components.md
- context_compass/system_docs/tests_components_index.md

## Validation
- Index --check, citation recipe, Key Files existence recipe, portability greps (notes 22:14:00Z).
  No test code changed, so no suite was run.

## Risks / Rollback Notes
- The docs are authored; nothing may be generated or asserted without reading the tests.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/tests_system_docs_refresh_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Task closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Test suite layout and the protected behavior of each cluster
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T21:12:25Z
  TYPE: DECISION
  CLAIM: Owner, after the override lane turn-in: "yeah go ahead and fix all that shit and finish up all those things,
    ok fix the rare crash bro thats a correctness issue". This task is one of the three follow-ups melder_0 reported
    (Phase-5 pool race, order-dependent guard test, weak tests system docs); the deleted unroll benchmarks need no
    action (they measured the retired emitter's dict-vs-unroll choice).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Work is owner-approved; file lists are recorded here before any edit.
  NEXT: Start after the Phase-5 fix: read the two authoring instructions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T21:58:30Z
  TYPE: FACT
  CLAIM: Suite inventory against both docs (measured on the device tree). `.py` files: unit 464 (461 test modules),
    component 143 (141), integration 148 (141), mocks 44, experimentation 196 (33 test modules; collected only by a
    local pytest). No test directory has an `__init__.py`; the 57 that exist belong to mock fixture packages and
    packages the experimentation benches generate. CI runs `run_runtime_tests.py`, which runs unit, component and
    integration in one free-threaded process with the runtime verified before and after, on the matrix from
    `python_runtime_matrix.py`. Four conftests exist (root 22, live_sim 28, conduit 445, github_workflows 73 lines).
    Six tracked `bundle.json` leftovers under `tests/unit/melder/utilities/_caching_system_tmp_load_*` are
    referenced by no test. Drift: tests_architecture said CI was UNKNOWN and named three conftests;
    tests_components says `codex*` worktrees are excluded by config (line 199; no such config exists), carries
    tool commands (lines 31-45) and has no `Protects:` line on most clusters.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:1-158
  - .github/scripts/run_runtime_tests.py:1-54
  - tests/conftest.py:1-22
  - tests/unit/github_workflows/conftest.py:1-73
  - context_compass/system_docs/tests_components.md:171-213
  IMPACT: Sets what both docs must say; the architecture doc was refreshed from it first.
  NEXT: Record the tests_architecture refresh, then refresh tests_components.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:58:30Z
  TYPE: MEASURE
  CLAIM: tests_architecture.md refreshed (edit_tests_architecture.py, 18 anchored edits; 874 lines): CI entrypoint
    block and CI/singleton-reset/concurrent-writer flows, the reset-boots-nothing rule naming the three class-level
    Aether caches, four conftests, the namespace sentence corrected, recounts, new unknowns (per-run CI matrix, the
    six bundle.json leftovers), tool commands replaced by prose. C1 remeasured (remeasure_c1.py: 8 ranges changed,
    every stamp refreshed) plus 6 new entries. Checks: index --check OK (31 sections), citation recipe clean,
    portability grep clean. Preservation diff (unique-line baseline vs after): 46 lines removed, all accounted for
    as replaced text (date, the CI unknown, old counts, "only THREE", conftest sizes 29/444, the namespace
    sentence, the Open Question), relocated tool commands and their fences, remeasured C1 values and 30 old
    `verified_at` stamps, and one rewrapped phrase.
  EVIDENCE:
  - context_compass/system_docs/tests_architecture.md:331-364
  - context_compass/system_docs/tests_architecture.md:549-741
  - context_compass/artifacts/tests_system_docs_refresh_20260926/edit_tests_architecture.py:1-293
  - context_compass/artifacts/tests_system_docs_refresh_20260926/tests_architecture_removed_lines.txt:1-46
  IMPACT: One of the two docs is done; nothing was lost from it.
  NEXT: Read tests_components_instructions.md and the rubric, then refresh tests_components.md.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:14:00Z
  TYPE: MEASURE
  CLAIM: tests_components.md refreshed (edit_tests_components.py over parts 1-7; 1,646 -> 2,484 lines). Every C3
    entry and every test C2 cluster now has a `Protects:` line, read from the tests' module docstrings and test
    names (surface.py, modoc.py, names.py). New: the CI driver in the runner component; an Experimentation And
    Profiling Trees C3; C2 clusters Package Root, Build Assets, Utilities (unit, component), Repository Tooling,
    Conduit, Multithreading and Live Sim; CI and concurrent-writer flows. Corrected: the false `codex*` exclusion,
    the reset flow (three class-level Aether caches; `Conduit._aether` assignments set an attribute src never
    reads), every tree count; tool commands replaced by prose. C1 core rebuilt as the union of the Key Files
    lists: 122 -> 181 entries (59 added), all remeasured (no range had moved), all stamps refreshed. The reset
    flow was then renamed "Singleton Reset And Re-Boot" to match tests_architecture. Checks: index --check OK
    (65 sections), citation recipe clean, Key Files existence recipe clean, portability and absolute-path greps
    empty. Preservation (baseline captured 21:45Z before any edit): 86 baseline lines have fewer copies; all are
    replaced text (scope, indexing commands, the CI unknown and open question, old counts, the codex line, the
    old runner/unit/component/integration field lines, the old reset-flow steps, the C1 intro), deduplicated rift
    bench bullets, rewritten one-line fields, and refreshed `verified_at` stamps.
  EVIDENCE:
  - context_compass/system_docs/tests_components.md:194-264
  - context_compass/system_docs/tests_components.md:1319-1387
  - context_compass/artifacts/tests_system_docs_refresh_20260926/edit_tests_components.py:1-151
  - context_compass/artifacts/tests_system_docs_refresh_20260926/tests_components_preservation.txt:1-84
  IMPACT: Both tests docs now describe the current suite; the component map names what each surface guards.
  NEXT: Record the tests_architecture follow-up and the rubric scores.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:14:00Z
  TYPE: FACT
  CLAIM: Three errors in the refreshed tests_architecture.md, found while mapping components, were corrected
    (edit_ta_followup.py): twelve CachingSystem tests write cwd-relative directories, not nine (AST count over
    test_caching_system.py); ".gitignore ... so the caches never reach a commit" was false for the six tracked
    `bundle.json` files and now covers `.melc` only; HARNESS DRIFT pointed at an authoring skill file
    (`tests_components_instructions.md`, a pointer into the tooling) and now points at its own recipe. Added: the
    opt-in profiling tree tests/experiments/cprofile_testing/ and an UNKNOWN for 140 tracked `.py` case packages the
    synthetic-module benches wrote under tests/experimentation/_*_tmp/ (they create a fresh directory per case and
    remove it with rmtree(ignore_errors=True)). Preservation: exactly 5 lines removed, all the corrected ones.
  EVIDENCE:
  - context_compass/system_docs/tests_architecture.md:532-565
  - context_compass/system_docs/tests_architecture.md:123-152
  - tests/unit/melder/utilities/test_caching_system.py:120-530
  - tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py:102-141
  - context_compass/artifacts/tests_system_docs_refresh_20260926/tests_architecture_followup_preservation.txt:1-6
  IMPACT: The pair agree; the tracked artifacts are raised, not changed.
  NEXT: Score both documents.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:14:00Z
  TYPE: MEASURE
  CLAIM: Rubric scores from the files on disk after the index rebuilds (self-scored; an independent review may
    differ). tests_components: Fidelity 4 (24), Contract 5 (15), Depth 4 (12), Addressability 3 (9), Join 5 (15),
    Mirror 5 (10) = 85, band B (was 74, C). Weak criterion: Addressability - `## C3 Components Catalog` and
    `## C2 Subcomponents Catalog` remain selectable containers (the Indexing section warns). Fidelity is 4, not
    5, because C2 `Protects:` lines are drawn from test docstrings and names, not every test body. Depth example
    still at 3: Mock Fixture Corpus Lifecycle "normal Python module import lifecycle". tests_architecture:
    Fidelity 4 (24), Contract 5 (15), Depth 4 (12), Addressability 5 (15), Join 5 (15), Mirror 5 (10) = 91, band
    A; Fidelity 4 because the follow-up found a wrong count in this same pass.
  EVIDENCE:
  - context_compass/system_docs/tests_components.md:617-706
  - context_compass/system_docs/tests_architecture_index.md:1-60
  IMPACT: Both clear the >= 80 exit gate.
  NEXT: Move the task to review; report the raised items.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:14:00Z
  TYPE: RAISE
  CLAIM: Test-tree items raised to the owner, not changed (test code is out of this task's scope): (1) the six
    tracked `bundle.json` files and the 140 tracked experimentation case packages (both UNKNOWNs in the docs);
    (2) tests/conftest.py says "no __init__.py anywhere" while 57 exist (fixture and generated packages), and
    uses `from __future__ import annotations`; (3) 245 test files assign `Conduit._aether`, which src never
    reads - harmless, but it reads like a required rebind.
  EVIDENCE:
  - tests/conftest.py:1-22
  - src/melder/aether/spellbook/spellbook.py:175-175
  IMPACT: Owner decisions; none blocks the docs.
  NEXT: Owner review of the task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T22:15:35Z
  TYPE: FACT
  CLAIM: M2-9 from melder_2 (22:07:45Z, consumed): 0.2.73 stops the normal site plan of a unique_per_conduit or
    spellspace root re-taking the slot guard its door holds, with two new tests. Both landed after the inventory, so
    edit_tests_docs_0273.py folded them in: unit 462/465, integration 142/149, conduit 35, spellbook unit 141,
    three CI tiers 745; the unit test joins the Spellbook Compiler Unit Cluster and the integration test the
    Conduit Integration Cluster, each with a Protects line; C1 core 183. Indexes --check OK, recipe and
    existence checks clean; preservation: only the seven replaced count/intro lines (and two in
    tests_architecture). M0-51 tells melder_2 the tests docs already carry their tests.
  EVIDENCE:
  - context_compass/artifacts/tests_system_docs_refresh_20260926/edit_tests_docs_0273.py:1-77
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py:1-12
  IMPACT: The docs match the tree including 0.2.73; melder_2 need not edit them.
  NEXT: Owner turn-in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Review. tests_architecture.md (895 lines, rubric 91) and tests_components.md (2,503 lines, rubric 85) describe the
current suite; both indexes --check clean. Edit scripts, preservation diffs and probes are in
artifacts/tests_system_docs_refresh_20260926/. Raised, not changed: tracked bundle.json and experimentation case
packages, the root conftest comment and future import, inert Conduit._aether assignments.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
