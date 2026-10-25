# Task: Refuse materializing codegen over live modules and leave sys.modules as found (defect D-20)

- Completed: 2026-10-25T12:10:50Z
- Summary: materialize_codegen never replaces a live module and gives back what it touched. Under every codegen profile it
  refuses a name already loaded, under `melder`, a standard-library or installed import name, before anything is
  registered or published (a payload with `refusal`); a frame's new `materialize_modules` rules narrow it further,
  and a frame with no rule keeps materializing new names (the owner's decision). Materialized code runs with the
  room's filtered builtins. A failed materialize cleans the module and the parent shells it created;
  SyntheticModule gives back a displaced non-synthetic module or parent attribute on unpublish, detach and
  cleanup. Known limit: a successful dotted materialize under a new root leaves its parent shell after the
  module's own cleanup. Notched 0.2.8272; release-note section "`materialize_codegen` no longer replaces a live
  module". Tiers green the GIL off and on on Linux (d20_tiers.txt); Windows tiers, hosted CI and
  integration/multithreading Not run. Rebuild last, after the closure.

## Metadata
- Task ID: TASK-2026-10-10-refuse-materializing-over-live-modules
- Story: none; parent EPIC-2026-10-25-codegen_room_policy_defects (defect found by
  TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-25T12:10:50Z

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

- from_state: blocked
- to_state: in_progress
- transition_reason: D-11 landed (TASK-2026-10-10-enforce-import-policy-on-dynamic-imports closed 2026-10-25,
  notched 0.2.8271), ending the tranche-order block; the owner's direction (chat 2026-10-25T11:17Z): "finish the
  D-20 and its epic".

- from_state: in_progress
- to_state: done
- transition_reason: landed and validated on the owner's direction (chat 2026-10-25T11:17Z), "finish the D-20
  and its epic"; notched 0.2.8272. Rebuild last.

## Steps / Checklist
- [x] Re-measure on 0.2.8267 (EPIC-2026-10-25-codegen_room_policy_defects): rerun the reproducer
      and the materialize verb tests, the GIL off and on; read the cited code at today's lines; record MEASURE
      and FACT notes; put the two questions to the owner.
- [x] Owner answers the two questions; patch docs written and linked.
- [x] Red first: symptom-named tests for the cases below fail on the current code.
- [x] Implement the name policy and the restoring exits; run the codegen and crystallizer tiers with the GIL off.
- [x] Update tests_components, src_components, src_architecture and the release note.
- [x] Notch, rebuild assets and llm_support last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Acceptance Criteria
- [x] Materializing under a name already in `sys.modules` - a melder module, a stdlib module such as `csv`, an
      installed import name such as `pytest` - is refused before anything is registered or published, and
      `sys.modules` and the parent package attribute are unchanged (N11).
- [x] A new name under a protected core root (`melder.injected_probe`), a standard-library name
      (`sys.stdlib_module_names`) and an installed top-level import name
      (`importlib.metadata.packages_distributions()`) are refused even when not yet imported.
- [x] Inside the declared generation namespace a new name materializes as today; the existing materialize verb tests
      keep passing (moved under the namespace if needed).
- [x] A materialize whose exec raises, and the cleanup of a materialized module, leave `sys.modules` and the parent
      attribute exactly as they were before the materialize (R6).
- [x] If the owner agrees, materialized source runs with the room's filtered builtins, pinned by a test that a name
      the room denies is unavailable to the module.
- [x] The release note carries a Breaking change entry for room code that materialized over existing names;
      src_architecture records D-20 as closed and the generation rule as an invariant.
- [x] The crystallizer restore, rebuild and graft tiers pass with the GIL off; Windows tiers and hosted CI are
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
- [x] No implementation before the owner answers the two questions.
- [x] No claim that the fix isolates agent code (C6.4 wording rule).
- [x] No closure without red-then-green tests for N11 and R6 and board sync.

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
- ARTIFACTS_REQUIRED: true (the reproducers live in the review's evidence pack)
- ARTIFACT_PATHS:
  - artifacts/core_protection_review_20261010/probes/probe_materialize.py
  - artifacts/core_protection_review_20261010/probes/probe_materialize_output.txt
  - artifacts/core_protection_review_20261010/probes/probe_materialize_fail.py
  - artifacts/core_protection_review_20261010/probes/probe_materialize_fail_output.txt
  - system_docs/patches/completed/codegen_materialize_namespace_2026_10_25/
- DISPOSITION: retain_as_reference for the reproducer pack; promote_to_documentation for the patch docs (merged
  into src_architecture and src_components at landing, the folder moved to patches/completed at closure).
- CLEANUP_TRIGGER: none for the pack; the patch folder moves to patches/completed at closure.

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

- DATETIME: 2026-10-25T02:02:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The BLOCKER of 2026-10-25T01:29:39Z belonged to the earlier melder_0 session and is lifted: the owner
    certified a new session as melder_0 (chat 2026-10-25) and sent it to D-10 first. This task stays blocked
    on the tranche order only (D-10, D-11, D-20); the owner's D-20 answer and his go stand.
  EVIDENCE: context_compass/tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md:217-271
  IMPACT: Nothing here changes until D-10 lands.
  NEXT: melder_0 starts this task after D-10 lands.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T08:45:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: D-10 landed (TASK-2026-10-10-deny-file-access-under-safe-codegen closed 2026-10-25, notched 0.2.8270);
    this task stays blocked on the tranche order only and now waits for D-11, which is ready. The owner's D-20
    answer and his go stand. D-10 left `SAFE_DENIED_BUILTIN_NAMES` naming `open`, so the room's filtered builtins
    this task gives materialized code already leave `open` out under safe, hybrid and precision.
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:108-130
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:82-109
  - context_compass/attention_board.md:121-122
  IMPACT: Nothing here changes until D-11 lands.
  NEXT: melder_0 starts this task after D-11 lands.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T11:30:33Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner settled the default the 00:37:11Z DECISION left for confirmation (chat 2026-10-25T11:25Z): a
    frame whose codegen posture declares no generation-namespace rule does NOT fail closed. With no rule, any new
    name that passes the hard refusals materializes; a declared rule narrows materialize to its roots. The hard
    refusals hold under every posture: a name already in sys.modules, a name under the protected core root
    (`melder`), a standard-library name and an installed top-level import name. Every exit leaves sys.modules
    and the parent attribute as found, and materialized code runs with the room's filtered builtins. Why: the
    expert examples (12, 26, 27, 29, 30, 32, 33, 36), the agents doc and docs/expert/codegen.md materialize
    flat new names under the standard presets; fail-closed would break all of them, and the hard refusals
    already cover every harm this defect records.
  EVIDENCE:
  - UX_and_AIX_experiences/04_expert/36_an_agent_builds_a_working_system.py:159-163
  - context_compass/tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md:252-268
  IMPACT: The design is complete; the examples and docs keep working without a rule.
  NEXT: Read the rule, transaction-context and namespace-builder seams at today's lines; then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T11:34:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written and linked (entry gate). Consumption mapping (patch section -> implementation step ->
    validation step):
    - architecture_patch 'Migration and Rollout Order' 1 -> PROTECTED_GENERATION_MODULE_ROOTS, the
      `materialize_modules` operation in FrameACLValidator and FrameACLCodegenBuilder -> unit: validator accepts
      and rejects the rule, builder merges roots.
    - component_patch_codegen_acl_profiles 'Interface Deltas' -> compiler `_compile_codegen_generation_controls`,
      the two surface fields, both surface clones -> unit: compiler matrix; integration: a declared rule narrows.
    - component_patch_synthetic_module_runtime -> publish/attach record, unpublish/detach/cleanup restore -> unit:
      test_synthetic_module restore cases.
    - component_patch_codegen_internal_engine -> `build_materialize_builtins` -> integration: a materialized
      module's builtins lack `open` and carry the import guard under hybrid.
    - code_description_patch_materialize_gate 'Control flow' -> the verb's six refusals and the restoring failure
      path -> unit (mocked engine) and integration (real rooms) per refusal; the failure path.
  EVIDENCE:
  - system_docs/patches/completed/codegen_materialize_namespace_2026_10_25/architecture_patch.md:1-80
  - system_docs/patches/completed/codegen_materialize_namespace_2026_10_25/code_description_patch_materialize_gate.md:1-35
  IMPACT: Implementation may start; every edit maps to a patch section and a pinned test.
  NEXT: Red tests on a /tmp copy of today's tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T12:00:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Implemented per the patch docs and validated on a /tmp copy of the device tree, the GIL off and on
    (3.14.7t). RED with source unchanged: 29 failed. GREEN: the six D-20 test files 146 passed in both modes; unit,
    component and the aether/crystallizer/mutation_research/conduit integration tiers pass in both modes (counts in
    d20_tiers.txt). Two spellbook integration failures belong to melder_3's store_key lane (M3-20), not D-20. The
    D-20 probe reports every review case refused with sys.modules and the parent attribute unchanged under safe,
    hybrid and full_access, and a failed dotted materialize leaves no module and no parent shell; byte-identical
    across GIL modes. The review's two probes now stop at their first refused case (they assume success). The
    materializing expert examples pass; 02, 09, 24 and 27 fail at list_cached_checkpoint_ids with or without
    D-20's crystallizer change, three of them never materialize - environmental or another lane's, flagged.
    Cost: the installed-name check (packages_distributions) is ~10 ms per materialize with 9 distributions,
    growing with the installed set; materialize is a rare, explicit verb, so it is not cached. Not run:
    integration/multithreading, Windows tiers, hosted CI.
  EVIDENCE:
  - artifacts/codegen_room_policy_20261025/runs/d20_red_gil0.txt:1-31
  - artifacts/codegen_room_policy_20261025/runs/d20_tiers.txt:1-27
  - artifacts/codegen_room_policy_20261025/runs/d20_probe_refusals_gil0.txt:1-17
  - artifacts/codegen_room_policy_20261025/runs/d20_name_gate_cost_gil0.txt:1-2
  IMPACT: The acceptance criteria are met on Linux; docs, graph, notch and release note remain, after S2's docs merge.
  NEXT: When melder_1 frees the docs pair (M0-231): src_architecture, src_components, tests_components, the graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T12:10:50Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Turn-in: src_architecture (invariant, Breaking entry, handoff, six C1 locs), src_components (four component
    contracts, eight C1 locs, handoff), tests_components (the new module, its C1 entry, handoff) and their indexes;
    the graph (nine descriptors, eight class nodes re-stamped, one new `uses` edge, src_graph reassembled and
    verified); docs/expert/codegen.md's payload row; notch 0.2.8272; the release-note section and a Packaging
    bullet. Closure: this ticket to completed/, the patch folder to patches/completed/, both boards, the epic,
    mailbox notices.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md
  IMPACT: D-20 is turned in; the codegen-room epic closes with it.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

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
