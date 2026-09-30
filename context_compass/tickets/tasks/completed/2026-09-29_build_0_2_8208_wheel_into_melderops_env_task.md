

# Task: Build the 0.2.8208 wheel, install it into the MelderOps env and raise MelderOps' Melder floor

## Metadata
- Task ID: TASK-2026-09-29-build-0-2-8208-wheel-into-melderops-env
- Story: none; rollout step of EPIC-2026-09-29-host-integration-read-surface ("Rollout / Adoption Plan")
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-29T22:09:30Z
- Updated: 2026-09-29T22:28:22Z

- Completed: 2026-09-29T22:28:22Z
- Summary: dist/melder-0.2.8208-py3-none-any.whl built (assets restamped 0.2.8208, verify_wheel and the CI smoke
  pass) and installed in priv_commandops/.venv314 over 0.2.8207 (RECORD-verified; old files in
  .venv314/_to_delete/); MelderOps' floor raised to melder>=0.2.8208; VM env venvs/melderops314t runs
  MelderOps' melder_setup tests on it (265 passed). No source change, no notch.

## Objective
Owner direction (chat, 2026-09-29, about 22:05Z): "no bro into your test environment, just make a new wheel with the
new version and install it into the melderops env and up the toml version", then "so your test env should have then
newst and melderops". Build `dist/melder-0.2.8208-py3-none-any.whl` with build assets stamped 0.2.8208, install it
into MelderOps' environment `priv_commandops/.venv314` (it holds 0.2.8207 today), raise MelderOps' floor in
`priv_commandops/pyproject.toml` from `melder>=0.2.8207` to `melder>=0.2.8208`, and give the VM test environment a
MelderOps environment carrying the same wheel. This answers the open question from before the compaction: the owner
does not want MelderOps' code switched onto the new calls in this lane.

## Ticket Contract
- ENTRY_GATE: owner direction in chat; this board row; the PLAN note below before any write.
- EXECUTION_BOUNDARY: melder_private - the generated build assets (rebuilt, stamped 0.2.8208), `dist/`, this task's
  artifacts. priv_commandops - the melder files in `.venv314/Lib/site-packages` (swapped by moves, no deletes) and
  the one dependency line plus its comment in `pyproject.toml`; no source, test or ContextCompass edits there. VM -
  a new venv under `$HOME/venvs/`. No notch: no source changes.
- DEPENDENCIES: TASK-2026-09-29-implement-frame-lookups-and-read-accessors (0.2.8208 landed 21:34:06Z);
  special_instructions/agent_contribution_guide.md (generated assets and rebuild order).
- EXIT_GATE: the wheel passes `verify_wheel` for 0.2.8208; the files installed in `.venv314` match the wheel's
  RECORD, and an isolated import of a copy of them reports 0.2.8208 with the new calls; the floor reads
  `melder>=0.2.8208`; the VM env imports `melder_ops` on melder 0.2.8208 and a MelderOps test subset passes.
- FAILURE_ESCALATION: BLOCKER if the Windows venv cannot be updated with moves only; then hand the owner the one
  native install command instead of forcing it.

## Scope Boundaries
- In scope: the objective above.
- Out of scope: MelderOps source changes (command_0's paused native_aether_access ticket), publishing, commits, a
  release cut, the frame-lookup lane's docs (they resume in their own task).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Every exit-gate item met; owner directive (chat, 2026-09-29) to turn in.

## Steps / Checklist
- [x] Rebuild the build assets at 0.2.8208 on a VM copy; copy them to the device tree; asset --check OK.
- [x] Build the wheel from a fresh staging copy; verify_wheel and a smoke import; copy it into dist/.
- [x] Install it into priv_commandops/.venv314 (moves plus unpack); check against RECORD; import a copy.
- [x] Raise the floor in priv_commandops/pyproject.toml (CRLF file kept CRLF).
- [x] VM MelderOps env with the wheel; import check and a MelderOps test subset.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- dist/melder-0.2.8208-py3-none-any.whl; melder 0.2.8208 in priv_commandops/.venv314; the raised floor; the VM env.

## Files / Paths Impacted
- Exact list in the PLAN note.

## Validation
- verify_wheel for 0.2.8208; the CI smoke script in an isolated 3.14t venv (GIL off); 593 RECORD hashes
  in .venv314; an import of a copy of the installed tree; MelderOps melder_setup tests on the VM env: 265
  passed. Not run: anything with the Windows interpreter itself (the owner's first import there compiles the
  bytecode); coverage.

## Risks / Rollback Notes
- The frame-lookup lane still owes its docs; the final asset rebuild after them changes the packaged system
  documents, so the wheel is rebuilt and reinstalled then (same version, so the reinstall must replace in place).
- Rollback of the env: move `.venv314/_to_delete/melder-0.2.8207/` back into site-packages.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No bytecode compiled into the Windows venv by the Linux interpreter (it would embed Linux paths).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed; the MelderOps pyproject comment)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner directive to turn in)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/wheel_0_2_8208_20260929/
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
- DATETIME: 2026-09-29T22:10:34Z
  TYPE: PLAN
  CLAIM: Facts first: MelderOps' env `priv_commandops/.venv314` is a Windows venv (pyvenv.cfg home is a Windows
    uv CPython 3.14t) holding melder 0.2.8207 installed by pip, so this VM cannot run its interpreter; the
    connected folders refuse deletes but allow moves; `verify_wheel` requires BUILT_FOR_VERSION == 0.2.8208 in the
    three manifests, which still say 0.2.8207; MelderOps pins `melder>=0.2.8207`; PyPI is reachable from the VM
    (HTTP 200) and uv 0.12.13 is installed. Plan: (1) rsync the device tree to $HOME/wt2_new, run the asset runner
    and --check there, copy the changed generated files back, --check on the device. (2) Stage a fresh copy of the
    packaging inputs, `uv build --wheel`, verify_wheel + smoke import, copy the wheel into dist/. (3) `uv pip
    install --target` the wheel into VM scratch (no bytecode, so no Linux paths get compiled in), move the old
    `melder/` and `melder-0.2.8207.dist-info/` into `.venv314/_to_delete/melder-0.2.8207/` (git-ignored by the
    venv's own `*` .gitignore), copy the new tree in, check every RECORD hash, import a VM copy of it. (4) Raise
    the floor line in priv_commandops/pyproject.toml (CRLF kept) with one comment line. (5) New VM venv
    $HOME/venvs/melderops314t: the wheel plus an editable VM copy of MelderOps with [test]; import check and the
    MelderOps tests around melder_setup. Also: while probing write access at 22:04Z I created the 0-byte file
    `priv_commandops/.write_probe_melder0`; deletes are refused, so it moves into `.venv314/_to_delete/` too.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8208_20260929/melderops_env_before.txt:1-36
  - .github/scripts/verify_distributions.py:83-113
  - src/melder/_build_assets/_bind_guard/bind_guard.py:79-95
  IMPACT: The wheel only verifies after the asset rebuild; the Windows env is updated with moves and copies only.
  NEXT: Rsync the device tree to the VM copy and run the asset runner there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T22:15:47Z
  TYPE: MEASURE
  CLAIM: Build assets rebuilt at 0.2.8208 on the VM copy (agent documentation 460 entries, bind guard 619, system
    documents 4; --check OK there). Only the five manifests changed in content (version stamps; the bind-guard
    source hash moved with this lane's source); the three payloads differ from the device copies only in line
    endings, so they were left alone. The five manifests were written to the device tree keeping its CRLF
    endings, and the asset --check on the device tree is OK for all three assets.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8208_20260929/assets_rebuild_vm.log:1-7
  - context_compass/artifacts/wheel_0_2_8208_20260929/assets_copy_back.log:1-8
  - context_compass/artifacts/wheel_0_2_8208_20260929/assets_check_device.log:1-3
  IMPACT: The wheel can now pass verify_wheel; the final asset rebuild after the frame-lookup docs is still owed.
  NEXT: Stage the packaging inputs and build the wheel with uv.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T22:17:08Z
  TYPE: MEASURE
  CLAIM: `dist/melder-0.2.8208-py3-none-any.whl` built with uv (setuptools backend, 3.14t) from a fresh staging copy
    of pyproject, README, LICENSE, NOTICE and src (runtime caches excluded, the tracked
    `__melder_cache__/__melder_cache__.py` marker included - the first staging dropped it and the member diff
    against 0.2.8206 caught it). verify_wheel passes for 0.2.8208; 591 members, the same set as the 0.2.8206 wheel;
    sha256 fedee807...52f2. In an isolated 3.14t venv (-I, GIL off) the CI smoke script passes and the new calls
    work: a fresh world lists no frames, get_frame returns a Spellbook's frame, root.spellbook is its Book.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8208_20260929/wheel_verify.log:1-8
  - context_compass/artifacts/wheel_0_2_8208_20260929/wheel_smoke.log:1-4
  - .github/scripts/smoke_wheel.py:44-79
  IMPACT: The wheel is ready for MelderOps' env.
  NEXT: Install it into priv_commandops/.venv314 with moves and copies, then check it against RECORD.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T22:18:44Z
  TYPE: MEASURE
  CLAIM: melder 0.2.8208 is installed in priv_commandops/.venv314. Method (the VM cannot run the Windows
    interpreter): `uv pip install --target` into VM scratch (no bytecode), direct_url.json pointed at the
    Windows wheel path and uv's own cache stamp dropped (RECORD updated), the old `melder/` and
    `melder-0.2.8207.dist-info/` moved into `.venv314/_to_delete/melder-0.2.8207/`, the new tree copied in. All
    593 RECORD hashes and sizes match, no stray or missing files, no .pyc; a VM copy of the installed tree imports
    as 0.2.8208 (metadata agrees) and a fresh world lists no frames. The 0-byte probe file I created at the repo
    root (22:04Z) moved to `.venv314/_to_delete/` as well; both need an owner delete (the venv's `*` .gitignore
    keeps them out of git meanwhile).
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8208_20260929/melderops_env_install_check.log:1-8
  - context_compass/artifacts/wheel_0_2_8208_20260929/melderops_env_before.txt:1-36
  IMPACT: MelderOps' env now carries the new calls; Windows compiles bytecode on first import there.
  NEXT: Raise the floor line in priv_commandops/pyproject.toml.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T22:23:21Z
  TYPE: MEASURE
  CLAIM: MelderOps' floor is raised: priv_commandops/pyproject.toml now reads `melder>=0.2.8208` with a three-line
    comment (CRLF kept; tomllib parses the dependencies as greenlet==3.5.5, melder>=0.2.8208). The VM test env
    `$HOME/venvs/melderops314t` (uv CPython 3.14.7t) holds the 0.2.8208 wheel plus an editable VM copy of
    MelderOps with [test] (greenlet 3.5.5, pytest 9.0.3, pytest-timeout 2.4.0). The ten MelderOps test files that
    exercise melder_setup (configurations, composition, bootstraps, native initialization) pass on it with the
    GIL off: 265 tests, 0 failures, 0 errors, 0 skipped (junit report; the suite's conftest hard-exits after the
    session, so the terminal summary line is not printed).
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8208_20260929/melderops_pyproject_before.toml:104-107
  - context_compass/artifacts/wheel_0_2_8208_20260929/vm_melderops_env_install.log:1-12
  - context_compass/artifacts/wheel_0_2_8208_20260929/melderops_setup_tests.txt:1-10
  - context_compass/artifacts/wheel_0_2_8208_20260929/melderops_setup_tests.xml:1-2
  IMPACT: Every exit-gate item of this task is met; MelderOps runs on 0.2.8208 in the VM.
  NEXT: Owner direction (22:22Z): add the release-note entry, keep the version, turn in, no asset rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Turned in 2026-09-29T22:28:22Z. dist/melder-0.2.8208-py3-none-any.whl (sha256 fedee807...52f2) is installed in
priv_commandops/.venv314 (INSTALLER uv, direct_url pointing at the Windows dist path); the old 0.2.8207 files
and my 0-byte write probe sit in .venv314/_to_delete/ for the owner to delete. MelderOps requires
melder>=0.2.8208. The VM env venvs/melderops314t has the same wheel and an editable VM copy of MelderOps.
When the frame-lookup docs land and assets are rebuilt, rebuild the wheel and reinstall it the same way (same
version, so replace the files in place).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
