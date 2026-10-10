# Task: Refuse materializing codegen over live modules and leave sys.modules as found (defect D-20)

## Metadata
- Task ID: TASK-2026-10-10-refuse-materializing-over-live-modules
- Story: none (defect found by TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-10T13:40:50Z

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
- to_state: draft
- transition_reason: opened at the hand-back of the core-protection review (owner, 2026-10-10: "If you have
  identified another gap, document its reproducer, impact and evidence separately"); parked until selected.

## Steps / Checklist
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

## Context / Handoff Summary
Draft defect ticket (D-20) parked in the backlog. materialize_codegen replaces live core, stdlib and dependency
modules under every accepting profile and cannot restore them. The fix: a generation namespace (owner declares
where), refusal of existing, protected, stdlib and installed names, exits that leave sys.modules as found, and
probably the room's builtins for materialized code. Reproducers are in the review's evidence pack.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
