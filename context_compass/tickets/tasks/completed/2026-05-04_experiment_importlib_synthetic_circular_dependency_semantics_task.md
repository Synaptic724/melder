# Task: Experiment Importlib Synthetic Circular Dependency Semantics
- Completed: 2026-05-10T00:06:36Z
- Summary: Closed after the importlib-style circular dependency bench proved
  the benign and bad synthetic/mixed cycle cases we needed.

## Metadata
- Task ID: TASK-2026-05-04-experiment-importlib-synthetic-circular-dependency-semantics
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-04T00:31:26Z
- Updated: 2026-05-10T00:06:36Z

## Objective
Build a bounded experiment under `tests/experimentation/` that proves what
importlib-style loading buys us for circular dependencies across:
- pure synthetic module graphs
- mixed physical/synthetic module graphs

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for experiments that test whether
  importlib-style loading can manage circular synthetic-module dependencies
  better than ad hoc module handling.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - `tests/experimentation/synthetic_module_import_testbench.py`
  - `tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py`
  - `tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py`
- EXIT_GATE: one runnable experiment exists and records at least:
  - benign synthetic cycle behavior
  - failing synthetic partial-init cycle behavior
  - benign mixed physical/synthetic cycle behavior
  - failing mixed physical/synthetic partial-init cycle behavior
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the bounded experiment
  requires a production loader implementation instead of a testbench.

## Scope Boundaries
- In scope:
  - importlib/meta-path synthetic loader behavior
  - circular import semantics
  - mixed physical/synthetic cycle semantics
  - observable failure mode capture
- Out of scope:
  - production crystallizer loader implementation
  - broad persistence or bootstrap policy changes
  - speculative cycle-resolution design beyond observed runtime behavior

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the four-case importlib cycle bench is implemented and
  the runtime behavior is now evidenced, so the next step is user review
  rather than more implementation.

## Steps / Checklist
- [ ] Build the importlib circular-dependency experiment bench.
- [ ] Cover synthetic benign/failing cycle cases.
- [ ] Cover mixed physical/synthetic benign/failing cycle cases.
- [ ] Run the bench and record the outcomes in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one bounded experiment bench for importlib-driven circular dependency semantics
- one concrete validation result showing what works and what fails

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-04_experiment_importlib_synthetic_circular_dependency_semantics_task.md
- codex/context_compass/attention_board.md
- tests/experimentation/

## Validation
- Not run.
- Recommended commands:
  - `python tests/experimentation/importlib_synthetic_circular_dependency_testbench.py`

## Risks / Rollback Notes
- Risk: the bench drifts into a production loader prototype.
  Rollback: keep the scope on runtime semantics only and stop at observed
  importlib behavior.

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
- DATETIME: 2026-05-04T00:31:26Z
  TYPE: PLAN
  CLAIM: The next bounded move is an importlib-semantics experiment, not more
    loader philosophy. The experiment should prove whether importlib-style
    loading gives us useful circular-dependency behavior for synthetic modules
    and mixed physical/synthetic graphs, and what exact failure mode appears
    when a cycle is semantically bad rather than merely present.
  EVIDENCE:
  - user_instruction: "go ahead and build some experiments to see if we can use it to detect circ dep of synthetic modules and even a mix"
  IMPACT: The next discussion about using importlib more should be based on a
    concrete runtime bench rather than on assumptions about what importlib
    probably does.
  NEXT: implement the four-case experiment bench and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T00:33:53Z
  TYPE: MEASURE
  CLAIM: The importlib cycle bench is green and it split the behavior cleanly.
    Benign synthetic cycles and benign mixed physical/synthetic cycles both
    load successfully when the loader follows importlib-style semantics:
    package/module shells are published early, module code executes against
    that partial world, and later reads happen after initialization settles.
    Bad synthetic and bad mixed cycles fail visibly with the expected
    partial-initialization import signal instead of silently producing a fake
    complete world.
  EVIDENCE:
  - tests/experimentation/importlib_synthetic_circular_dependency_testbench.py:1-344
  - validation_result:
    `python.exe tests/experimentation/importlib_synthetic_circular_dependency_testbench.py`
    -> `OK_IMPORTLIB_SYNTHETIC_BENIGN_CYCLE`
    -> `OK_IMPORTLIB_SYNTHETIC_BAD_CYCLE_DETECTED`
    -> `OK_IMPORTLIB_MIXED_BENIGN_CYCLE`
    -> `OK_IMPORTLIB_MIXED_BAD_CYCLE_DETECTED`
    -> `OK_IMPORTLIB_SYNTHETIC_CIRCULAR_DEPENDENCY_EXPERIMENTS`
  IMPACT: We now have direct repo-local evidence that importlib-style loading
    is worth using for activation/runtime semantics, including circular import
    behavior, while `SpellCrystal` still has to own graph truth and dependency
    validation.
  NEXT: use this result when deciding how much of the production synthetic
    loader should lean on importlib finder/loader behavior instead of ad hoc
    exec-only activation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded experiment lane for importlib-driven circular
dependency behavior in synthetic and mixed module worlds.
