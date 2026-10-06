# Task: Deliver the 0.2.8215 wheel into MelderOps' environments and revalidate the injected-provider diagnostic

## Metadata
- Task ID: TASK-2026-09-30-deliver-0-2-8215-wheel-and-revalidate-melderops
- Epic: tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md (work package D); follows
  tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md (work package C, in review)
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-30T20:40:57Z
- Updated: 2026-09-30T21:18:29Z

- Completed: 2026-09-30T21:18:29Z
- Summary: dist/melder-0.2.8215-py3-none-any.whl built and verified (verify_wheel, smoke, sha256 cfaf55b6...4191),
  installed in priv_commandops/.venv314 over 0.2.8212 (RECORD-verified; old files in
  .venv314/_to_delete/melder-0.2.8212/) and in the VM env; the epic's diagnostic and the order matrix pass on it
  (red on 0.2.8212); MelderOps suite 6561 of 6573 passed, 3 pre-existing timing failures. No source change.

## Objective
Owner direction (chat, 2026-09-30): "so you fixed the issue and it works now? you can close that epic if its done,
please remake the wheel and install it into priv_commandops env". Build `dist/melder-0.2.8215-py3-none-any.whl`
(assets already stamped 0.2.8215), install it into `priv_commandops/.venv314` over 0.2.8212 and into the VM's
MelderOps env, then run the epic's unchanged diagnostic, command_0's order matrix and the Toolbox tests on the
installed wheel. When they pass, work package C, this task and the epic close on the owner's directive.

## Ticket Contract
- ENTRY_GATE: owner direction in chat; this board row; the PLAN note below before any write outside this ticket.
- EXECUTION_BOUNDARY: melder_private - `dist/` and this task's artifacts (no source change, no notch).
  priv_commandops - the melder files in `.venv314/Lib/site-packages` (swapped by moves and copies, no deletes); no
  source, test, pyproject or ContextCompass edits there beyond a mailbox NOTICE. VM - `$HOME/venvs/melderops314t`,
  `$HOME/melderops_copy` and scratch.
- DEPENDENCIES: work package C landed at 0.2.8215 with assets and LLM bundles rebuilt (--check OK).
- EXIT_GATE: verify_wheel passes for 0.2.8215; the files installed in `.venv314` match the wheel's RECORD and a copy
  of them imports as 0.2.8215; on the installed wheel in the VM env the epic's diagnostic and the order matrix pass
  and the Toolbox and melder_setup tests show no failure caused by Melder.
- FAILURE_ESCALATION: BLOCKER if the Windows venv cannot be updated with moves and copies (hand the owner the native
  install command); a failing diagnostic on the installed wheel reopens work package C instead of closing the epic.

## Scope Boundaries
- In scope: the objective above.
- Out of scope: MelderOps source or tests (command_0's Toolbox lane), MelderOps' `melder>=0.2.8212` floor (not
  asked), publishing, commits, a release cut. Running the Windows interpreter is not possible from the VM.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: (2026-09-30T21:18:29Z) every exit-gate item met; the
  owner's directive closes the epic once the diagnostic passes on the installed wheel. Earlier: draft ->
  in_progress below.
- from_state: draft
- to_state: in_progress
- transition_reason: (2026-09-30T20:40:57Z) owner direction in chat; ticket and board row created before any build.

## Steps / Checklist
- [x] Stage the packaging inputs from the device tree, build the wheel with uv, verify_wheel, member diff against
      0.2.8212, smoke in an isolated 3.14t venv; copy the wheel into dist/.
- [x] Install into priv_commandops/.venv314 (moves plus copies); check every RECORD hash; import a copy.
- [x] Upgrade the VM env; refresh the VM copy of MelderOps.
- [x] Run the diagnostic, the order matrix, the Toolbox tests and the melder_setup tests on the installed wheel.
- [x] Close work package C, this task and the epic on the owner's directive; boards and mailboxes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- dist/melder-0.2.8215-py3-none-any.whl; melder 0.2.8215 in priv_commandops/.venv314 and the VM env; the
  revalidation results.

## Files / Paths Impacted
- Exact list in the PLAN note.

## Validation
- verify_wheel for 0.2.8215 and the CI smoke script in an isolated 3.14t venv (GIL off); 594 RECORD hashes in
  .venv314; an import of a copy of the installed tree; on the installed wheel in the VM env: the diagnostic and
  the order matrix 4/4 (control on 0.2.8212: 2 failed), Toolbox 85/87 (2 skipped), melder_setup 265/265, the
  whole MelderOps suite 6561/6573 (9 skipped; 3 timing failures that fail on 0.2.8212 too). Not run: anything
  with the Windows interpreter itself (it compiles bytecode on its first import); coverage.

## Risks / Rollback Notes
- Rollback of the env: move `.venv314/_to_delete/melder-0.2.8212/` back into site-packages.
- Other agents run tests from `.venv314`; the swap is two moves and one copy, announced by a NOTICE.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No bytecode compiled into the Windows venv by the Linux interpreter (it would embed Linux paths).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner directive to close the epic)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/wheel_0_2_8215_20260930/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure

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

- DATETIME: 2026-09-30T20:41:56Z
  TYPE: PLAN
  CLAIM: Facts: priv_commandops/.venv314 (Windows uv CPython 3.14t) holds melder 0.2.8212 installed by uv with a
    direct_url to the Windows dist path, and has no _to_delete folder any more; MelderOps pins melder>=0.2.8212
    (left alone); the VM env venvs/melderops314t holds 0.2.8212 plus an editable copy of MelderOps at
    $HOME/melderops_copy; the VM has 1.2G free, uv 0.12.13 and CPython 3.14.7t; dist/ is git-ignored. Plan:
    (1) stage the files git lists as tracked or untracked-not-ignored under pyproject.toml, README.md, LICENSE,
    NOTICE and src into VM scratch, `uv build --wheel`, verify_wheel for 0.2.8215, member diff against the 0.2.8212
    wheel, the CI smoke script and the release example in an isolated 3.14t venv (GIL off), copy the wheel into
    dist/. (2) `uv pip install --target` into scratch (no bytecode), point direct_url.json at the Windows wheel
    path and fix RECORD, move melder/ and melder-0.2.8212.dist-info/ into .venv314/_to_delete/melder-0.2.8212/,
    copy the new tree in, check every RECORD hash, import a VM copy. (3) Upgrade the VM env with the wheel and
    rsync the device MelderOps tree into its copy (no .venv314, .git or caches). (4) On the installed wheel: the
    epic's diagnostic, command_0's order matrix, the Toolbox tests, the melder_setup set, then the whole MelderOps
    suite in shards (junit, since its conftest hard-exits). (5) A NOTICE to command_0 in priv_commandops.
  EVIDENCE:
  - ../priv_commandops/.venv314/Lib/site-packages/melder-0.2.8212.dist-info/direct_url.json:1-1
  - ../priv_commandops/pyproject.toml:112-112
  - tickets/tasks/completed/2026-09-29_build_0_2_8208_wheel_into_melderops_env_task.md:122-217
  - ../priv_commandops/context_compass/artifacts/2026-09-30_toolbox_native_dispense/test_native_dependency_lookup.py:1-35
  IMPACT: The same install method as 0.2.8208 and 0.2.8212; the diagnostic runs on the installed wheel, not source.
  NEXT: Stage the packaging inputs and build the wheel with uv.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T20:43:44Z
  TYPE: MEASURE
  CLAIM: dist/melder-0.2.8215-py3-none-any.whl is built (uv 0.12.13, setuptools backend, CPython 3.14.7t) from a
    fresh staging copy of the 596 files git lists as tracked or untracked-not-ignored under pyproject.toml,
    README.md, LICENSE, NOTICE and src (none untracked). verify_wheel passes for 0.2.8215; 591 members, the same
    package set as 0.2.8212 (585 files, none added or removed); all 585 package files are byte-identical to the
    device tree; the lane's markers (flag_dependencies_without_own_plan, _requires_own_target_pass,
    _raise_unless_resolution_valid, the version) are present; sha256 cfaf55b6...4191, 3258176 bytes. In an isolated
    3.14t venv (-I, GIL off) the CI smoke script passes for 0.2.8215 and the release example returns the injected
    instance on its direct meld. The same bytes are in dist/.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/wheel_build.log:2112-2119
  - context_compass/artifacts/wheel_0_2_8215_20260930/wheel_verify.log:1-11
  - context_compass/artifacts/wheel_0_2_8215_20260930/wheel_smoke.log:1-7
  - context_compass/artifacts/wheel_0_2_8215_20260930/verify_wheel_8215.py:1-53
  IMPACT: The wheel carries option B and the refreshed assets; it is ready for MelderOps' environments.
  NEXT: Install it into priv_commandops/.venv314 with moves and copies, then check it against RECORD.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T20:46:13Z
  TYPE: MEASURE
  CLAIM: melder 0.2.8215 is installed in priv_commandops/.venv314. Method (the VM cannot run the Windows
    interpreter): `uv pip install --target` into VM scratch (no bytecode), direct_url.json pointed at the Windows
    wheel path and uv's uv_cache.json stamp dropped (RECORD rewritten, 594 rows checked in scratch), the old
    `melder/` (with its 533 Windows .pyc and runtime caches) and `melder-0.2.8212.dist-info/` moved into
    `.venv314/_to_delete/melder-0.2.8212/`, the new tree copied in. The recursive copy stopped once with "cannot
    create directory melder/__melder_cache__: File exists" (the directory was there, empty, when inspected), so
    its one marker file and the dist-info were copied separately. The installed tree then matches its RECORD: 594
    rows, no hash or size mismatch, no stray or missing file, no .pyc; INSTALLER uv, direct_url the Windows dist
    path. A VM copy of it imports as 0.2.8215 (metadata agrees) and the release example passes on it.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/melderops_env_before.txt:1-11
  - context_compass/artifacts/wheel_0_2_8215_20260930/prepare_windows_install.log:1-2
  - context_compass/artifacts/wheel_0_2_8215_20260930/melderops_env_install_check.log:1-3
  - context_compass/artifacts/wheel_0_2_8215_20260930/melderops_env_import_copy.log:1-4
  IMPACT: MelderOps' Windows env carries option B; Windows compiles bytecode on its first import there; the old
    files wait in .venv314/_to_delete/ for an owner delete.
  NEXT: Upgrade the VM env with the wheel and refresh its copy of MelderOps from the device tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T20:47:30Z
  TYPE: MEASURE
  CLAIM: The epic's unchanged diagnostic passes on the installed 0.2.8215 wheel. VM env venvs/melderops314t: uv
    replaced 0.2.8212 with the dist/ wheel (melder imports from the venv's site-packages; melder_ops from the
    editable copy), and $HOME/melderops_copy was refreshed from the device tree (89 files changed, caches
    excluded) with command_0's two diagnostics copied to their original paths. Run as in the epic (repo root,
    PYTHONPATH=src, GIL off): test_native_dependency_lookup (Spectrum host, NativeService/NativeConsumer, direct
    service meld `is consumer.service`) and the order matrix (service_only, service_first, tool_first) - 4 passed.
    Control in the same env and copy with 0.2.8212 reinstalled: the direct lookup and tool_first fail with the
    original "Cannot build CreationContext before spell_codegen_creation exists." (2 failed, 2 passed); the env
    was put back on 0.2.8215.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/vm_melderops_env_install.log:1-6
  - context_compass/artifacts/wheel_0_2_8215_20260930/melderops_copy_refresh.log:1-17
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_0_2_8215.log:1-14
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_control_0_2_8212.log:1-15
  - ../priv_commandops/context_compass/artifacts/2026-09-30_toolbox_native_dispense/test_native_dependency_lookup.py:1-35
  IMPACT: The epic's first acceptance criteria hold on the delivered build in a MelderOps host; the red control
    shows the diagnostic detects the defect in this environment. The Windows interpreter run stays Not run.
  NEXT: Run the Toolbox tests, the melder_setup set and the whole MelderOps suite on the installed wheel.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T21:15:04Z
  TYPE: MEASURE
  CLAIM: The whole MelderOps suite on the installed 0.2.8215 wheel (VM env, CPython 3.14.7t, GIL off, a clean
    PYTHONPYCACHEPREFIX, eight shards under 170 s): 6573 tests, 6561 passed, 9 skipped, 3 failed, none from Melder.
    command_center 2902/2905 (3 skipped), component 473/473, system_integration and test_idea 29/30 (1 skipped),
    utilities 975/977 (2 skipped), concurrency 1296/1296, synchronization 886/892. The three failures are timing
    tests of MelderOps' own primitives: AgenticCoordinator test_28 measures 0.1496-0.1500 s against >= 0.15 and
    fails 6 of 6 runs on 0.2.8212 as on 0.2.8215; FlowRegulator fairness fails 1 of 6 isolated runs on 0.2.8215
    and failed in the 0.2.8212 control too; FlowRegulator latency ratio passes 6 of 6 in isolation. Focused sets:
    Toolbox 85/87 (2 skipped), melder_setup 265/265 - the Toolbox fixture failure recorded in the epic now passes.
    A first utilities run showed 18 failures caused by Windows-compiled .pyc in the VM copy's __pycache__ (code
    objects named C:\Users\...); the clean-prefix run passes, and the stale runs are kept under suite/superseded/.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/suite/summary.txt:1-67
  - context_compass/artifacts/wheel_0_2_8215_20260930/suite/test_28_repeats_control_0_2_8212.log:1-12
  - context_compass/artifacts/wheel_0_2_8215_20260930/suite/timing_repeats_0_2_8215.log:1-12
  - context_compass/artifacts/wheel_0_2_8215_20260930/junit_summary.py:1-25
  IMPACT: No MelderOps regression from 0.2.8215; the epic's consumer revalidation is complete in the VM. The
    Windows interpreter itself: Not run (the same RECORD-verified files are in .venv314).
  NEXT: Close work package C, this task and the epic on the owner's directive, then sync boards and mailboxes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T21:18:29Z
  TYPE: DECISION
  CLAIM: Closure on the owner's directive (chat): "you can close that epic if its done". Every exit-gate item of
    this task is met, and with it the epic's: work package C (option B, 0.2.8215), this task and the epic move to
    their completed folders; board rows become closed anchors, artifact rows cleared; NOTICEs M0-155..157 in
    melder_private and M0-158 to command_0 in priv_commandops.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/suite/summary.txt:1-67
  - context_compass/artifacts/wheel_0_2_8215_20260930/melderops_env_install_check.log:1-3
  IMPACT: MelderOps runs the fix; the Windows run of the diagnostic is left to the owner or command_0.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done 2026-09-30T21:18:29Z: wheel in dist/, .venv314 and the VM env; diagnostic green on it;
the old 0.2.8212 files wait in .venv314/_to_delete/melder-0.2.8212/ for an owner delete.
Opened 2026-09-30T20:40:57Z on the owner's direction: build, install and revalidate 0.2.8215 in MelderOps, then
close the epic if the diagnostic passes.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
