# Task: Experiment Synthetic Module Import In Runtime

## Metadata
- Task ID: TASK-2026-04-26-experiment-synthetic-module-import
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: review
- Owner: codex
- Agent Name: codex_01
- Priority: p1
- Created: 2026-04-26T17:20:21Z
- Updated: 2026-04-28T11:47:20Z

## Objective
Build a focused experimental test bench under `tests/experimentation/` that
materializes one synthetic module in memory, registers it, and proves that a
second generated/importing unit can consume it the way later codegen/runtime
flows would need.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a test jig to experimentally prove
  in-memory synthetic-module import behavior before more design discussion.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - current crystallizer design epic
  - Python module/import semantics only
- EXIT_GATE: the experiment exists, is runnable, and records how far the
  in-memory synthetic-module approach gets in practice.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if Python import semantics force
  a much broader experimental harness than this bounded test jig.

## Scope Boundaries
- In scope:
  - synthetic module test bench
  - in-memory module registration
  - second-unit import/use proof
- Out of scope:
  - crystallizer implementation
  - runtime production code changes
  - package-manager behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an experiment-first proof of
  synthetic-module import behavior.

## Steps / Checklist
- [ ] Create `tests/experimentation/`.
- [ ] Build the synthetic module and loader test bench.
- [ ] Record the concrete import/registration behavior in `## Notes`.
- [ ] Run the experiment and capture results.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one experimentation bench under `tests/experimentation/`
- one concrete validation result for synthetic-module import behavior

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-26_experiment_synthetic_module_import_task.md
- codex/context_compass/attention_board.md
- tests/experimentation/

## Validation
- Executed:
  - `python tests/experimentation/synthetic_module_import_testbench.py`
- Result:
    - `OK_SYNTHETIC_MODULE_IMPORT`
    - loaded synthetic package graph:
      - `synthetic_pkg`
      - `synthetic_pkg.base`
      - `synthetic_pkg.consumer`
      - `synthetic_pkg.feature`
  - Executed:
    - `python tests/experimentation/synthetic_module_import_testbench.py`
  - Result:
    - `OK_SYNTHETIC_MODULE_IMPORT_DEEP`
    - loaded deep synthetic package graph:
      - `synthetic_pkg`
      - `synthetic_pkg.runtime`
      - `synthetic_pkg.runtime.primitives`
      - `synthetic_pkg.runtime.primitives.base`
      - `synthetic_pkg.base`
      - `synthetic_pkg.feature`
      - `synthetic_pkg.api`
      - `synthetic_pkg.api.v1`
      - `synthetic_pkg.api.v1.surface`
      - `synthetic_pkg.consumer`
  - Executed:
    - `python tests/experimentation/synthetic_module_import_testbench.py`
  - Result:
    - `OK_SYNTHETIC_MODULE_IMPORT_DEEP_IMPORTLIB`
    - importing only `synthetic_pkg.consumer` through a synthetic
      `meta_path` finder/loader was enough to auto-load the full registered
      synthetic dependency closure with no physical files

## Risks / Rollback Notes
- Risk: the bench accidentally proves only a trivial exec scenario instead of
  an import-by-name scenario.
  Rollback: keep the bench focused on explicit import semantics and second-unit
  consumption, not raw namespace sharing.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-26T17:20:21Z
  TYPE: FACT
  CLAIM: The user wants a concrete experiment, not more abstract design, to
    test whether a synthetic module can be created in memory, registered, and
    then imported or consumed by a second generated unit.
  EVIDENCE:
  - user_instruction: "make a test bench to see if you can actually do this stuff"
  - user_instruction: "make the object in memory put some stuff in there, and then add it to sys.modules and import it into a codegen"
  IMPACT: The next move must be an isolated experimental harness under
    `tests/experimentation/`, not more design drift.
  NEXT: create the experimentation folder and build the minimal synthetic
    module import bench.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T17:22:21Z
  TYPE: FACT
  CLAIM: The bench now exists and proves the core synthetic-module case in one
    process. A synthetic package shell plus synthetic submodules can be
    materialized as real module objects, inserted into `sys.modules` before
    execution, and then imported by name from a dependent synthetic unit using
    normal Python import syntax.
  EVIDENCE:
  - tests/experimentation/synthetic_module_import_testbench.py:47-110
  - tests/experimentation/synthetic_module_import_testbench.py:113-158
  - tests/experimentation/synthetic_module_import_testbench.py:161-187
  IMPACT: We now have a concrete proof that the synthetic-module direction is
    viable for normal import-style use, at least for a package/submodule graph
    materialized inside one process.
  NEXT: record the validation result and return the experiment for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T17:22:21Z
  TYPE: MEASURE
  CLAIM: The focused synthetic-module import bench is green. The package shell,
    submodule imports, export access, and cleanup all worked in one process.
  EVIDENCE:
  - validation_result: `python tests/experimentation/synthetic_module_import_testbench.py` -> `OK_SYNTHETIC_MODULE_IMPORT`
  IMPACT: We can discuss the next semantic questions from a real working proof
    instead of only from theory.
  NEXT: return the experiment for review and decide whether to extend it into
    package scopes, shared/local module spaces, or restoration semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T17:22:21Z
  TYPE: DECISION
  CLAIM: The synthetic-module direction should now be treated as a validated
    core crystallizer feature. The bench proved that a synthetic package shell
    and dependent submodules can be created fully in memory, inserted into
    `sys.modules` before execution, consumed through normal import syntax, and
    cleaned back out deterministically.
  EVIDENCE:
  - tests/experimentation/synthetic_module_import_testbench.py:47-110
  - tests/experimentation/synthetic_module_import_testbench.py:113-187
  - validation_result: `python tests/experimentation/synthetic_module_import_testbench.py` -> `OK_SYNTHETIC_MODULE_IMPORT`
  IMPACT: Later crystallizer design no longer needs to treat in-memory module
    import semantics as hypothetical. It can use this as a real baseline for
    synthetic module records, graph recovery, and import-friendly reuse.
  NEXT: mirror this decision into the crystallizer epic so later stories inherit
    the validated synthetic-module direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-27T23:43:28Z
  TYPE: PLAN
  CLAIM: The user asked for a deeper import-semantics extension of the existing
    bench. The next slice is to prove that nested synthetic packages and
    re-exported deep objects remain usable across multiple import hops instead
    of only one package-shell plus one direct submodule chain.
  EVIDENCE:
  - user_instruction: "can we use synthetic modules in memory to reference other inmemory synthetic modules?"
  - user_instruction: "can you test a deep object import step so that each synthetic module can be properly used?"
  - tests/experimentation/synthetic_module_import_testbench.py:1-178
  IMPACT: The existing green bench is not the end of the lane; it now needs
    one bounded extension that stresses deeper object import and re-export
    semantics before we treat the module graph story as strong enough.
  NEXT: extend the bench with nested package/subpackage records, deep object
    imports, and assertions that the imported objects are callable/constructable
    through the full synthetic graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-27T23:45:08Z
  TYPE: FACT
  CLAIM: The bench now proves a deeper import path than the original slice. A
    nested synthetic package/subpackage graph can re-export deep objects
    through `synthetic_pkg.api.v1.surface`, and a later consumer module can
    import those re-exported objects and use them normally.
  EVIDENCE:
  - tests/experimentation/synthetic_module_import_testbench.py:101-169
  - tests/experimentation/synthetic_module_import_testbench.py:172-209
  IMPACT: The synthetic-module direction now has a stronger baseline than a
    shallow one-hop import proof. Deep package shells, re-exports, and
    downstream consumer usage all behave like normal Python modules in one
    process.
  NEXT: return the deeper bench for review and decide whether the next seam is
    shared/local module spaces, circular imports, or restore-time loading.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-27T23:45:08Z
  TYPE: MEASURE
  CLAIM: The deeper synthetic-module bench is green. Nested package shells,
    deep object imports, re-exported class aliases, and downstream consumer use
    all passed inside one process, and cleanup removed the full graph from
    `sys.modules`.
  EVIDENCE:
  - tests/experimentation/synthetic_module_import_testbench.py:172-219
  - validation_result: `python tests/experimentation/synthetic_module_import_testbench.py` -> `OK_SYNTHETIC_MODULE_IMPORT_DEEP`
  IMPACT: We now know the current loader pattern supports deeper import hops
    and usable object flow, not just shallow module visibility.
  NEXT: decide the next bounded synthetic-module stress case.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-28T11:43:02Z
  TYPE: PLAN
  CLAIM: The user explicitly asked to add more loader features, not just more
    manually pre-materialized module assertions. The next bounded experiment is
    to give the bench a real `importlib`/`meta_path` path so that importing the
    top-level synthetic consumer triggers dependency-module materialization from
    the in-memory record registry instead of forcing the bench to preload the
    entire closure by hand.
  EVIDENCE:
  - user_instruction: "add more features to the loader see what else we can learn from our experiments"
  - tests/experimentation/synthetic_module_import_testbench.py:1-219
  IMPACT: This distinguishes "manual sys.modules stuffing works" from
    "synthetic modules can participate in a real importlib-driven load path",
    which is a stronger proof for the crystallizer runtime story.
  NEXT: extend the bench loader with a finder/loader install path, rerun the
    experiment, and record whether importing only the top-level synthetic
    consumer auto-loads the dependency graph correctly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-28T11:47:20Z
  TYPE: FACT
  CLAIM: The bench now has a real importlib-driven path. A synthetic
    `meta_path` finder/loader can serve module specs from the in-memory record
    registry, and importing only `synthetic_pkg.consumer` is enough to
    auto-materialize the full synthetic dependency closure into `sys.modules`.
  EVIDENCE:
  - tests/experimentation/synthetic_module_import_testbench.py:81-99
  - tests/experimentation/synthetic_module_import_testbench.py:217-224
  - tests/experimentation/synthetic_module_import_testbench.py:464-480
  IMPACT: The experiment now proves more than manual preload semantics. It
    shows that synthetic modules can participate in a real importlib-style load
    path without physical files, which is a stronger baseline for later
    crystallizer loader work.
  NEXT: return the loader-enhanced bench for review and decide whether the next
    seam should be circular imports, partial graph unload, or restore-time load
    order from persisted crystal records.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-28T11:47:20Z
  TYPE: MEASURE
  CLAIM: The importlib-driven synthetic loader bench is green. Both the direct
    materialization path and the new `meta_path` path loaded the same ten-module
    synthetic graph, and the importlib path succeeded without manual
    pre-materialization of each module.
  EVIDENCE:
  - tests/experimentation/synthetic_module_import_testbench.py:464-480
  - validation_result: `python tests/experimentation/synthetic_module_import_testbench.py` -> `OK_SYNTHETIC_MODULE_IMPORT_DEEP_IMPORTLIB`
  IMPACT: We now know the next loader questions are not basic import viability
    but more advanced lifecycle and graph-management semantics.
  NEXT: choose the next bounded synthetic-loader stress case.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded synthetic-module import experiment under
`tests/experimentation/`.
