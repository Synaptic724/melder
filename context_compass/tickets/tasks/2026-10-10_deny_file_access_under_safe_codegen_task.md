# Task: Make the safe codegen profile deny file access through open() (defect D-10)

## Metadata
- Task ID: TASK-2026-10-10-deny-file-access-under-safe-codegen
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
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24), "focus on 2 and 3 make an epic for each and investigate them",
  scheduled it under EPIC-2026-10-25-codegen_room_policy_defects; melder_0 re-measures it on 0.2.8267
  and puts the posture question (D2) to the owner.

## Steps / Checklist
- [x] Re-measure on 0.2.8267 (EPIC-2026-10-25-codegen_room_policy_defects): rerun the reproducer
      and the strict xfail, the GIL off and on; read the cited code at today's lines; record MEASURE
      and FACT notes; put the posture question (D2) to the owner.
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

- DATETIME: 2026-10-25T00:16:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Scheduled under EPIC-2026-10-25-codegen_room_policy_defects at the owner's ask (chat 2026-10-24),
    "focus on 2 and 3 make an epic for each and investigate them".
    The re-measure, on a /tmp copy of the 0.2.8267 tree, the GIL off and on: (1) codegen_probe.py, open-write and
    open-read of a core file under the five postures; (2) the strict xfail test_safe_profile_refuses_writing_files;
    (3) a read at today's lines of the safe deny list and the profiles that reuse it, the builtins strategy and the
    builtin-policy and name-resolution strategies; (4) the file routes the acceptance criteria name (`open`,
    `io.open`, `os.open`, pathlib writes) probed under each profile, so the posture question (D2) is put to the
    owner with each profile's answer today.
  EVIDENCE:
  - context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe.py:1-60
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:136-166
  IMPACT: The owner decides D2 on today's postures, not on the 2026-10-10 ones.
  NEXT: Copy the 0.2.8267 tree to /tmp and run the probe, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:23:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Re-measured on a /tmp copy of the 0.2.8267 working tree (copied from the device checkout at git 9f240166f),
    the GIL off and on, Python 3.14.7 free-threaded. codegen_probe.py: under all five postures (safe, hybrid,
    hybrid+precision, permissive, full_access) an `open(path, 'w').write(...)` is accepted and the file is
    written, and `open(<core .py>).read()` is accepted and returns the file (74042 chars of bind.py now, where
    it was 64109 at 2026-10-10 because bind.py grew; the acceptance is unchanged). pathlib-write, import-melder
    and import-subprocess match the 2026-10-10 run exactly. The GIL-on output is byte-identical to the GIL-off
    run. The strict xfail test_safe_profile_refuses_writing_files still XFAILs (pytest: 16 passed, 5 xfailed,
    both GIL modes). So D-10 reproduces unchanged at 0.2.8267.
  EVIDENCE:
  - artifacts/codegen_room_policy_20261025/runs/codegen_probe_0_2_8267_gil0.txt:1-28
  - artifacts/codegen_room_policy_20261025/runs/codegen_probe_0_2_8267_gil1.txt:1-28
  - artifacts/codegen_room_policy_20261025/runs/codegen_tests_0_2_8267_gil0.txt:1-40
  IMPACT: The recorded symptom holds on today's tree, so the owner's D2 decision rests on current behaviour.
  NEXT: Confirm the cause at today's lines (next note), then put D2 to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:23:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The 2026-10-10 cause holds at 0.2.8267, read at today's lines. `SAFE_DENIED_BUILTIN_NAMES` still omits
    `open`, and `HYBRID_DENIED_BUILTIN_NAMES` and `PRECISION_DENIED_BUILTIN_NAMES` are still that same tuple.
    The safe profile builds its one `builtin_names` deny rule from that tuple, so `open` is on no deny list; the
    runtime builtins are `vars(builtins)` minus the denied names (so `open` stays in `__builtins__`); and the
    static builtin gate refuses only an `ast.Call` whose `func` is an `ast.Name` in the denied set, so a call to
    `open` is never refused and `f = open; f(...)` would not be either. imports being off under safe stops the
    `import io`/`pathlib` routes, not `open` itself. The posture question (D2) is unchanged: deny `open` under
    safe, and whether hybrid and precision (which reuse the tuple) too.
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:83-99
  - src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:106-124
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:100-108
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:103-127
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:252-265
  IMPACT: The fix is still a deny-list change plus a pinned per-profile file matrix, after D2.
  NEXT: DECISION_REQUEST to the owner: D2 (deny `open` under safe; hybrid and precision too?).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:37:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's decision on D2 (chat 2026-10-25, answering the decision request): deny `open` under safe,
    hybrid and precision; permissive and full_access stay documented open postures - the recommended option.
    The three share one tuple today (`SAFE_DENIED_BUILTIN_NAMES`, which hybrid and precision alias), so the
    deny-list change covers exactly them. Carried into the patch doc for the owner's confirmation: hybrid also
    allows `import pathlib` (it is on hybrid's import allow list, not precision's), and the re-measure shows a
    pathlib write accepted under hybrid; denying `open` leaves that route, so the patch doc states hybrid's
    file posture with and without pathlib on its list.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:57-60
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:210-231
  IMPACT: The fix proceeds on a decided posture; the pathlib residue is named before the patch doc, not found after.
  NEXT: On the owner's go: write the patch docs (architecture + component patch for the codegen ACL profiles).
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
investigation only. Scope unchanged: `open` reads and writes files under every codegen profile, safe included,
against safe's documented posture (Note of 2026-10-10). State: the re-measure on 0.2.8267 is planned (PLAN note);
nothing run yet. Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the
strict xfail still XFAILs. Decided 2026-10-25 (DECISION note): deny `open` under safe, hybrid and
precision; hybrid's pathlib route goes to the patch doc. Next, on the owner's go: patch docs, red
tests, the fix, notch and rebuild.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
