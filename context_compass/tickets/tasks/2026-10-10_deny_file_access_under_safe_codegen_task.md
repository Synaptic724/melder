# Task: Make the safe codegen profile deny file access through open() (defect D-10)

## Metadata
- Task ID: TASK-2026-10-10-deny-file-access-under-safe-codegen
- Story: none; parent EPIC-2026-10-25-codegen_room_policy_defects (defect found by
  TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-25T08:05:21Z

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

- from_state: blocked
- to_state: in_progress
- transition_reason: the owner certified a new session as melder_0 and directed it (chat 2026-10-25):
  "Go do the D-10 story first try that"; his go of 2026-10-25 ("go ahead and do them one by one") stands.

- from_state: in_progress
- to_state: blocked
- transition_reason: everything that can land before the notch is done (fix, tests, docs; Note of
  2026-10-25T02:59:13Z); the hybrid pathlib row, and with it the notch, release note and rebuild, waits on the
  owner's answer to the architecture patch's DECISION_REQUEST (A keep pathlib on hybrid, B move it).

- from_state: blocked
- to_state: in_progress
- transition_reason: the owner answered the pathlib question (chat 2026-10-25, "focus on B"): option B.

## Steps / Checklist
- [x] Re-measure on 0.2.8267 (EPIC-2026-10-25-codegen_room_policy_defects): rerun the reproducer
      and the strict xfail, the GIL off and on; read the cited code at today's lines; record MEASURE
      and FACT notes; put the posture question (D2) to the owner.
- [x] Owner answers the posture question; patch docs written and linked (hybrid's pathlib route put back
      to the owner in the architecture patch).
- [x] Red first: the strict xfail fails on its assertion; add the per-profile matrix cases.
- [x] Implement the deny list change and the docstrings; run the codegen unit, component and integration tiers.
- [x] Remove the strict xfail marker; update tests_components, src_components, src_architecture
      (release note at the notch).
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
  - system_docs/patches/active/codegen_open_builtin_posture_2026_10_25/architecture_patch.md
  - system_docs/patches/active/codegen_open_builtin_posture_2026_10_25/component_patch_codegen_acl_profiles.md
  - system_docs/patches/active/codegen_open_builtin_posture_2026_10_25/component_patch_codegen_internal_engine.md
- DISPOSITION: retain_as_reference (the review's probe pack); promote_to_documentation (the patch docs:
  merged into src_components and src_architecture at closure, the folder moved to patches/completed/)
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

- DATETIME: 2026-10-25T02:01:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: A new session takes the implementation as melder_0: the owner certified it (chat 2026-10-25,
    "AGENT_NAME: melder_0" and "CERTIFY: APPROVED") and directed "Go do the D-10 story first try that". The
    BLOCKER of 2026-10-25T01:29:39Z belonged to the earlier session and is lifted. The owner's D2 answer (deny
    `open` under safe, hybrid and precision; permissive and full_access stay open) and the tranche order D-10,
    D-11, D-20 stand. Order of work: patch docs first (the codegen ACL is a policy gate), then red tests, the
    fix, docstrings and system docs, the notch and release-note entry, closure, and the rebuild last.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:233-262
  - context_compass/tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md:217-271
  IMPACT: The task is in progress again on a decided posture; nothing in src/ has changed yet.
  NEXT: Read the codegen ACL code and docs at today's lines, then write the patch docs and link them here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:01:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M3-6 (melder_3's NOTICE, 2026-10-25T01:13:45Z, consumed here): src_components is at its spec
    (STORY-2026-10-24-src_components_to_spec closed; 12,642 -> 11,874 lines). Landing a change there: a file a C2
    entry names in Key Files (C1) goes into its parent C3 entry's list and the C1 map too (the map is the C3 Key
    Files union); an entry states today's rule with its version tag, no "before" or CORRECTED history; one dated
    handoff entry per lane, at the top, with the contracts changed, the unknowns and what to verify next; no path
    into context_compass in any spelling.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-24_src_components_to_spec_story.md:1-12
  IMPACT: This task's src_components update (the codegen validation and ACL entries) follows these rules.
  NEXT: Apply them at the src_components step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T02:11:05Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The engine has a second, hand-kept copy of the safe posture. When the owning Rift has no codegen
    projection for the frame a request names, `_try_get_codegen_projection` returns None (the lookup's
    ValueError for a frame the room holds no projection for is swallowed) and
    `_build_default_namespace_configuration` uses a literal deny tuple equal to `__import__` plus today's safe
    tuple, imports off. The request then validates and runs, and the public `execute_codegen` reaches it with any
    such frame name. Changing only the shared tuple would leave `open` one argument away in every codegen room.
  EVIDENCE:
  - src/melder/nexus/rift/codegen_system/codegen_system.py:404-475
  - src/melder/nexus/rift/codegen_system/codegen_system.py:510-537
  - src/melder/nexus/rift/rift.py:683-700
  - src/melder/nexus/rift/command_system/codegen_command_system.py:669-737
  IMPACT: The fix covers the default posture too; it reads the safe tuple so the two cannot drift again.
  NEXT: Patch docs carry both changes (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T02:11:05Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written and linked (patch codegen_open_builtin_posture_2026_10_25: architecture patch and
    two component patches; no code_description patch - the gate pipeline, texts, order and locks are
    unchanged). Consumption mapping, patch section -> implementation -> validation:
    (1) architecture Migration 1 / both Validation sections -> red tests: per-posture file matrix and the
    no-projection request (integration), compiled deny lists per preset (unit), default posture (unit) -> run
    on a /tmp copy, GIL off, expect the safe/hybrid/precision/default `open` cases red;
    (2) acl profiles Target boundary -> "open" into `SAFE_DENIED_BUILTIN_NAMES` -> those cases green;
    (3) engine Target boundary -> default reads `("__import__",) + SAFE_DENIED_BUILTIN_NAMES` -> default cases
    green; (4) docstrings of the five presets and the default -> re-read; (5) strict xfail marker removed ->
    its test passes; (6) docs, release note, notch, closure, rebuild -> the two `--check` runs print OK.
    Open: hybrid's pathlib route (architecture patch DECISION_REQUEST, recommendation B) - its test waits on
    the owner; everything else proceeds.
  EVIDENCE:
  - context_compass/system_docs/patches/active/codegen_open_builtin_posture_2026_10_25/architecture_patch.md:1-103
  - context_compass/system_docs/patches/active/codegen_open_builtin_posture_2026_10_25/component_patch_codegen_acl_profiles.md:1-73
  - context_compass/system_docs/patches/active/codegen_open_builtin_posture_2026_10_25/component_patch_codegen_internal_engine.md:1-70
  IMPACT: The patch gate is met for the decided part; src/ edits follow the mapping.
  NEXT: Write the red tests and run them on a /tmp copy, GIL off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:16:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red first, on a /tmp copy with the new tests and no src change, Python 3.14.7t, the GIL off: 18 failed,
    32 passed, 5 xfailed - exactly the predicted cases. Failing: `open` write and read and a bare `open` reference
    under safe, hybrid and hybrid+precision (9, each accepted); the no-projection request in a safe and in a
    full_access room (2: accepted and the file written, so the default path is live and ignores the linked
    frame's profile); the compiled deny list for safe, default, hybrid, hybrid+precision and permissive+precision
    (5); the default posture (1); the runtime builtins of the safe tuple (1). Passing as pinned: permissive and
    full_access read and write with `open`; `io.open` and `os.open` refused under safe ("Import statements are
    not allowed") and under hybrid and hybrid+precision ("Import root 'io'/'os' is not allowed"), run under
    permissive and full_access - the patch's UNKNOWN on those messages is resolved; pathlib as recorded (hybrid
    accepted, pending the owner). The strict xfail still XFAILs.
  EVIDENCE: context_compass/artifacts/codegen_room_policy_20261025/runs/d10_red_gil0.txt:1-43
  IMPACT: The tests fail for the defect and pass for the postures that stay; the fix can be judged by them.
  NEXT: Implement: "open" into SAFE_DENIED_BUILTIN_NAMES; the engine default reads the safe tuple; docstrings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:27:56Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Implemented per the patch mapping (steps 2-5). `SAFE_DENIED_BUILTIN_NAMES` names "open" (hybrid and
    precision alias it), with a comment saying what it is for and that it is policy, not isolation; the engine's
    no-projection default reads `("__import__",) + SAFE_DENIED_BUILTIN_NAMES` (the literal copy is gone) and its
    docstring states both postures; the five preset docstrings gain a "Files:" line (hybrid states pathlib as it
    is today, pending the owner). The permissive class docstring said it denies mutation and unsafe reflection
    while its build() allows both - provably wrong in the paragraph being edited, so corrected. The strict xfail
    marker is removed (its test passes) and the test module docstring now lists three kinds of test.
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:83-105
  - src/melder/nexus/rift/codegen_system/codegen_system.py:407-483
  - src/melder/nexus/acl/configurations/profiles/codegen/permissive_profile.py:14-21
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:140-151
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:202-455
  IMPACT: The decided part of D-10 is in the tree; only hybrid's pathlib posture is open.
  NEXT: Validate (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:27:56Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green on a /tmp copy with the fix, Python 3.14.7t. Codegen tiers (35 codegen/ACL unit files,
    tests/component/melder/aether, tests/integration/melder/aether): 2938 passed, 5 xfailed with the GIL off
    and on - the xfails are D-11's four and one pre-existing component xfail; D-10's is gone. Whole suite, GIL
    off, in chunks: component+integration 4708 passed, 49 skipped, 9 xfailed, 3 xpassed (the three are
    pre-existing non-strict xfails - two spellbook "Fault B" cases and an intermittent notch race); unit
    6247 + 3665 passed (3 skipped, 7 xfailed); experimentation 250 passed, 4 skipped. A first unit run failed 5
    tests only because the copy lacked .readthedocs.yaml, codecov.yml, benchmarks/ and context_compass/system_docs
    (120 passed once copied); docs/ was not copied. The reproducer now reports open-write and open-read-core
    refused ("Builtin 'open' is not allowed in this codegen mode.") under safe, hybrid and hybrid+precision,
    pathlib-write still accepted under hybrid, everything else as at 0.2.8267; the GIL-on run is identical but
    for the GIL warning. Windows and hosted CI: Not run.
  EVIDENCE:
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_fix_tiers_gil0.txt:1-15
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_fix_tiers_gil1.txt:1-15
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_fix_suite_component_integration_gil0.txt:1-24
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_fix_suite_unit_a_gil0.txt:1-5
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_fix_suite_unit_b_gil0.txt:1-4
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_fix_suite_experimentation_gil0.txt:1-4
  - context_compass/artifacts/codegen_room_policy_20261025/runs/codegen_probe_d10_fix_gil0.txt:1-29
  - context_compass/artifacts/codegen_room_policy_20261025/runs/codegen_probe_d10_fix_gil1.txt:1-32
  IMPACT: Acceptance criteria 1-3 are met and the file-posture rows are pinned; criterion 4 waits only on
    hybrid's pathlib row (the owner's call).
  NEXT: The owner's pathlib answer; then docs, release note, notch, closure and the rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T02:41:49Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Re-onboarded after a compaction (self-certified as melder_0 on the owner's standing preference). Two
    NOTICEs consumed here. M3-10 (melder_3, 2026-10-25T02:33:01Z): melder_3 took 0.2.8268
    (TASK-2026-10-25-creations_many_disposal_docstrings, closed) and re-extracted only creations.py's graph
    descriptor, so the seven descriptors this task changed - stdlib_import_sets.py, codegen_system.py and the five
    codegen presets - still lag their source. M2-44 (melder_2, 2026-10-25T02:34:43Z): melder_2's lane
    (STORY-2026-10-25-pypi_trusted_publishing_and_provenance) edits .github/, tests/unit/github_workflows, the
    README's install lines, docs/beginner/install.md, one Packaging bullet before the running note's rebuild line
    and the tests pair, with no src and no notch, and asks who holds any of them. This task holds two: tests_components
    (the codegen core-boundary entry, its C1 map row, one handoff entry) and the running note (a Breaking section,
    a Packaging bullet, the rebuild line's version at the notch); M0-223 tells melder_2.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-25_creations_many_disposal_docstrings_task.md:1-14
  - context_compass/tickets/stories/2026-10-25_pypi_trusted_publishing_and_provenance_story.md:28-36
  - src/melder/__version__.py:12-12
  IMPACT: This task's notch is the next free number above 0.2.8268 at landing; the seven descriptors are
    re-extracted then; both shared documents take targeted edits, re-read first, so melder_2's bullet stands.
  NEXT: Repair the board row's `next`, then the src_architecture entries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:59:13Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: System docs carry the change (patch steps 6, docs part), each claim re-read against today's source:
    src_architecture - a new first operational invariant (the presets' file posture; the no-projection default
    reads the safe tuple; the compiler's deny-minus-allow rule; defence in depth, not isolation; no cache or record
    move), a Breaking (0.2.8269) failure mode, the code map's codegen_system.py remeasured (545), five sources added
    and a handoff entry; src_components - Nexus Descriptor And ACL Managers gains "Codegen presets' file posture",
    Codegen Internal Engine and its CodegenSystem C2 the safe default and its refusals, the three numeric
    citations remapped (:263, :298, :142; the citation check reports zero findings), the code map remeasured,
    the inventory line for stdlib_import_sets.py, six sources (292) and a handoff entry; tests_components - the
    codegen integration bullet (46 tests), its Key Files tag, the unit cluster's `open` bullet, the core map row
    (455), three sources and a handoff entry. All three indexes regenerated, `--check` OK. src change: a module
    docstring for stdlib_import_sets.py (documentation only), which was UNKNOWN in the inventory. Version tags say
    0.2.8269 - the next free number above melder_3's 0.2.8268; re-read `__version__` at landing and retag if it
    moved. Sentences that depend on the pathlib answer (they say hybrid admits `pathlib`): src_architecture
    1051-1052, src_components 2781-2782, tests_components 1707-1707, the hybrid docstring and the hybrid test row.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1040-1065
  - context_compass/system_docs/src_architecture.md:2168-2176
  - context_compass/system_docs/src_components.md:2691-2709
  - context_compass/system_docs/src_components.md:2770-2800
  - context_compass/system_docs/tests_components.md:1701-1710
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:1-23
  - context_compass/artifacts/codegen_room_policy_20261025/scripts/d10_src_components.py:1-200
  IMPACT: Everything but the pathlib row, the graph, the release note, the notch, closure and the rebuild is done;
    those wait on the owner's A or B (the graph and the rebuild go last either way).
  NEXT: The owner's pathlib answer; meanwhile nothing else in this task can land.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:05:21Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner answered the pathlib question (chat 2026-10-25, "yeah do that stuff", then "focus on B"):
    option B. "pathlib" moves from the common import-root list to the permissive extras, so hybrid refuses
    `import pathlib` (path arithmetic included) while permissive keeps it and precision and safe are unchanged;
    the hybrid test row flips to refused, hybrid's docstring and the three doc sentences named in the Note of
    2026-10-25T02:59:13Z follow, and the release note carries it as Breaking beside `open`. The patch docs record
    the decision before the src edit. M2-46 (melder_2's NOTICE, 2026-10-25T03:22:43Z, consumed here): its lane is
    turned in; its one Packaging bullet stands before the running note's rebuild line, the header and that line's
    version are this task's at the notch, and its tests_components entries sit above this task's.
  EVIDENCE:
  - context_compass/system_docs/patches/active/codegen_open_builtin_posture_2026_10_25/architecture_patch.md:84-95
  - context_compass/tickets/stories/completed/2026-10-25_pypi_trusted_publishing_and_provenance_story.md:1-8
  IMPACT: The last open posture is decided; the task can land.
  NEXT: Patch docs record B; then the red run of the flipped hybrid row.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Scope: `open` reads and writes files under every codegen profile, safe included, against safe's documented
posture (Note of 2026-10-10). State: in_progress, melder_0 (re-onboarded 2026-10-25T02:41:49Z after a compaction).
Decided (DECISION of 2026-10-25T00:37:11Z): deny `open` under safe, hybrid and precision. Done: patch docs
(codegen_open_builtin_posture_2026_10_25, linked); red run (18 predicted failures); the fix - "open" in
`SAFE_DENIED_BUILTIN_NAMES`, the engine's no-projection default reading that tuple, five profile docstrings, a
module docstring for stdlib_import_sets.py, the xfail marker gone; green - codegen tiers GIL off and on, the whole
suite GIL off, the reproducer (Notes of 2026-10-25T02:27:56Z); system docs - src_architecture, src_components,
tests_components and their indexes (Note of 2026-10-25T02:59:13Z). Open: hybrid's pathlib route - the owner's
call (A keep, B move pathlib to the permissive extras; recommended B). Next: on his answer (B: move pathlib, flip
the hybrid test row, the hybrid docstring and the three doc sentences that Note names, rerun the codegen tiers),
then re-extract the seven codegen graph descriptors and reassemble, notch (the next number above 0.2.8268; retag
the docs if it moved), the release-note Breaking entry, a NOTICE, closure (the patch folder to patches/completed/,
boards) and the rebuild last. Nothing is notched or rebuilt yet.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
