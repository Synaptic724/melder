

# Task: P1 - generated plans pass dependency values positionally

## Metadata
- Task ID: TASK-2026-09-26-emit-positional-constructor-args
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: review
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T16:15:41Z
- Updated: 2026-09-26T16:30:38Z

## Objective
The generalized no-overrides step plans (phase-11 codegen, the gauntlet's lane) construct each object with a
positional call for the leading dependency parameters instead of keywords, cutting the per-object cost on
CPython 3.14 (specialized allocate-and-init path) with identical binding.

## Ticket Contract
- ENTRY_GATE: attribution evidence in the measure task (keyword 170 ns vs positional 77 ns; prototype A/B);
  owner go-ahead for ideas (2026-09-26 "go ahead and ... send it"); notice to melder_0 before the tree edit.
- EXECUTION_BOUNDARY: generalized_manifest_no_overrides_compiler.py (emission and hydration helpers only) plus two
  new test files. No row, manifest or cache-format change; no public API change.
- DEPENDENCIES: melder_0 owns the override lanes and hydrators (not touched); fable_0's closed task 5 last
  edited this module; cache generation stays 14 because persisted payloads are rows, not emitted code.
- EXIT_GATE: suites green on 3.14t and GIL on the VM copy; device tree byte-identical to the validated copy;
  owner-run gauntlet before/after; owner accepts.
- FAILURE_ESCALATION: CONFLICT if another agent claims the file; BLOCKER on any suite regression; revert is
  restoring the pre-change file (no data or cache migration involved).

## Scope Boundaries
- In scope: `emit_step_plan_source`, `emit_specialized_step_plan_source`, `hydrate_no_overrides_executor`,
  `build_specialized_no_overrides_executor`, `_append_step_resolution_source`, `_emit_construct_instance`,
  new `positional_dependency_names` / `rows_positional_dependency_names`.
- Out of scope: the transient and many_only emitters and the override lanes (same lever, follow-ups).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Applied to the device tree at 16:16Z (byte-identical to the validated copy); the owner's
  Windows gauntlet run and acceptance are what remain.

## Steps / Checklist
- [x] Prototype and measure (measure task notes).
- [x] Production change as an anchored apply script (CRLF preserved, exact-once anchors).
- [x] Unit tests (20) and component tests (7); full suites on 3.14t and GIL.
- [x] Notice to melder_0; apply to the device tree with --check first; verify byte-identity.
- [ ] Owner-run gauntlet before/after on Windows.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py
- tests/unit/melder/spellbook/spell_compiler/test_generalized_positional_emission.py (new)
- tests/component/melder/spellbook/test_spellbook_component_positional_constructor_args.py (new)

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py
- tests/unit/melder/spellbook/spell_compiler/test_generalized_positional_emission.py
- tests/component/melder/spellbook/test_spellbook_component_positional_constructor_args.py

## Validation
- VM copy, CPython 3.14.7t (-X gil=0): unit spellbook 2178, component spellbook 771, integration spellbook
  581 (2 skipped, 2 xfailed, 2 xpassed), integration conduit 268, multithreading 42, unit aether 4145,
  component aether 1200 (1 xfailed), integration aether 716, unit crystallizer 565, integration crystallizer
  258 (3 xfailed), unit mutation_research 277 - all passed. GIL (-X gil=1): unit spellbook 2178, component
  spellbook 771, integration spellbook 581, unit aether 4145, conduit 268, multithreading 42 - all passed.
- Owner machine: Not run.
- Recommended commands:
  - python -m pytest tests/unit/melder/spellbook tests/component/melder/spellbook -q
  - python -m pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -s -q

## Risks / Rollback Notes
- Behavior change (intended): a positional-only dependency parameter used to fail with MeldExecutionError
  (TypeError: positional-only argument passed as keyword); it now melds.
- Classes with a custom metaclass `__call__`, a custom `__new__`, or a non-function `__init__` keep keyword
  calls, so nothing that inspects its arguments can see a different call shape.
- Rollback: restore the pre-change module; nothing persisted depends on the emitted code.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No gain claimed from a VM number alone; the owner-run number decides.

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
  - artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/ab_p1_production_cycle.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure; the owner confirms retention.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T16:15:41Z
  TYPE: DECISION
  CLAIM: Implementation shape: positional names are computed at hydration from each step's live target
    (`rows_positional_dependency_names`) and passed to emission as an optional per-row tuple; rows, manifests
    and the cache format are untouched, so no cache generation bump. The rule reads `__init__.__code__` (the
    function that receives the call), requires `type.__call__` and `object.__new__`, and takes the longest
    prefix of positional parameters that are all dependencies. The prototype's `inspect.signature` evaluated
    TYPE_CHECKING-only annotations and failed 8 tests; the code-object rule never touches annotations. No patch
    docs: no boundary, lifecycle or policy change, and the system docs do not describe argument style.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/generalized_manifest_no_overrides_compiler.diff:1-417
  - artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/apply_p1_src.py:1-519
  IMPACT: Contract-preserving by construction; the owner can ask for patch docs if wanted.
  NEXT: Record validation, then notify melder_0 and apply.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:15:41Z
  TYPE: MEASURE
  CLAIM: Production P1 on the VM copy (CPython 3.14.7t, one worker thread, 3 interleaved rounds x 7 x 3,000
    cycles, median of medians): request 15.43 -> 12.19 us (-21%), worker_a 10.50 -> 8.93 (-15%), worker_b
    10.18 -> 9.01 (-11%); clean rounds reach 11.6 / 8.7 / 8.7. All listed suites pass on 3.14t and GIL (see
    Validation). A positional-only dependency class now melds (it raised MeldExecutionError before); against
    the original emitter only that new component test fails.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/ab_p1_production_cycle.txt:1-24
  - artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/test_generalized_positional_emission.py:1-411
  - artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/test_spellbook_component_positional_constructor_args.py:1-195
  IMPACT: Tangible per-cycle gain with green suites; ready for the device tree.
  NEXT: Notice to melder_0 (M2-5), then apply with --check first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:22:07Z
  TYPE: FACT
  CLAIM: P1 applied to the device tree at 16:16Z after notice M2-5: the module is byte-identical to the validated
    VM copy (cmp) with CRLF preserved, and the two new test files are identical to the copies that passed. The
    device file was unchanged since the copy was taken, so no concurrent edit was overwritten.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1-1810
  - artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/apply_p1_src.py:1-519
  IMPACT: The owner's next gauntlet run measures P1.
  NEXT: Owner runs the gauntlet on Windows; compare same-run ratios with owner_run_20260926.txt.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:22:21Z
  TYPE: RISK
  CLAIM: A `git status` run by melder_2 inside the device VM refreshed the index and left an empty
    .git/index.lock (16:16:01Z) because the connected folder refuses deletes; git commits would have failed
    with "index.lock: File exists". melder_2 asked for delete permission (granted) and removed only that empty
    lock at 16:21Z. Rule adopted: git in the device VM runs with GIT_OPTIONAL_LOCKS=0, read-only commands only.
  EVIDENCE: attention_board.md:1-20
  IMPACT: Any agent running git through the VM mount can block the owner's git the same way.
  NEXT: Standing note on the attention board so every agent sees it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T19:06:31Z
  TYPE: FACT
  CLAIM: Since melder_0's S2b-2 (on the device at 17:26Z), P1's emitter is no longer on the normal meld path.
    Generalized normal hydration now uses the site-plan runtime's execute_normal as the inner no-overrides
    executor. emit_step_plan_source, where P1 lives, is reached only through the opt-in singleton specializer
    (generalized_singleton_specialization_enabled, default False) and the tests that pin the old emission. The
    positional lever lives on in melder_0's lowering: SitePlanEmission._call_arguments passes operands
    positionally in signature order until the first omitted parameter. So the owner's next gauntlet run measures
    the lowering's positional calls, not P1's code. One difference: P1 kept keyword calls unless the class used
    type.__call__, object.__new__ and a plain-function __init__, so a metaclass or __new__ that inspects argument
    names saw the same call shape. The lowering has no such guard. Whether its parameter kinds make that case
    safe is UNKNOWN (melder_0's lane; sent as an FYI).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:266-345
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:883-936
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:470-476
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:1703-1720
  - artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/generalized_manifest_no_overrides_compiler.diff:212-273
  IMPACT: P1's gain now reaches the gauntlet through the lowering, and P1's own code will leave with melder_0's
    S2b-3 retirement of the old normal emitters (the owner's decision). P1 stays in review until then; closing
    it is the owner's call.
  NEXT: Tell the owner in the next report; send the guard FYI in the NOTICE to melder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T19:50:20Z
  TYPE: FACT
  CLAIM: Consumed M0-41 (melder_0, 19:33:08Z), a reply to M2-7 item 4. The guard question was a real behavior
    change. Since S2b-2 the generalized family passed dependencies positionally to a class whose inherited
    __new__ sees the call (melder_0's pos_probe.py). melder_0 fixed it as P5 (0.2.69): the lowering now applies
    P1's rule (type.__call__, object.__new__, a plain-function __init__), extended to plain functions and bound
    methods (SitePlanLowering.positional_run); root __args__ values stay positional. P1's own emitter leaves with R2.
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:2478-2491
  IMPACT: P1 lives on as the lowering's positional rule; its code retires with melder_0's R2. The P1 task can be
    closed when the owner accepts.
  NEXT: Put P1's closure to the owner with the next report.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
P1 validated on the VM copy and applied to the device tree (16:16Z, byte-identical). Waiting on the owner's
Windows gauntlet run (same-run ratios against owner_run_20260926.txt) and acceptance.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
