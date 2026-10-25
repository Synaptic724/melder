# Task: Refuse materializing codegen over live modules and leave sys.modules as found (defect D-20)

## Metadata
- Task ID: TASK-2026-10-10-refuse-materializing-over-live-modules
- Story: none; parent EPIC-2026-10-25-codegen_room_policy_defects (defect found by
  TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: blocked
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-25T01:29:39Z

## Objective
`materialize_codegen` publishes a SyntheticModule under any dotted-legal name - over Melder's own modules, the
standard library and installed dependencies - under every codegen profile that accepts the code, and its failure
and cleanup paths leave a displaced name missing instead of restoring it. Make generation refuse existing names,
protected core roots, standard-library names and installed import names (review contract C1.4, case N11), and make
every exit leave `sys.modules` and the parent package attribute as found (case R6).

## Defect
- Symptom: under safe and hybrid alike, `Bind = None` materialized as `melder.aether.spellbook.bind.bind` replaces the
  core module (`importlib.import_module` and the parent package attribute return the SyntheticModule); a new
  `melder.injected_probe` joins the melder package; `csv` is replaced; `pytest` is shadowed. A materialize over `csv`
  whose exec raises leaves `csv` absent from `sys.modules`, and cleanup of a successful replacement of `json` leaves
  `json` absent: the original module is never restored.
- Secondary: materialized source executes with the interpreter's full builtins - `execute_source` execs into the
  module dict and nothing in `synthetic_module.py` sets `__builtins__`, so Python inserts the real ones - while
  `execute_codegen` runs with the room's filtered builtins. The code is still validated statically first.
- Reproducer: `context_compass/artifacts/core_protection_review_20261010/probes/probe_materialize.py` and
  `probe_materialize_fail.py`, with their recorded outputs (rerun 2026-10-10T13:33Z on this tree). No test pins the
  defect yet (the review left a strict xfail to the owner, contract C6.2); the red tests of this ticket are its pin.
- Cause: `CodegenCommandSystem.materialize_codegen` checks `module_name` for dotted-identifier legality only;
  `SyntheticModule.publish_to_sys_modules` assigns `sys.modules[name]` unconditionally and attaches the parent
  package attribute; `SyntheticModule.cleanup` removes only its own object and keeps no record of what it displaced;
  the command's failure path (R8) calls that cleanup.
- Impact: one accepted materialize can disable or rewrite Melder's runtime for the rest of the process (after
  `Bind = None` every later import of the bind module gets the synthetic one), or shadow a dependency, and nothing
  in-process puts it back. This contradicts the owner's direction that dependencies are never hot-mutated and that
  core changes are denied by default (review Note 17).

## Ticket Contract
- ENTRY_GATE: the owner selects this ticket, assigns an implementer and routes it on `attention_board.md`; the owner
  answers the two questions below; patch docs exist (a new generation gate and a SyntheticModule contract change).
- EXECUTION_BOUNDARY: `src/melder/nexus/rift/command_system/codegen_command_system.py` (`materialize_codegen`),
  `src/melder/crystallizer/synthetic_module.py` (publication and cleanup), the codegen ACL configuration if the
  namespace becomes an ACL rule; tests: `tests/unit/melder/aether/test_codegen_materialize_verb.py` and a new
  integration test; src_components (SyntheticModule, codegen command system), src_architecture; the release note.
- DEPENDENCIES: the review contract C1.4, C3.4, C4.3 (in-process replacement has no rollback today) and D2; the
  crystallizer restore and rebuild lanes also publish SyntheticModules, so a guard placed in SyntheticModule itself
  must keep those lanes working (restore skips modules already in `sys.modules`, review Note 21).
- EXIT_GATE: the acceptance criteria pass with the GIL off; notch, release note and rebuild per the contribution
  guide; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST if a restore or rebuild lane needs to publish over an existing name; CONFLICT
  if an existing test materializes over a live module on purpose.

## Questions for the Owner
- Where is the generation namespace declared (C1.4): a codegen ACL capability rule with module-root conditions, a
  Nexus or room configuration value, or one fixed prefix (for example `codegen_generated`)? Recommendation: an ACL
  capability rule, so each frame's posture states it and the existing compile path carries it.
- Should materialized code execute with the room's filtered builtins? Recommendation: yes, the same mapping
  `execute_codegen` uses, so a materialized module cannot reach what the room cannot.

## Scope Boundaries
- In scope: the name policy for `materialize_codegen`; restoring `sys.modules` and the parent attribute on every
  exit; the builtins mapping for materialized source if the owner agrees.
- Out of scope: live in-place module replacement as a feature (review D7 keeps it an experiment lane); the
  crystallizer's own restore semantics; `open` (D-10); dynamic imports (D-11).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24), "focus on 2 and 3 make an epic for each and investigate them",
  scheduled it under EPIC-2026-10-25-codegen_room_policy_defects; melder_0 re-measures it on 0.2.8267
  and puts the two questions to the owner.

## Steps / Checklist
- [x] Re-measure on 0.2.8267 (EPIC-2026-10-25-codegen_room_policy_defects): rerun the reproducer
      and the materialize verb tests, the GIL off and on; read the cited code at today's lines; record MEASURE
      and FACT notes; put the two questions to the owner.
- [ ] Owner answers the two questions; patch docs written and linked.
- [ ] Red first: symptom-named tests for the cases below fail on the current code.
- [ ] Implement the name policy and the restoring exits; run the codegen and crystallizer tiers with the GIL off.
- [ ] Update tests_components, src_components, src_architecture and the release note.
- [ ] Notch, rebuild assets and llm_support last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Acceptance Criteria
- [ ] Materializing under a name already in `sys.modules` - a melder module, a stdlib module such as `csv`, an
      installed import name such as `pytest` - is refused before anything is registered or published, and
      `sys.modules` and the parent package attribute are unchanged (N11).
- [ ] A new name under a protected core root (`melder.injected_probe`), a standard-library name
      (`sys.stdlib_module_names`) and an installed top-level import name
      (`importlib.metadata.packages_distributions()`) are refused even when not yet imported.
- [ ] Inside the declared generation namespace a new name materializes as today; the existing materialize verb tests
      keep passing (moved under the namespace if needed).
- [ ] A materialize whose exec raises, and the cleanup of a materialized module, leave `sys.modules` and the parent
      attribute exactly as they were before the materialize (R6).
- [ ] If the owner agrees, materialized source runs with the room's filtered builtins, pinned by a test that a name
      the room denies is unavailable to the module.
- [ ] The release note carries a Breaking change entry for room code that materialized over existing names;
      src_architecture records D-20 as closed and the generation rule as an invariant.
- [ ] The crystallizer restore, rebuild and graft tiers pass with the GIL off; Windows tiers and hosted CI are
      reported Not run until seen.

## Deliverables
- The generation name policy, the restoring exits, their regressions and the documentation updates.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY.

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_codegen_materialize_verb.py`
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/integration/melder/crystallizer`

## Risks / Rollback Notes
- A guard placed in SyntheticModule could break crystallizer lanes that publish synthetic modules; prefer the codegen
  verb as the enforcement point unless the restore lanes are covered by tests.
- Rollback is reverting the verb and SyntheticModule changes; recorded worlds and caches are not affected.
- A name policy in-process is defence in depth, not isolation (contract C6.1).

## Applicable Anti-Patterns
- [ ] No implementation before the owner answers the two questions.
- [ ] No claim that the fix isolates agent code (C6.4 wording rule).
- [ ] No closure without red-then-green tests for N11 and R6 and board sync.

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
- ARTIFACTS_REQUIRED: true (the reproducers live in the review's evidence pack)
- ARTIFACT_PATHS:
  - artifacts/core_protection_review_20261010/probes/probe_materialize.py
  - artifacts/core_protection_review_20261010/probes/probe_materialize_output.txt
  - artifacts/core_protection_review_20261010/probes/probe_materialize_fail.py
  - artifacts/core_protection_review_20261010/probes/probe_materialize_fail_output.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none; the pack belongs to the completed review ticket.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: codegen materialization; in-process module replacement
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-10T13:40:50Z
  TYPE: FACT
  CLAIM: Opened from the core-protection review's hand-back (review ticket Notes 20, 27 and 28). At 66939dfe8
    materialize_codegen checks module_name for legality only, publication overwrites sys.modules and the parent
    attribute unconditionally, and cleanup never restores a displaced module; the probes rerun on this tree show a
    core, a stdlib and an installed name replaced under safe and hybrid, and the originals lost on failure and on
    cleanup. No test pins it yet.
  EVIDENCE:
  - src/melder/nexus/rift/command_system/codegen_command_system.py:739-888
  - src/melder/crystallizer/synthetic_module.py:462-531
  - src/melder/crystallizer/synthetic_module.py:901-949
  - src/melder/crystallizer/synthetic_module.py:1047-1094
  - tests/unit/melder/aether/test_codegen_materialize_verb.py:1-146
  - context_compass/artifacts/core_protection_review_20261010/probes/probe_materialize_output.txt:1-11
  - context_compass/artifacts/core_protection_review_20261010/probes/probe_materialize_fail_output.txt:1-6
  IMPACT: Agent code in any codegen room can replace a running core or dependency module with no way back.
  NEXT: Owner answers where the generation namespace is declared and whether materialized code gets room builtins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:16:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Scheduled under EPIC-2026-10-25-codegen_room_policy_defects at the owner's ask (chat 2026-10-24),
    "focus on 2 and 3 make an epic for each and investigate them".
    The re-measure, on a /tmp copy of the 0.2.8267 tree, the GIL off and on: (1) probe_materialize.py and
    probe_materialize_fail.py (a core, a new melder.*, a stdlib and an installed name materialized; the originals
    lost on a failed materialize and on cleanup); (2) the materialize verb unit tests; (3) a read at today's lines
    of CodegenCommandSystem.materialize_codegen and SyntheticModule's publication, execution and cleanup; (4) every
    other publisher of a SyntheticModule (the crystallizer's restore, rebuild and graft lanes) listed with what it
    expects of sys.modules, so the guard's place is chosen with them in view; (5) the builtins materialized source
    runs with, observed.
  EVIDENCE:
  - context_compass/artifacts/core_protection_review_20261010/probes/probe_materialize.py:1-52
  - context_compass/artifacts/core_protection_review_20261010/probes/probe_materialize_fail.py:1-34
  - tests/unit/melder/aether/test_codegen_materialize_verb.py:1-146
  IMPACT: The owner answers the namespace and builtins questions knowing which lanes a guard would meet.
  NEXT: Copy the 0.2.8267 tree to /tmp and run both probes, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:23:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Re-measured on the /tmp copy of 0.2.8267, the GIL off and on. probe_materialize.py: under safe and hybrid
    alike a materialize over `melder.aether.spellbook.bind.bind` replaces the core module (import_module and the
    parent package attribute return the SyntheticModule), a new `melder.injected_probe` joins the package, `csv`
    is replaced and `pytest` is shadowed. probe_materialize_fail.py: a materialize over `csv` whose exec raises
    leaves `csv` absent from sys.modules, and cleanup of a `json` replacement leaves `json` absent - the
    original is never restored. Identical to 2026-10-10 and byte-identical across GIL modes. The materialize
    verb unit tests still pass (5 passed). So D-20 reproduces unchanged at 0.2.8267.
  EVIDENCE:
  - artifacts/codegen_room_policy_20261025/runs/probe_materialize_0_2_8267_gil0.txt:1-11
  - artifacts/codegen_room_policy_20261025/runs/probe_materialize_fail_0_2_8267_gil0.txt:1-6
  - artifacts/codegen_room_policy_20261025/runs/codegen_tests_0_2_8267_gil0.txt:1-40
  IMPACT: The recorded symptom holds, so the owner's namespace and builtins answers rest on current behaviour.
  NEXT: Confirm the cause at today's lines (next note), then put the two questions to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:23:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The cause holds at 0.2.8267, read at today's lines (line numbers, not bodies). `materialize_codegen`
    (codegen_command_system.py:739) checks `module_name` for dotted-identifier legality only, with no existing /
    protected / stdlib / installed check. `SyntheticModule.publish_to_sys_modules` (:930) assigns
    `sys.modules[self.__name__]` unconditionally (:947) and keeps no record of what it displaced;
    `SyntheticModule.cleanup` (:462, del at :501; a second path at :970) removes only its own object, so a
    displaced original is never put back. `execute_source` (:901) execs into the module dict and sets no
    `__builtins__`, so materialized code runs with the interpreter's full builtins, where execute_codegen uses
    the room's filtered set. The two owner questions (generation namespace; room builtins for materialized
    code) are unchanged, and the crystallizer restore/rebuild/graft lanes that also publish SyntheticModules
    remain the reason to prefer the verb as the enforcement point.
  EVIDENCE:
  - src/melder/nexus/rift/command_system/codegen_command_system.py:739-739
  - src/melder/crystallizer/synthetic_module.py:901-947
  - src/melder/crystallizer/synthetic_module.py:462-501
  IMPACT: The fix is a name policy plus restoring exits, after the owner answers; a guard's place weighs the lanes.
  NEXT: DECISION_REQUEST to the owner: where the generation namespace is declared; room builtins for materialized
    code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:37:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's decision (chat 2026-10-25, answering the decision request): the generation namespace is declared
    as a codegen ACL capability rule (module-root conditions in each frame's posture, carried by the existing
    compile path), and materialized code runs with the room's filtered builtins, the same mapping
    execute_codegen uses - the recommended option. What follows for the patch doc: materialize_codegen refuses
    a name outside the declared namespace, a name already in sys.modules, a protected core root, a stdlib name
    and an installed import name, before anything is registered or published; every exit leaves sys.modules and
    the parent attribute as found; the guard sits at the verb, because the crystallizer's restore, rebuild and
    graft lanes publish SyntheticModules outside any room's posture. Carried into the patch doc for the owner's
    confirmation: a frame that declares no namespace rule refuses every materialize (recommended: fail closed).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md:58-63
  - context_compass/tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md:230-252
  IMPACT: The fix proceeds on a decided design; the default for a frame without a rule is named before the patch doc.
  NEXT: On the owner's go: write the patch docs (the verb's name policy, SyntheticModule's exits, the builtins).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T01:29:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: BLOCKER
  CLAIM: The owner gave the go on 2026-10-25; melder_0 is blocked by the session's content filter (the epic's
    BLOCKER note). Nothing in src/ changed; this task is ready for another implementer as specified.
  EVIDENCE: context_compass/tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md:254-271
  IMPACT: The task is unstarted.
  NEXT: The owner assigns an implementer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Scheduled 2026-10-25 under EPIC-2026-10-25-codegen_room_policy_defects (the owner's ask); in_progress, melder_0,
investigation only. Scope unchanged: materialize_codegen replaces live core, stdlib and dependency modules and
cannot restore them (Note of 2026-10-10). State: the re-measure on 0.2.8267 is planned (PLAN note); nothing run
yet. Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the verb
tests pass. Decided 2026-10-25 (DECISION note): an ACL capability rule declares the namespace; materialized
code gets the room's filtered builtins; a frame with no rule fails closed (to confirm in the patch doc).
Next, on the owner's go: patch docs, red tests, the fix, notch and rebuild.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
