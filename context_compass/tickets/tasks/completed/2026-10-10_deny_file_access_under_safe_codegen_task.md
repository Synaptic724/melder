# Task: Make the safe codegen profile deny file access through open() (defect D-10)

- Completed: 2026-10-25T08:42:12Z
- Summary: Room code under the safe, hybrid and precision codegen profiles - and under the engine's no-projection
  default - is refused `open` (called or only named; gone from the room's runtime builtins), and `pathlib` is a
  permissive-only import root (the owner's D2 and B); every profile's file posture is pinned by tests and stated in
  its docstring. Notched 0.2.8270; release-note section "Codegen rooms under the safe, hybrid and precision profiles
  refuse `open`". Tests green, the GIL off and on, on Linux and - the four D-10 test files - on the owner's Windows
  machine; hosted CI Not run. Rebuild last, after the closure.

## Metadata
- Task ID: TASK-2026-10-10-deny-file-access-under-safe-codegen
- Story: none; parent EPIC-2026-10-25-codegen_room_policy_defects (defect found by
  TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-25T09:35:56Z

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

- from_state: in_progress
- to_state: done
- transition_reason: the EXIT_GATE is met but for the rebuild, which the turn-in order runs after this closure:
  the acceptance criteria pass with the GIL off and on and the strict xfail marker is gone because its test passes
  (Notes of 2026-10-25T02:27:56Z, 08:15:05Z and 08:30:27Z); the graph (08:35:38Z), the notch 0.2.8270 and the
  release-note entry (08:38:11Z) and the NOTICEs (08:39:10Z) are in. Closed on the owner's direction (chat
  2026-10-25): "yeah do that stuff" for the plan that ended in this closure, then "focus on B".

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
- [x] Notch (0.2.8270); the asset and bundle rebuild follows this closure, last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Acceptance Criteria
- [x] Under `safe`, code calling `open(path, 'w')` is refused at validation with a message naming `open`, and the file
      is not created (`test_safe_profile_refuses_writing_files` passes without its xfail marker).
- [x] Under `safe`, `open(path).read()` is refused the same way, and `f = open` followed by `f(path, 'w')` is refused
      (name resolution, because `open` is no longer an available builtin).
- [x] `open` is absent from the runtime `__builtins__` of a safe room, so a form static validation misses still fails.
- [x] Every other profile's file posture is pinned by a symptom-named test (refused or documented as allowed) for
      `open`, `io.open`, `os.open` and pathlib writes, per the owner's answer.
- [x] The profile docstrings state what each posture allows for files; the release note carries a Breaking change
      entry for code that used `open` in a safe room; the defect is recorded as closed in src_architecture.
- [x] Existing codegen tiers pass with the GIL off; Windows tiers and hosted CI are reported Not run until seen.

## Deliverables
- The deny-list change, its regressions and the documentation updates.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY; tests: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`,
  `tests/integration/melder/aether/test_codegen_system_integration_matrix.py`, the codegen unit tests.

## Validation
- Run, on /tmp copies of the working tree, Python 3.14.7t: red first - the 18 predicted failures (Note of
  2026-10-25T02:16:35Z) and option B's two (08:08:18Z); green - the codegen tiers, the GIL off and on, and the
  whole suite with the GIL off, at the fix (02:27:56Z) and under B (08:15:05Z), whose one unit failure was
  melder_1's notch-to-rebuild window, not this change; the reproducer, the GIL off and on, and the UX lessons
  (08:30:27Z), whose one failing probe fails the same way before any D-10 change.
- Run on Windows by the owner (chat, 2026-10-25T09:35Z; Note of 2026-10-25T09:35:56Z): the four D-10 test files in
  `.venv_new`, the GIL off and on - 219 passed and 4 xfailed each, as on Linux.
- Not run: the rest of the Windows tiers and hosted CI (the owner's runs); coverage was not measured.
- Recommended commands:
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/integration/melder/aether/test_codegen_core_boundary_integration.py`
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/unit/melder/nexus tests/integration/melder/aether`

## Risks / Rollback Notes
- Room code that legitimately used `open` under safe or hybrid stops working (Breaking). Rollback is reverting the
  deny-list change; no persisted state is involved.
- Denying names in-process is defence in depth, not isolation (contract C6.1); do not describe the fix as protection.

## Applicable Anti-Patterns
- [x] No implementation before the posture question is answered.
- [x] No claim that the fix protects files from agent code (C6.4 wording rule).
- [x] No closure without the xfail marker removed by a passing test and board sync.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (the owner directed the landing and the closure in
      chat, 2026-10-25; the walkthrough is in the session report)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true (the reproducer lives in the review's evidence pack)
- ARTIFACT_PATHS:
  - artifacts/core_protection_review_20261010/probes/codegen_probe.py
  - artifacts/core_protection_review_20261010/probes/codegen_probe_output.txt
  - system_docs/patches/completed/codegen_open_builtin_posture_2026_10_25/architecture_patch.md
  - system_docs/patches/completed/codegen_open_builtin_posture_2026_10_25/component_patch_codegen_acl_profiles.md
  - system_docs/patches/completed/codegen_open_builtin_posture_2026_10_25/component_patch_codegen_internal_engine.md
    (the three patch docs moved from patches/active/ at closure)
  - artifacts/codegen_room_policy_20261025/runs/ and scripts/ (this task's d10_* runs and scripts; the epic's
    folder, kept with it)
- DISPOSITION: retain_as_reference (the review's probe pack); promote_to_documentation (the patch docs:
  merged into src_components and src_architecture at closure, the folder moved to patches/completed/)
- CLEANUP_TRIGGER: applied at closure: the review's probe pack stays with the review; the patch docs are promoted
  into src_architecture, src_components and tests_components and their folder moved to
  system_docs/patches/completed/; this task's runs and scripts stay in the epic's folder.

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

- DATETIME: 2026-10-25T08:08:18Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Option B red first, on a fresh /tmp copy (option-B tests, src unchanged), Python 3.14.7t, the GIL off: the
    hybrid pathlib-write row (now expecting "Import root 'pathlib' is not allowed") and the new unit pin
    `test_frame_acl_compiler_admits_pathlib_only_under_the_permissive_import_list[hybrid]` fail - hybrid's compiled
    allowed roots still hold "pathlib" - and the other 8 cases pass (safe, hybrid+precision, permissive,
    permissive+precision, full_access). The patch docs recorded B first (script d10_patch_docs_decision_b.py).
  EVIDENCE:
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_red_gil0.txt:1-27
  - tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py:313-362
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:402-434
  IMPACT: The two tests fail for exactly the posture B changes, so they can judge the move.
  NEXT: Move "pathlib" to the permissive extras and fix hybrid's docstring; rerun the tiers.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T08:15:05Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Option B green on the /tmp copy, Python 3.14.7t. "pathlib" moved from the common roots to the permissive
    extras; hybrid's docstring says `io`, `os` and `pathlib` are permissive-only roots; the safe and hybrid "Files:"
    lines no longer say "no file access" (they name the routes refused - a claim beyond the pinned routes would read
    as protection, C6.4) and the module docstring says the three are permissive extras. Codegen tiers (35 unit
    files, component and integration aether): 2980 passed, 5 xfailed, the GIL off and on - D-11's four and the
    pre-existing component xfail. Whole suite, GIL off: component+integration 4767 passed, 29 skipped, 10 xfailed,
    2 xpassed (all pre-existing markers); unit chunk A 6323 passed, 3 skipped, 7 xfailed; experimentation 250
    passed, 4 skipped; unit chunk B 3664 passed and 1 failed - `test_generated_build_assets_are_stamped_for_the_live_version`,
    because melder_1 notched 0.2.8269 (M1-64, consumed here) while the copy was taken and its rebuild has not run;
    it reads the assets' stamp, not this change, and passes once a rebuild stamps the live version. M1-64:
    melder_1 took 0.2.8269 for STORY-2026-10-25-probe_and_purge_reach_every_version and rebuilds at its closure,
    so this task notches above it and retags its docs from 0.2.8269.
  EVIDENCE:
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_fix_tiers_gil0.txt:1-16
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_fix_tiers_gil1.txt:1-16
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_suite_component_integration_gil0.txt:1-20
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_suite_unit_a_gil0.txt:1-5
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_suite_unit_b_gil0.txt:1-32
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_suite_experimentation_gil0.txt:1-5
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:25-66
  IMPACT: B holds across the suite; the one failure is the notch-to-rebuild window of another lane.
  NEXT: The codegen lessons (UX expert examples) on the copy, the probe rerun, then the docs' B sentences.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:30:27Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Option B's remaining checks and its docs, on the /tmp copy, Python 3.14.7t. The codegen probe reports
    hybrid's pathlib write refused ("Import root 'pathlib' is not allowed in this codegen mode.") beside its `open`
    refusals, and every other row as at the fix, the GIL off and on (the GIL-on output differs only by the GIL
    warning). The UX lessons (expert examples and probes, outside CI): 84 passed, 1 failed -
    `test_probe_two_visible_spells_may_not_share_a_name`, which fails the same way on the 0.2.8267 tree before any
    D-10 change, so it is a stale probe and not this change. The docs carry B (src_architecture's invariant and
    Breaking entry, src_components' file-posture block, tests_components' bullet), every D-10 tag reads 0.2.8270 -
    the next free number above melder_1's 0.2.8269 (M1-64) - and the three indexes check current. The owner's
    commit 1dd4470e7 holds the pre-B D-10 work; the working tree adds B, the retag and what follows.
  EVIDENCE:
  - context_compass/artifacts/codegen_room_policy_20261025/runs/codegen_probe_d10_b_gil0.txt:1-29
  - context_compass/artifacts/codegen_room_policy_20261025/runs/codegen_probe_d10_b_gil1.txt:1-33
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_ux_expert_gil0.txt:1-28
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_b_ux_probe_baseline_gil0.txt:1-8
  - context_compass/system_docs/src_architecture.md:1075-1101
  - context_compass/system_docs/src_architecture.md:2219-2229
  - context_compass/system_docs/src_components.md:2786-2799
  - context_compass/system_docs/tests_components.md:1728-1736
  IMPACT: Acceptance criteria 1-4 hold under B and the docs match the code; left are the graph, the notch, the
    release note, the NOTICE, closure and the rebuild.
  NEXT: Refresh the seven codegen graph descriptors - authored fields checked, each node accepted only after its
    source is re-read - and reassemble the graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:35:38Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The graph carries D-10. The extractor ran into a mirror (the whole tree is walked, other lanes' files
    included) and only the seven descriptors came back, each refused unless its authored fields equalled the
    repository's (d10_graph_descriptors.py). Prose brought to the source, every file read in full first: the
    import-set module states `open` on the shared deny tuple and `io`/`os`/`pathlib` as permissive extras (its
    first responsibility named a "safe" import-root set; safe has imports off); each preset class states its file
    posture; the permissive class's role and second responsibility said it denies mutation and unsafe reflection
    while its build() allows both - corrected; CodegenSystem states the no-projection safe posture and gains an
    authored `uses` edge to the import-set module; safe_profile's `uses` edge now names the denied-builtin tuple.
    Twelve nodes accepted with graph_walker (the six classes, CodegenSystem and the five module nodes, all
    SEMANTICS_STALE before), the seven files normalized to the extractor's format, and the graph reassembled:
    1230 nodes, 1420 edges, its index current.
  EVIDENCE:
  - context_compass/artifacts/codegen_room_policy_20261025/scripts/d10_graph_descriptors.py:1-183
  - context_compass/system_docs/src_graph.md:20724-20747
  - context_compass/system_docs/src_graph.md:23081-23152
  IMPACT: The node-level map of the codegen ACL now says what the code does; the notch is next.
  NEXT: Read `__version__`, take the next number (0.2.8270 if it is still 0.2.8269), update the release-note header.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:38:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Notched 0.2.8270: `__version__` read 0.2.8269 (melder_1's) at landing and now reads 0.2.8270, the number
    every D-10 tag already carries. The running note's header reads 0.2.8270; it gains the section "Codegen rooms
    under the safe, hybrid and precision profiles refuse `open`" (the Breaking change for `open` under safe,
    hybrid and precision - the no-projection default included - and for hybrid's `import pathlib`, with the
    refusal texts, the remedy - run file code under permissive or full_access - and what stays the same) and one
    Packaging bullet before the rebuild line, which now names 0.2.8270; every other bullet, melder_2's included,
    stands as it was.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-1
  - release_docs/next_version_release.md:177-205
  - release_docs/next_version_release.md:252-257
  - context_compass/artifacts/codegen_room_policy_20261025/scripts/d10_release_note.py:1-90
  IMPACT: The user-facing record of the change is in the running note under the version it lands in.
  NEXT: NOTICE the other agents (0.2.8270 taken), then close the task and sync the boards; the rebuild runs last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:39:10Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M3-13 (melder_3's NOTICE, 2026-10-25T08:37:18Z, consumed here): melder_3 added an untracked component test
    module (TASK-2026-10-25-rebind_while_old_objects_are_alive_tests, tests only, no notch) and edited the tests
    pair (tests_components and tests_architecture, both indexes regenerated); it rebuilds after its own closure.
    For this task: the llm bundles are built and checked with --include-untracked, and tests_components is
    re-read before any further edit - this task's bullet survives the edit, moved to lines 1739-1747, and its
    index checks current. M0-225 to M0-227 told melder_1, melder_2 and melder_3 that this task took 0.2.8270.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-25_rebind_while_old_objects_are_alive_tests_task.md:1-16
  - context_compass/system_docs/tests_components.md:1739-1747
  IMPACT: The rebuild at the end of this task includes melder_3's untracked test module; no edit of mine collides.
  NEXT: Close the task: completion summary, criteria, move to completed/, board and artifact sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T08:46:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Closed. Acceptance: the owner's direction (chat 2026-10-25), "yeah do that stuff" for the plan that ended in
    this closure, then "focus on B". The ticket is in tickets/tasks/completed/ with its completion summary, every
    criterion checked and the validation record (Windows tiers and hosted CI Not run). Boards: the active row and its
    detail entry are gone, a closed anchor is added and the oldest dropped (12 kept); D-11's row is ready with no
    blocker and D-20's waits on D-11, both tickets noted. Artifacts: the reproducer row is retained under the
    completed path; the three patch docs, marked merged, moved to system_docs/patches/completed/ and their row is
    cleared as promote_to_documentation. The epic records the landing. Only the rebuild is left, and it runs last.
  EVIDENCE:
  - context_compass/attention_board.md:121-122
  - context_compass/artifact_board.md:69-69
  - context_compass/artifact_board.md:108-108
  - context_compass/tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md:1-12
  IMPACT: The task is turned in; the next lane (D-11) routes cleanly.
  NEXT: Rebuild the assets and the bundles from the repository root, both with --check.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T09:07:48Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The rebuild ran last, from the repository root on Python 3.14.7t. The first asset run wrote the agent
    documentation and bind-guard manifests and stopped at the system documents, whose builder clears its stale
    payloads with unlink, which the connected folder refused; the owner granted deletion for this session's folder
    (asked once), and the rerun wrote all three assets at v0.2.8270 and its `--check` printed OK for each (key
    match). The bundles, built with --include-untracked (melder_3's untracked test module, M3-13): src 585, tests
    1154 and other 418 files, and `--check --include-untracked` printed OK for all three. No .git/index.lock left.
    These records are outside both builds (context_compass/ is neither ingested by the assets beyond its
    system_docs nor bundled), so the checks stay green after this note.
  EVIDENCE: context_compass/artifacts/codegen_room_policy_20261025/runs/d10_rebuild_0_2_8270.txt:1-31
  IMPACT: D-10 is fully turned in at 0.2.8270: code, tests, docs, graph, notch, release note, records and assets.
  NEXT: None for D-10; the epic's next lane is D-11, ready.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T09:19:17Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The final tree, after the rebuild, on a fresh /tmp copy, Python 3.14.7t with the GIL off: the codegen tiers
    (35 unit files, component and integration aether) 2986 passed and 9 xfailed - D-11's four, the pre-existing
    component xfail and the four strict xfails of melder_3's new rebind module, whose controls account for the
    added passes - and test_package_version_metadata.py 4 passed, so the stamp test that failed in the option-B
    unit chunk (the window before melder_1's rebuild) passes at 0.2.8270.
  EVIDENCE:
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_final_tiers_gil0.txt:1-17
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_final_version_metadata_gil0.txt:1-5
  IMPACT: The turned-in tree is green on the tiers this task changed, with the version and assets it shipped.
  NEXT: None for D-10.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T09:35:56Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Windows, run by the owner on his machine and pasted in chat at 2026-10-25T09:35Z: the four test files D-10
    changed (the frame-ACL codegen profiles and the codegen system and namespace unit matrices, and the codegen
    core-boundary integration module), in `.venv_new` (CPython 3.14 free-threaded, melder editable from the working
    tree at 0.2.8270), 219 passed and 4 xfailed with the GIL off and 219 passed and 4 xfailed with it on - the same
    counts as on Linux; the 4 are D-11's strict xfails and the GIL-on run's one warning is Melder's GIL-enabled
    UserWarning. The ticket's Windows "Not run" becomes this run for the D-10 files; hosted CI stays Not run.
  EVIDENCE:
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_windows_owner_gil0.txt:1-10
  - context_compass/artifacts/codegen_room_policy_20261025/runs/d10_windows_owner_gil1.txt:1-14
  IMPACT: D-10's file posture holds on Windows as on Linux, the GIL off and on.
  NEXT: None for D-10.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Closed 2026-10-25, notched 0.2.8270 (release-note section "Codegen rooms under the safe, hybrid and precision
profiles refuse `open`"). Delivered: `open` is on `SAFE_DENIED_BUILTIN_NAMES`, the tuple safe, hybrid and
precision share, so their room code is refused when it calls or names `open` and finds no `open` in its runtime
builtins; the engine's no-projection default reads that tuple instead of a copy; `pathlib` is a permissive extra,
so hybrid refuses `import pathlib` (the owner's D2 and B); each preset's docstring states its file posture and
symptom-named tests pin every profile's posture for `open`, `io.open`, `os.open` and pathlib writes. Evidence: the
re-measure (Notes of 2026-10-25T00:23:47Z), the decisions (00:37:11Z, 08:05:21Z), the patch docs and red runs
(02:11:05Z, 02:16:35Z, 08:08:18Z), the fix and green runs (02:27:56Z, 08:15:05Z, 08:30:27Z), the documents
(02:59:13Z), the graph (08:35:38Z), the notch and release note (08:38:11Z), the NOTICEs (08:39:10Z) and this
closure. The pre-B work is in the owner's commit 1dd4470e7; B, the retag, the graph, the notch, the release note,
these records and the moved patch folder are in the working tree for his next commit. Not run: hosted CI and the
rest of the Windows tiers (the owner ran the four D-10 files, the GIL off and on: 219 passed, 4 xfailed each).
Open: none for D-10; the UX probe test_probe_two_visible_spells_may_not_share_a_name fails on 0.2.8267 as well
(stale, outside CI). The rebuild ran last: assets and bundles OK at 0.2.8270 (MEASURE of 2026-10-25T09:07:48Z).
Next for the epic: D-11, ready.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
