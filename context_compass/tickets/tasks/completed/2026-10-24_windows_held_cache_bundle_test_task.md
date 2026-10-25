# Task: A Windows-only test shows the cache save surviving a real WinError 5

- Completed: 2026-10-24T23:03:28Z
- Summary: A Windows-only test file checks the 0.2.8266 cache save against a rename Windows itself refuses. On the
  owner's machine (Python 3.14.7 free-threaded, the GIL off and on) all four tests pass and every refusal is
  [WinError 5], his MelderOps code: a hold that ends within the retries is waited out, a longer one leaves the save
  refused and logged and the meld unaffected. Tests only: no notch, no release-note entry; melder_1's rebuild took
  the file into the LLM bundles. The emulation harness and the runs are kept in the artifact folder.

## Metadata
- Task ID: TASK-2026-10-24-windows_held_cache_bundle_test
- Story: none (standalone; a follow-up of TASK-2026-10-24-cache_file_write_failure_fails_meld)
- Status: done
- Owner: Mark
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T22:24:45Z
- Updated: 2026-10-24T23:03:28Z

## Objective
The owner's ask (chat 2026-10-24, after the 0.2.8266 fix): "dude add it to my machine and see what happens I can
run whatever commands you want". The fix's tests inject the rename refusal, because Linux never refuses a rename for
sharing. This task adds a Windows-only integration test file that makes Windows refuse it for real: it holds the
bundle open with Python's open(), which on Windows does not share delete access, so a rename onto it fails as the
owner's MelderOps run failed (PermissionError [WinError 5]). On that real refusal it checks the premise (Windows
refuses the rename), a hold that ends while the save retries (the save waits it out), a hold that outlasts the
retries (the save returns False, the bundle stays as it was, no temp file is left, one WARNING) and a meld whose
save is refused (it returns its object, and a later save writes what was kept). The owner runs it on his machine;
his output is recorded here.

## Ticket Contract
- ENTRY_GATE: this task's board row; the save path and the existing refused-save tests read and recorded first.
- EXECUTION_BOUNDARY: one new test file,
  tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py; this ticket, its board
  row, artifacts/windows_held_bundle_20261024/ (the Linux emulation harness and the runs) and its artifact row. No src
  change, no notch, no release-note entry: tests only.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (completed, 0.2.8266); the backlog drafts
  identify_windows_cache_file_holder (the MelderOps holder) and document_refused_cache_save_tests (the tests map).
- EXIT_GATE: the file is collected and skipped on the VM and passes there under the emulation harness, the GIL off
  and on; the owner's Windows run recorded; the ticket closed with board and artifact sync.
- FAILURE_ESCALATION: CONFLICT when Windows does not refuse the rename while the handle is held (the fix's
  hypothesis would be wrong); DECISION_REQUEST when a refusal on the owner's machine outlasts the retries in the
  short-hold case, or any test fails there.

## Scope Boundaries
- In scope: the Windows-only test file; its emulated run on the VM; the owner's run on Windows and its record.
- Out of scope: src and the retry budget (a finding that calls for a change gets a task of its own); naming what
  held the bundle in the owner's MelderOps run (TASK-2026-10-24-identify_windows_cache_file_holder, backlog).

## State Transition Event
- from_state: in_progress (validation)
- to_state: done
- transition_reason: the EXIT_GATE is met (Notes 4-5): the file skips on the VM and passes under the emulation
  harness, the GIL off and on, and passes on the owner's Windows machine, the GIL off and on. Routine closure of the
  owner's ask (Note 1); tests only (Note 6).

## Steps / Checklist
- [x] Read the save path (`CachingSystem.emit` and its helpers) and the refused-save tests; record the PLAN.
- [x] Write the Windows-only test file and the emulation harness.
- [x] Run the file on a /tmp copy on the VM: skipped as written and passing under the harness, the GIL off and on;
      record the MEASURE.
- [x] Hand the owner the command; record his Windows output as a MEASURE.
- [x] Closure: summary, move to completed/, board and artifact sync; the tests-map entry joins the backlog draft
      document_refused_cache_save_tests.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py (four Windows-only tests).
- The VM runs (skipped; emulated) and the owner's Windows run, recorded here.

## Files / Paths Impacted
- tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py (new)
- context_compass/tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task.md
- context_compass/attention_board.md (this task's row)
- context_compass/artifact_board.md (one row)
- context_compass/artifacts/windows_held_bundle_20261024/

## Validation
- VM (Linux; Python 3.14.7 free-threaded), a /tmp copy of the working tree at 0.2.8267: as written, 4 skipped,
  the GIL off and on; under the emulation harness, 4 passed, the GIL off and on. On the 0.2.8265 copy under the
  harness tests 2-4 fail with the save's PermissionError (red before the fix). Note 4.
- Windows, the owner's machine (chat 2026-10-24): 4 passed, the GIL off and on; every refusal [WinError 5]
  (Note 5).
- Commands:
  - Windows, PowerShell, from the repository root, where <file> is
    tests\integration\melder\conduit\test_conduit_integration_windows_held_cache_bundle.py:
    `.\.venv_new\Scripts\python.exe -m pytest <file> -v -s`, then the same with `-X gil=1` before `-m`.
    `.venv_new` installs melder editable from `src`, and tests/conftest.py puts `src` first on sys.path.
  - VM: the harness's docstring
    (context_compass/artifacts/windows_held_bundle_20261024/scripts/windows_emulation_harness.py).

## Risks / Rollback Notes
- Windows may report the refusal as [WinError 32] rather than [WinError 5]; both are PermissionError, which the
  retry catches; the tests assert PermissionError and print the code.
- A scanner on the owner's machine may add refusals of its own; the short-hold test asserts at least the two it
  makes and prints every count.
- The meld test writes under the package's default cache folder, as the component tests do, and removes its frame
  folder afterwards, best-effort.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [x] No src or retry-budget change in this task; a finding that calls for one gets a task of its own.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/windows_held_bundle_20261024/scripts/
  - artifacts/windows_held_bundle_20261024/runs/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: applied at closure (Note 6): the folder is retained - the harness reruns the Windows-only
  tests' logic off Windows, beside the VM and Windows runs.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, tests and evidence; this ticket, the test
  file and the harness; 2026-10-24.
- Evidence: the Windows runs by Mark (the owner) on his machine, pasted in chat 2026-10-24 (Note 5).
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested

## Notes
- DATETIME: 2026-10-24T22:24:45Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's ask (chat 2026-10-24), answering the offer of a Windows-only test that holds the bundle open:
    "dude add it to my machine and see what happens I can run whatever commands you want". This task adds
    that test file and nothing else - tests only, so no notch and no release-note entry - and records the
    owner's run on Windows here. The fix's open HYPOTHESIS (what held the bundle in his MelderOps run) stays
    with the backlog draft identify_windows_cache_file_holder: this test makes its own holder.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:305-323
  - context_compass/tickets/tasks/backlog/2026-10-24_identify_windows_cache_file_holder_task.md:1-147
  IMPACT: The 0.2.8266 save gets checked against a refusal Windows itself raises, which the VM cannot raise.
  NEXT: Record the PLAN read from the save path and the existing refused-save tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:24:45Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Read at 0.2.8267: `emit()` writes the envelope to `<bundle>.<pid>.<thread id>.tmp` and renames it onto the
    bundle with `Path.replace` (that is `os.replace`); while `RETRY_REFUSED_RENAME` (True on win32) a
    PermissionError is retried up to `REPLACE_ATTEMPTS` (5) with sleeps of 0.01 s times the attempt number
    (0.1 s in all), then the save logs once at WARNING, removes its temp file and returns False with its
    payloads kept. The premise, UNKNOWN until test 1 runs on Windows: Python's open() there shares read and
    write but not delete, so a handle it holds on the bundle makes that rename fail as the owner's run failed.
    The file's four tests - Windows-only (skipif), marked integration, nothing injected; a spy on os.replace
    only counts and passes through - each print their refusal codes and timings for the owner's run:
    (1) a rename onto a held bundle raises PermissionError and succeeds once the handle closes;
    (2) a hold the spy releases after two refused attempts: the save returns True with the new payload;
    (3) a hold over the whole save: False after exactly REPLACE_ATTEMPTS refusals, the bundle byte-identical,
    no temp file, one WARNING; the next save after the hold writes both payloads;
    (4) a dynamic root's bundle held while a spell bound after conjure is first melded: the meld returns its
    object, its save refused REPLACE_ATTEMPTS times; after the hold a later spell's save writes both plans.
    On the VM they skip as written; a harness in this task's artifact folder runs them with the retry on and
    a rename onto a file this process holds open refused (read from /proc/self/fd), the GIL off and on.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:762-804
  - src/melder/utilities/caching_system/caching_system.py:948-1063
  - src/melder/utilities/caching_system/caching_system.py:263-271
  - tests/unit/melder/utilities/test_caching_system_refused_save.py:1-485
  - tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py:1-434
  IMPACT: Each test names what it shows on a real refusal, so the owner's output reads as the answer to his question.
  NEXT: Write the test file and the harness; run both on a /tmp copy, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:50:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M3-3 from melder_3 (NOTICE, 2026-10-24T22:40:34Z, no ACK asked): src_architecture is at its spec (its trim
    story closed, 5,739 -> 4,784 lines). A change landing there states today's rule and its mechanism only,
    puts component mechanics in the src_components entry, keeps C1 notes descriptive, adds one dated handoff
    entry per lane at the top and no path into context_compass in any spelling; src_components gets the same
    pass next (Story 2), and an agent tells melder_3 before writing it. This task writes neither document.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-24_src_architecture_trim_to_spec_story.md:1-12
  IMPACT: Nothing changes in this lane (tests only). A later lane of mine that writes src_architecture or
    src_components - a fix from the backlog drafts - follows those rules and tells melder_3 first while Story 2 runs.
  NEXT: Record the VM runs (Note 4).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T22:50:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The test file (four tests) and the Linux emulation harness are written. On a /tmp copy of the working tree
    at 0.2.8267 (Python 3.14.7 free-threaded): as written the four tests skip, the GIL off and on; under the
    harness (the retry on; a rename onto a file this process holds open refused) they pass, the GIL off and on.
    The premise was refused once and allowed on the first try after the close; the short hold saved on the third
    attempt (2 refusals, 0.031 s); the long hold returned False after 5 refusals in 0.10 s, the bundle unchanged,
    no temp file, one WARNING, and the next save wrote both payloads; the meld returned its object in 0.104 s
    through 5 refusals, the second meld saved nothing, and the later spell's save wrote the bundle with 3 plans.
    Under the same harness on the 0.2.8265 copy (before the fix) tests 2-4 fail with the PermissionError raised
    out of the save or the meld - the owner's failure - and test 1 on the REPLACE_ATTEMPTS its print reads.
    Windows: Not run.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py:347-382
  - tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py:385-443
  - tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py:446-515
  - tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py:518-594
  - context_compass/artifacts/windows_held_bundle_20261024/scripts/windows_emulation_harness.py:1-206
  - context_compass/artifacts/windows_held_bundle_20261024/runs/skipped_as_written_gil0.txt:1-16
  - context_compass/artifacts/windows_held_bundle_20261024/runs/skipped_as_written_gil1.txt:1-24
  - context_compass/artifacts/windows_held_bundle_20261024/runs/emulated_gil0.txt:1-20
  - context_compass/artifacts/windows_held_bundle_20261024/runs/emulated_gil1.txt:1-24
  - context_compass/artifacts/windows_held_bundle_20261024/runs/red_on_0_2_8265_gil0.txt:1-26
  - context_compass/artifacts/windows_held_bundle_20261024/runs/red_on_0_2_8265_gil1.txt:1-30
  IMPACT: The tests' logic holds off Windows and catches the 0.2.8265 defect. Only Windows answers the premise (does
    open() make Windows refuse the rename), which code it raises (5 or 32) and whether a scanner adds refusals.
  NEXT: Hand the owner the PowerShell command in Validation; record his output as a MEASURE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:03:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The owner's run on his Windows machine (chat 2026-10-24; .venv_new, CPython 3.14.7 free-threaded, melder
    editable from the working tree at 0.2.8267): the four tests pass, the GIL off and on (4 passed in 6.00 s and
    in 0.68 s), and every refusal is [WinError 5] (ERROR_ACCESS_DENIED), the code of his MelderOps failure. The
    premise holds: a rename onto a file Python's open() holds is refused, and allowed on the first try after the
    close. The short hold saved on the third attempt (2 refusals; 0.033 s and 0.032 s); the long hold returned
    False after 5 refusals in 0.104 s with the bundle unchanged, no temp file and one WARNING, and the next save
    wrote both payloads; the meld returned its object through 5 refusals (0.106 s and 0.105 s), the second meld
    saved nothing and the later spell's save wrote 3 plans. Nothing else refused a rename (0 beyond the holds').
  EVIDENCE:
  - context_compass/artifacts/windows_held_bundle_20261024/runs/windows_owner_gil0.txt:1-27
  - context_compass/artifacts/windows_held_bundle_20261024/runs/windows_owner_gil1.txt:1-34
  - tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py:1-594
  IMPACT: On Windows the 0.2.8266 save does what the VM's emulation showed: a holder that lets go within about 100 ms
    costs a wait of about 30 ms, a longer one a refused save with one WARNING, never a failed meld. What held the
    bundle in the MelderOps run is still unnamed (TASK-2026-10-24-identify_windows_cache_file_holder).
  NEXT: Close the task (Note 6).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T23:03:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closed: the EXIT_GATE is met - the file skips on the VM and passes there under the emulation harness, the
    GIL off and on (Note 4), and the owner's Windows run passes, the GIL off and on (Note 5). Tests only: no
    notch, no release-note entry, no rebuild here. M1-59 (melder_1's NOTICE, 2026-10-24T22:56:45Z, consumed
    here): its rebuild after the 0.2.8265 cut took the untracked file into the LLM bundles' tests corpus, every
    check OK. The artifact folder is retained: the harness reruns the tests' logic off Windows beside the runs.
    The holder draft gets the measured premise and the tests-map draft its fourth file (a FACT note each). The
    file stays untracked until the owner commits it.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-24_windows_held_cache_bundle_test_task.md:222-275
  - context_compass/tickets/tasks/completed/2026-10-24_cut_release_note_0_2_8265_task.md:1-276
  IMPACT: The lane is done; only the owner's commit of the new test file is pending.
  NEXT: None in this task; the two drafts wait for the owner's scheduling.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done (Note 6): the Windows-only test file is in tests/integration/melder/conduit/ (untracked until the owner
commits it) and passes on the owner's Windows machine, the GIL off and on, with [WinError 5] on every refusal
(Note 5); the emulation harness and the runs stay in the artifact folder. Open elsewhere, as drafts: the MelderOps
holder (TASK-2026-10-24-identify_windows_cache_file_holder) and the tests-map entries
(TASK-2026-10-24-document_refused_cache_save_tests).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
