# Task: Check dynamic imports against the codegen import policy (defect D-11)

## Metadata
- Task ID: TASK-2026-10-10-enforce-import-policy-on-dynamic-imports
- Story: none (defect found by TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-10T13:40:50Z

## Objective
Under every codegen profile that enables imports with an allow or deny list - hybrid, the precision overlay and
permissive - a `__import__(...)` call loads roots the profile denies or does not allow, because the import gate
reads import statements only. Make every import, statement or call, answer to the same compiled roots, and keep the
defect's strict xfails as the proof. full_access stays unconstrained. This is policy and defence in depth, not a
security boundary (review contract C6.1).

## Defect
- Symptom: under hybrid and hybrid+precision, `loaded = __import__('subprocess')` (also `socket`, `importlib`) is
  accepted and returns the module, although those roots are on the profile's deny list; under hybrid,
  hybrid+precision and permissive `__import__('melder')` is accepted although the allow lists leave `melder` out and
  `import melder` is refused. Under safe it is refused ("Builtin '__import__' is not allowed").
- Reproducer: `context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe2.py` and its recorded
  output `codegen_probe2_output.txt` (rerun 2026-10-10T13:33Z on this tree). Pinned regressions: the four strict
  xfails `tests/integration/melder/aether/test_codegen_core_boundary_integration.py::`
  `test_hybrid_refuses_dynamic_imports_of_its_denied_roots[None-subprocess|None-socket|None-importlib|`
  `precision-subprocess]`.
- Cause: `FrameACLCompiler._compile_codegen_builtin_controls` adds `__import__` to the denied builtins only when
  imports are disabled; `CodegenImportPolicyStrategy` inspects `Import` and `ImportFrom` nodes only; name resolution
  admits every builtin that is not denied; the reflection strategy covers `importlib.import_module` and `reload` only
  as attribute calls on a Name.
- Impact: with `subprocess` reachable, room code can run an installer or any program; with `importlib` it can import
  anything; with `melder` it reaches the core directly - in rooms whose profiles promise otherwise.

## Ticket Contract
- ENTRY_GATE: the owner selects this ticket, assigns an implementer and routes it on `attention_board.md`; patch docs
  exist (the codegen import gate is a policy gate); the design choice below is recorded as a DECISION note.
- EXECUTION_BOUNDARY: `src/melder/nexus/acl/frame_acl_compiler.py` (import and builtin controls),
  `src/melder/nexus/rift/codegen_system/validation/strategies/` (import, builtin or name strategy),
  `src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py` (a runtime import guard,
  if chosen), the codegen tests named below, src_components (codegen validation and namespace), src_architecture
  (the boundary invariant), the release note.
- DEPENDENCIES: the review contract (C6) and D2; independent of D-10 and D-20.
- EXIT_GATE: the acceptance criteria pass with the GIL off; the four strict xfail markers are deleted because the
  tests pass; notch, release note and rebuild per the contribution guide; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST if a runtime guard changes import-statement behaviour for allowed roots;
  CONFLICT if an existing test depends on `__import__` under a listed profile.

## Scope Boundaries
- In scope: `__import__` calls and the other dynamic import routes under profiles with import lists; a runtime guard
  if chosen; error messages that name the refused root.
- Out of scope: the contents of the allow and deny lists (an owner decision under D2, for example listing the
  protected core's packages as denied roots); `open` (D-10); materialize_codegen (D-20).

## Design Options (implementer proposes, owner decides)
- A, static only: deny the `__import__` name whenever the compiled posture has an allow or deny list. Simple; refused
  at validation (what the strict xfails assert); misses any route that reaches the import machinery without the name.
- B, runtime guard: replace `__builtins__['__import__']` in the room namespace with a wrapper that checks each
  import's root against the compiled roots and raises ImportError naming the root. Covers statements and calls
  alike; removing `__import__` outright is not an option, because import statements call it.
- Recommendation: A and B together - A gives the validation message, B covers the forms static analysis misses.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: opened at the hand-back of the core-protection review (owner, 2026-10-10: "Keep the
  filesystem-access and dynamic-import gaps explicitly open until fixed and verified"); parked until selected.

## Steps / Checklist
- [ ] Record the design choice; write and link patch docs.
- [ ] Red first: the four strict xfails fail on their assertion; add the cases listed below.
- [ ] Implement; run the codegen unit, component and integration tiers with the GIL off.
- [ ] Remove the strict xfail markers; update tests_components, src_components, src_architecture, release note.
- [ ] Notch, rebuild assets and llm_support last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Acceptance Criteria
- [ ] Under hybrid and hybrid+precision, `__import__` of `subprocess`, `socket` and `importlib` is refused with a
      message naming the root, and nothing is loaded (the four strict xfails pass without their marker).
- [ ] Under hybrid, hybrid+precision and permissive, `__import__('melder')` is refused, as `import melder` is today;
      under full_access it is accepted.
- [ ] `__import__` of an allowed root (for example `json` under hybrid) and ordinary import statements of allowed
      roots keep working.
- [ ] With option B, a dynamic route that static validation does not see is refused at run time with ImportError
      naming the root, pinned by its own symptom-named test.
- [ ] The release note carries a Breaking change entry for room code that used `__import__` under a listed profile;
      src_architecture records the defect as closed and the import gate as covering calls.
- [ ] Existing codegen tiers pass with the GIL off; Windows tiers and hosted CI are reported Not run until seen.

## Deliverables
- The import-policy change, its regressions and the documentation updates.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY; tests: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`,
  `tests/integration/melder/aether/test_codegen_system_integration_matrix.py`, the codegen unit tests.

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/integration/melder/aether`
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/unit/melder/nexus`

## Risks / Rollback Notes
- A runtime guard sits on every import a room makes; measure that ordinary allowed imports keep their cost.
- Rollback is reverting the compiler and strategy changes; no persisted state is involved.
- In-process import checks are defence in depth, not isolation (contract C6.1).

## Applicable Anti-Patterns
- [ ] No implementation before the design choice is recorded.
- [ ] No claim that the fix isolates agent code (C6.4 wording rule).
- [ ] No closure without the xfail markers removed by passing tests and board sync.

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
- ARTIFACTS_REQUIRED: true (the reproducer lives in the review's evidence pack)
- ARTIFACT_PATHS:
  - artifacts/core_protection_review_20261010/probes/codegen_probe2.py
  - artifacts/core_protection_review_20261010/probes/codegen_probe2_output.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none; the pack belongs to the completed review ticket.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: codegen import gate; dynamic imports from agent code
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-10T13:40:50Z
  TYPE: FACT
  CLAIM: Opened from the core-protection review's hand-back (review ticket Notes 11, 27 and 28). At 66939dfe8 the
    compiler denies `__import__` only when imports are off and the import strategy reads statements only, so
    hybrid's, precision's and permissive's roots constrain import statements, not imports. The reproducer and its
    recorded output are in the review's evidence pack; four strict xfails pin the hybrid and precision contract.
  EVIDENCE:
  - src/melder/nexus/acl/frame_acl_compiler.py:600-630
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:89-171
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:99-149
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_reflection_policy_strategy.py:148-220
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:169-206
  - context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe2_output.txt:1-19
  IMPACT: Room code under a listed profile can load subprocess, socket, importlib or melder.
  NEXT: Implementer records the design choice (A, B or both) as a DECISION note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Draft defect ticket (D-11) parked in the backlog. `__import__` bypasses the codegen import gate under hybrid, the
precision overlay and permissive. The fix makes every import answer to the compiled roots (a static refusal of the
name, a runtime guard, or both). Reproducer and four strict xfails are in place.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
