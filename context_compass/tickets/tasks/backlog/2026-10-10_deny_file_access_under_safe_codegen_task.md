# Task: Make the safe codegen profile deny file access through open() (defect D-10)

## Metadata
- Task ID: TASK-2026-10-10-deny-file-access-under-safe-codegen
- Story: none (defect found by TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-10T13:40:50Z

## Objective
Code run in a codegen room under the `safe` profile reads and writes any file the process can reach through the
`open` builtin, although the profile documents that it "denies ... writes". Make `safe` refuse `open` (static
refusal naming it, and the name absent from the runtime builtins), pin the file-access posture of every other
profile on purpose, and keep the defect's strict xfail as the proof. This is a defect fix inside the codegen ACL;
it does not make the profiles a security boundary (review contract C6.1).

## Defect
- Symptom: under `safe`, `handle = open(<path>, 'w'); handle.write('x')` is accepted by `execute_codegen` and writes
  the file; `open(<core .py>).read()` returns its full text. The same holds under hybrid, hybrid+precision,
  permissive and full_access.
- Reproducer: `context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe.py` and its recorded
  output `codegen_probe_output.txt` (rerun 2026-10-10T13:33Z on this tree: open-write accepted and written under
  all five postures; open-read-core returned 64109 characters of bind.py under all five). The pinned regression is
  the strict xfail `tests/integration/melder/aether/test_codegen_core_boundary_integration.py::`
  `test_safe_profile_refuses_writing_files`.
- Cause: `SAFE_DENIED_BUILTIN_NAMES` does not name `open` (hybrid and precision reuse the same tuple);
  `CodegenBuiltinsStrategy` builds `__builtins__` as `vars(builtins)` minus that list; the builtin strategy refuses
  only calls whose callee is a denied Name; name resolution admits every builtin that is not denied.
- Impact: any agent with a codegen room can rewrite repository or installed `.py` files the process can write,
  Melder's own included, and read any file, which contradicts the safe contract and the owner's direction that
  core changes are denied by default. Out-of-process writers are outside this ticket (contract C6.3).

## Ticket Contract
- ENTRY_GATE: the owner selects this ticket, assigns an implementer and routes it on `attention_board.md`; the owner
  answers the posture question below (D2) before implementation; patch docs exist (the codegen ACL is a policy gate).
- EXECUTION_BOUNDARY: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py` (split the shared
  denied-builtin tuple if only `safe` changes), `safe_profile.py` (and the other profile docstrings if their posture
  changes), `src/melder/nexus/acl/frame_acl_compiler.py` only if the compile step needs it; the codegen tests named
  below; src_components (codegen validation) and src_architecture (the boundary invariant); the release note.
- DEPENDENCIES: the review's governed-evolution contract (C3.2 read, C6) and D2; independent of D-11 and D-20.
- EXIT_GATE: the acceptance criteria below pass with the GIL off; the strict xfail marker is deleted because the test
  passes; notch, release note and rebuild per the contribution guide; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST if denying `open` under `safe` breaks a supported room workflow; CONFLICT if
  an existing test requires file access under `safe`.

## Scope Boundaries
- In scope: `open` under `safe`; a pinned per-profile file-access matrix (`open`, `io.open`, `os.open`, pathlib
  writes) for the posture the owner chooses; documentation of each profile's file posture.
- Out of scope: an OS sandbox, read-only mounts or a separate agent process (D2 item 4, an owner decision);
  ProtocolCrafter writers; materialize_codegen (D-20); dynamic imports (D-11).

## Decision Needed Before Implementation
- Under hybrid and precision, should `open` be denied too? Today their deny lists are the safe list, so changing the
  shared tuple changes all three. Recommendation: deny `open` under safe, hybrid and precision (agent reads of source
  go through the research reads, contract C3.2), leave permissive and full_access as documented open postures.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: opened at the hand-back of the core-protection review (owner, 2026-10-10: "Keep the
  filesystem-access and dynamic-import gaps explicitly open until fixed and verified"); parked until selected.

## Steps / Checklist
- [ ] Owner answers the posture question; patch docs written and linked.
- [ ] Red first: the strict xfail fails on its assertion; add the per-profile matrix cases.
- [ ] Implement the deny list change and the docstrings; run the codegen unit, component and integration tiers.
- [ ] Remove the strict xfail marker; update tests_components, src_components, src_architecture, release note.
- [ ] Notch, rebuild assets and llm_support last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Acceptance Criteria
- [ ] Under `safe`, code calling `open(path, 'w')` is refused at validation with a message naming `open`, and the file
      is not created (`test_safe_profile_refuses_writing_files` passes without its xfail marker).
- [ ] Under `safe`, `open(path).read()` is refused the same way, and `f = open` followed by `f(path, 'w')` is refused
      (name resolution, because `open` is no longer an available builtin).
- [ ] `open` is absent from the runtime `__builtins__` of a safe room, so a form static validation misses still fails.
- [ ] Every other profile's file posture is pinned by a symptom-named test (refused or documented as allowed) for
      `open`, `io.open`, `os.open` and pathlib writes, per the owner's answer.
- [ ] The profile docstrings state what each posture allows for files; the release note carries a Breaking change
      entry for code that used `open` in a safe room; the defect is recorded as closed in src_architecture.
- [ ] Existing codegen tiers pass with the GIL off; Windows tiers and hosted CI are reported Not run until seen.

## Deliverables
- The deny-list change, its regressions and the documentation updates.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY; tests: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`,
  `tests/integration/melder/aether/test_codegen_system_integration_matrix.py`, the codegen unit tests.

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/integration/melder/aether/test_codegen_core_boundary_integration.py`
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/unit/melder/nexus tests/integration/melder/aether`

## Risks / Rollback Notes
- Room code that legitimately used `open` under safe or hybrid stops working (Breaking). Rollback is reverting the
  deny-list change; no persisted state is involved.
- Denying names in-process is defence in depth, not isolation (contract C6.1); do not describe the fix as protection.

## Applicable Anti-Patterns
- [ ] No implementation before the posture question is answered.
- [ ] No claim that the fix protects files from agent code (C6.4 wording rule).
- [ ] No closure without the xfail marker removed by a passing test and board sync.

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
  - artifacts/core_protection_review_20261010/probes/codegen_probe.py
  - artifacts/core_protection_review_20261010/probes/codegen_probe_output.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none; the pack belongs to the completed review ticket.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: codegen builtins posture; file access from agent code
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-10T13:40:50Z
  TYPE: FACT
  CLAIM: Opened from the core-protection review's hand-back (review ticket Notes 10, 27 and 28). At 66939dfe8 no
    codegen profile denies `open`: the safe deny list is shared by hybrid and precision, the runtime builtins are
    the full builtins minus that list, and validation refuses only calls by a denied Name. The reproducer and its
    recorded output are in the review's evidence pack; the strict xfail pins the safe contract.
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:73-99
  - src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:10-48
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:82-109
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:85-127
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:136-166
  - context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe_output.txt:1-28
  IMPACT: Agent code in any codegen room can rewrite source files the process can write.
  NEXT: Owner answers the posture question; then patch docs and red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Draft defect ticket (D-10) parked in the backlog. `open` reads and writes files under every codegen profile, safe
included, against safe's documented posture. The fix is a deny-list change plus pinned per-profile file posture,
after the owner answers whether hybrid and precision deny `open` too. Reproducer and strict xfail are in place.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
