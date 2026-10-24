# Task: ci_lane_loose_ends - say Melder depends on pip, pin pip where CI installs it, settle two stale backlog tickets

- Completed: 2026-10-24T21:59:15Z
- Summary: pyproject's description and README:44 say Melder depends on pip; pip==26.2.2 is pinned in the speed
  manifest and docs/requirements.lock, and both installed-package probes install the wheel beside the running
  release's test-manifest pins (`runtime-requirements`) and run `pip check`, documented in .github/ci_cd/ and
  BRANCH_WORKFLOW.md; tests/unit/github_workflows 506 passed (hosted CI Not run). The 2026-10-04 cache temp-file task
  closed superseded and the 2026-09-22 shared-gauntlet task obsolete. No src change, no notch. Owner-owed: the commit
  of the guide, tests-map, release-note and ticket edits (the code is in 3cf114b9d); the LLM bundles are rebuilt at
  melder_1's 0.2.8267 landing.

## Metadata
- Task ID: TASK-2026-10-24-ci_lane_loose_ends
- Story: none (standalone; the loose ends TASK-2026-10-24-ci_python_315_and_release_test_rerun flagged at closure)
- Status: done
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T21:14:14Z
- Updated: 2026-10-24T21:59:15Z

## Objective
Close the four loose ends left at the CI lane's closure, on the owner's word (chat 2026-10-24, 15:07 MDT: "yeah
update toml to that please, ok sure edit .github its fine, yeah so get t hose loose ends fixed up, then we'll talk
next"):
1. `pyproject.toml`'s description says "Zero dependencies" while `[project.dependencies]` holds `pip==26.2.2`; the
   README's "**Zero dependencies.**" line makes the same claim. Both say what Melder depends on.
2. The speed manifest and the two installed-package probes pin pip as `.github/ci_cd/python_versions.md`'s "Add a
   runtime dependency to Melder" recipe asks (steps 3 and 4, and 5 if the documentation build imports Melder), with
   `.github/ci_cd/` kept current.
3. TASK-2026-10-04-per_process_conjure_cache_temp_file is covered by 0.2.8266 (melder_0's per-writer temp file):
   closed as superseded once that landing is turned in.
4. TASK-2026-09-22-shared-gauntlet-configuration-order-followup lost its evidence in the 2026-10-24 cleanup: the
   failure is reproduced on the current tree, then the ticket is closed as obsolete with evidence or carries the
   fresh evidence for a later pick.

## Ticket Contract
- ENTRY_GATE: the owner's word above; an active board row; `.github/ci_cd/` read before any `.github` edit
  (special_instructions/ci_cd_guide.md).
- EXECUTION_BOUNDARY: the `description` line of `pyproject.toml`; README.md's dependency line;
  `.github/python/speed/3.14.7.toml`; the wheel probe in `.github/workflows/build-distributions.yml`;
  `probe_install` in `.github/scripts/testpypi_candidate.py` and any script or test the pin source needs;
  `.github/ci_cd/`; `tests/unit/github_workflows/`; the documentation requirements if step 5 applies; the tests
  documents (with their indexes) where they describe these files; one packaging line in
  `release_docs/next_version_release.md`, coordinated with the lanes landing before it; the two backlog tickets
  of items 3 and 4; this ticket and its board row. No `src/` change, so no notch.
- DEPENDENCIES: TASK-2026-10-24-ci_python_315_and_release_test_rerun (completed; it pinned pip in the test
  manifests); TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0, 0.2.8266) for item 3; the release note
  and the LLM bundles, which melder_0 (0.2.8266), melder_1 (0.2.8267) and melder_3 rebuild or edit in turn.
- EXIT_GATE: both texts true; the speed manifest and both probes install pip==26.2.2 from a pin, documented in
  `.github/ci_cd/`; `python -m pytest tests/unit/github_workflows` green with the checkout's pyproject.toml; items 3
  and 4 closed or carrying their evidence and next step; the release-note line in; the bundles rebuilt after the
  last of these edits with both checks printing only OK (by the last lander, or by me).
- FAILURE_ESCALATION: DECISION_REQUEST if pinning pip in `probe_install` needs a fetch its `--no-index` posture
  forbids; CONFLICT if the release note or a tests document is mid-edit by another lane; BLOCKER if the gauntlet
  failure cannot be reproduced for want of an input that no longer exists.

## Scope Boundaries
- In scope: the two texts, the three pip pins and their documentation, the two backlog tickets' state.
- Out of scope: whether Melder should depend on pip (the owner's call, recorded as intended); hosted CI runs (the
  owner's; "Not run" until seen); any `src/` change; repairing the gauntlet setup if the failure still reproduces
  (a later pick).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: every exit-gate item holds (Notes from 21:47:48Z): both texts true; the speed manifest and both
  probes install pip==26.2.2 from a pin, documented in `.github/ci_cd/`; tests/unit/github_workflows green; items 3
  and 4 closed with their evidence; the release-note line in. The bundle rebuild is the last lander's (melder_1,
  0.2.8267), as the exit gate allows. Earlier: draft -> in_progress (opened and started on the owner's word, chat
  2026-10-24, 15:07 MDT, quoted in Objective).

## Steps / Checklist
- [x] Read `.github/ci_cd/`, the speed manifest, both probes and the tests that pin dependencies; record the plan.
- [x] Item 1: the description and the README line.
- [x] Item 2: pin pip in the speed manifest and both probes; `.github/ci_cd/` and the tests documents; tests.
- [x] Item 3: close the 2026-10-04 cache temp-file task as superseded once 0.2.8266 is turned in.
- [x] Item 4: reproduce the shared gauntlet's setup on the current tree; close or update that ticket.
- [x] Release-note line; NOTICEs; closure; the bundles rebuilt last by whoever lands last (melder_1's landing).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- True dependency texts; pip pinned wherever CI installs Melder's runtime dependencies; two backlog tickets settled.

## Files / Paths Impacted
- pyproject.toml (the `description` line)
- README.md (the dependency line)
- .github/python/speed/3.14.7.toml
- .github/workflows/build-distributions.yml
- .github/scripts/testpypi_candidate.py
- .github/ci_cd/
- tests/unit/github_workflows/
- release_docs/next_version_release.md
- context_compass/tickets/tasks/backlog/2026-10-04_per_process_conjure_cache_temp_file_task.md
- context_compass/tickets/tasks/backlog/2026-09-22_shared_gauntlet_configuration_order_followup_task.md

## Validation
- Ran (device VM, CPython 3.14.7 free-threaded, the test-manifest pins in a venv):
  - `python -X gil=0 -m pytest tests/unit/github_workflows -q -p no:cacheprovider`: 506 passed at 3cf114b9d and
    506 passed after the guide edits (490 before the change, on 3bedd65bb).
  - `python -X gil=0` and `-X gil=1 -m pytest benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py -q`:
    5 passed each (item 4's evidence).
  - `index_document.py --doc context_compass/system_docs/tests_components.md --check`: OK.
- Not run: hosted CI (the owner's; the RC probe's PyPI download and the Windows and macOS cells are unseen); the
  build-asset and LLM-bundle rebuilds and checks, which run last at melder_1's 0.2.8267 landing (M0-219: the
  bundles' tests corpus is stale until then).

## Risks / Rollback Notes
- The release note and the LLM bundles are shared with three landing lanes; edit the note by text anchor after a
  fresh read, and leave the rebuild to the last lander.
- Every edit is a few lines in a tracked file; git restores any of them.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

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

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

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
- Ticket/Work Author(s): melder_2 (synaptic_python_developer); prose; created 2026-10-24T21:14:14Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none (a routine CI and documentation change closed on the owner's word; my own checks
  are not independent review)

## Notes
- DATETIME: 2026-10-24T21:14:14Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner chose to close all four loose ends (chat 2026-10-24, 15:07 MDT, quoted in Objective): the
    description, `.github` ("ok sure edit .github its fine"), and the two stale backlog tickets. The README line
    makes the description's claim word for word, so it is fixed with it and reported to him.
  EVIDENCE:
  - pyproject.toml:8-8
  - pyproject.toml:71-73
  - README.md:44-44
  - context_compass/tickets/tasks/completed/2026-10-24_ci_python_315_and_release_test_rerun_task.md:470-472
  IMPACT: Scope and authority for the four items are set; nothing outside them is in this lane.
  NEXT: Read `.github/ci_cd/`, the speed manifest, the two probes and the pin tests, then record the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:14:14Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The tree moved since the CI lane closed. The owner committed that lane's 23 files with his pyproject.toml,
    README.md and uv.lock edits in 0fddab923 (14:42 MDT), then fa397480e and 3bedd65bb (15:06 MDT, melder_0's 0.2.8266
    documents among them); `__version__` reads 0.2.8266. M0-217 (melder_0, consumed here): it took 0.2.8266 - notch
    above it if landing after; melder_1's removal is next at 0.2.8267 - and its closing rebuild runs with
    --include-untracked. melder_3 now holds src_architecture_to_spec (trims src_architecture after melder_1's
    turn-in). 0.2.8266's invariant names a per-writer temp file, `<conduit>.meldercache.<pid>.<thread id>.tmp`.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/system_docs/src_architecture.md:1176-1200
  - context_compass/attention_board.md:112-115
  IMPACT: Items 1 and 2 edit committed files; this lane takes no notch; three lanes edit the release note or rebuild
    the bundles after melder_0, so my note line and the rebuild order go through the mailbox; item 3's supersession
    is in the code that landed.
  NEXT: As in the DECISION note above.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:25:11Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Item 4 is obsolete. The failure (the 2026-09-19 lane's validation.md, kept in git at 72b712179^) was the
    shared gauntlet's Melder adapter calling configure_aether_frame before it set
    phase_scheduler_workers_per_spellbook ("Cannot modify configuration after it is frozen."). Since f1cd22a22
    (2026-09-26) `_build_runtime_melder` sets the property on a fresh configuration with no frame call before it,
    and the lane-parity guard builds that lane: 5 passed on 3bedd65bb with the GIL off (3.14.7t), among them
    test_shared_gauntlet_does_not_borrow_the_melder_only_builder.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1066-1106
  - benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py:429-451
  IMPACT: That task closes as obsolete with evidence, the second branch of its exit gate; nothing to repair.
  NEXT: Close TASK-2026-09-22-shared-gauntlet-configuration-order-followup with this evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:25:11Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Item 3 is covered by landed code. The 2026-10-04 task asks for a per-process temp name in place of the
    fixed `<bundle>.melc.tmp`, keeping the atomic replace; since 0.2.8266 (melder_0,
    TASK-2026-10-24-cache_file_write_failure_fails_meld, F2) the save writes `<bundle name>.<pid>.<thread id>.tmp`,
    renames it onto the bundle and removes it when the save is refused.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:948-1019
  - context_compass/system_docs/src_architecture.md:1176-1200
  IMPACT: That task closes as superseded by 0.2.8266; its two-writer test is melder_0's per-writer temp-name test.
  NEXT: Close TASK-2026-10-04-per_process_conjure_cache_temp_file as superseded.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:25:11Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Items 1 and 2, following python_versions.md's runtime-dependency recipe (steps 3-5):
    (1) pyproject's description reads "One dependency (pip), 3.14+ no-GIL." and README:44 "**One dependency:
    pip.** Nothing else comes with it." (pip declares no dependencies of its own);
    (2a) the speed manifest pins pip==26.2.2 with the test manifests' comment;
    (2b) python_runtime_matrix.py gains `declared_dependencies` (the [project.dependencies] names), `runtime_pins`
    (a manifest's pins of them; a declared one left unpinned is refused) and a `runtime-requirements` operation
    writing them for the running release's test manifest, or --manifest;
    (2c) the wheel probe in build-distributions.yml installs those pins with the wheel (--no-deps), then
    `uv pip check`; (2d) `probe_install` downloads them from PyPI (isolated, no deps, wheels only), installs them
    with the TestPyPI wheel (--no-deps --no-index), then `pip check`;
    (2e) docs/requirements.lock pins pip==26.2.2: the docs build imports Melder from src for autodoc;
    (2f) tests for 2b and 2d, the wheel-probe contract updated, the runtime-dependency test covering the speed
    manifest; (2g) python_versions.md, scripts.md, workflows.md and BRANCH_WORKFLOW.md current; the tests map's C1
    extents and index regenerated.
    The test cells, the manifest format and src/ stay as they are.
  EVIDENCE:
  - .github/ci_cd/python_versions.md:105-117
  - .github/python/speed/3.14.7.toml:6-15
  - .github/workflows/build-distributions.yml:68-74
  - .github/scripts/testpypi_candidate.py:198-219
  - docs/conf.py:12-12
  - docs/requirements.lock:1-32
  - tests/unit/github_workflows/test_python_runtime_matrix.py:219-234
  IMPACT: pip==26.2.2 is installed wherever CI or the docs build imports Melder, from one source per release,
    and both probes prove the installed set satisfies the wheel's own requirement; baseline before any edit:
    tests/unit/github_workflows 490 passed on 3bedd65bb (3.14.7t, GIL off).
  NEXT: Make the item 1 edits, then 2a-2g, then run tests/unit/github_workflows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T21:47:48Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Items 1 and 2a-2f are in, as the PLAN note set them out, and the owner committed them in 3cf114b9d
    (15:42 MDT) with melder_0's closure: both texts say "One dependency (pip)"; the speed manifest and
    docs/requirements.lock pin pip==26.2.2; python_runtime_matrix.py has `declared_dependencies`, `runtime_pins`,
    `release_manifest` and the `runtime-requirements` operation; the wheel probe installs the wheel beside those
    pins with --no-deps and runs `uv pip check`; `probe_install` downloads the pins from PyPI (isolated, wheels
    only, no deps), installs them with the TestPyPI wheel (--no-deps --no-index) and runs `pip check` before the
    smoke test; 16 test cases added and the wheel-probe contract test updated. This context was re-onboarded
    (REONBOARD at 21:45Z) after a compaction; these are the files as they stand at 3cf114b9d.
  EVIDENCE:
  - pyproject.toml:8-8
  - README.md:44-44
  - .github/python/speed/3.14.7.toml:7-8
  - docs/requirements.lock:16-16
  - .github/scripts/python_runtime_matrix.py:247-329
  - .github/scripts/python_runtime_matrix.py:516-523
  - .github/workflows/build-distributions.yml:68-78
  - .github/scripts/testpypi_candidate.py:203-273
  - tests/unit/github_workflows/test_python_runtime_matrix.py:250-366
  - tests/unit/github_workflows/test_candidate_publication.py:438-530
  - tests/unit/github_workflows/test_workflow_contracts.py:518-551
  IMPACT: The speed manifest changed, so by its own rule (lines 1-3) the next speed run starts a new comparison
    baseline; the LLM bundles' tests corpus was rebuilt before these edits (M0-219), so melder_1's landing rebuild
    covers it. 2g (the guide and the tests map) is what remains of item 2.
  NEXT: Update .github/ci_cd/ (python_versions.md, scripts.md, workflows.md) and BRANCH_WORKFLOW.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T21:47:48Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: `python -X gil=0 -m pytest tests/unit/github_workflows -q -p no:cacheprovider` gives 506 passed in 4.98 s
    on 3cf114b9d (CPython 3.14.7 free-threaded, GIL off, the test-manifest pins in a venv on the device VM), against
    490 on 3bedd65bb before the change. Hosted CI: Not run (the owner's).
  EVIDENCE:
  - tests/unit/github_workflows/test_python_runtime_matrix.py:250-366
  - tests/unit/github_workflows/test_candidate_publication.py:438-530
  IMPACT: The pin source, both probes and the contract tests agree on the committed tree; the guide edits next
    must keep the ci_cd contract test green.
  NEXT: Re-run the same command after the guide edits.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:53:45Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: 2g and the release-note line are in. The CI guide says the speed manifest holds pip, describes both
    installed-package probes (the `runtime-requirements` pins beside the wheel, no resolver, `pip check` before the
    smoke test; the RC probe's wheel from TestPyPI by hash and pins from PyPI) and rewrites the runtime-dependency
    recipe (steps 2-5: the tests that refuse a manifest, the probes following on their own, a transitive
    dependency left to `runtime_pins`, the docs lock); scripts.md lists the operation and the probe, workflows.md
    the two probes, BRANCH_WORKFLOW.md the speed manifest, the dependency rule and both probes. The tests map's
    Repository Tooling Unit Cluster protects the pins, the three C1 extents are remeasured (954, 530, 539) and its
    index regenerated (`--check` OK). The release note's Packaging section says Melder declares pip==26.2.2 (the
    owner's 0fddab923; the note had no line for it) and what CI checks, before the rebuild line. Afterwards
    `pytest tests/unit/github_workflows` gives 506 passed (3.14.7t, GIL off).
  EVIDENCE:
  - .github/ci_cd/python_versions.md:41-43
  - .github/ci_cd/python_versions.md:74-90
  - .github/ci_cd/python_versions.md:121-133
  - .github/ci_cd/scripts.md:13-13
  - .github/ci_cd/scripts.md:43-46
  - .github/ci_cd/scripts.md:75-78
  - .github/ci_cd/workflows.md:70-70
  - .github/ci_cd/workflows.md:127-130
  - .github/BRANCH_WORKFLOW.md:160-170
  - .github/BRANCH_WORKFLOW.md:264-266
  - .github/BRANCH_WORKFLOW.md:361-364
  - context_compass/system_docs/tests_components.md:1447-1450
  - context_compass/system_docs/tests_components.md:3136-3155
  - context_compass/system_docs/tests_components.md:3903-3908
  - release_docs/next_version_release.md:1469-1473
  IMPACT: Item 2's exit gate holds: the speed manifest and both probes install pip==26.2.2 from a pin, documented
    in `.github/ci_cd/`, and the workflow suite is green. melder_1 re-reads the note and the tests map before
    editing (M2-32); its 0.2.8267 header and rebuild-line bump take my bullet as it stands.
  NEXT: Close the two backlog tickets (items 3 and 4) with their evidence, then this one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T21:59:15Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Items 3 and 4 are closed and anchored, each moved to tickets/tasks/completed/:
    TASK-2026-10-04-per-process-conjure-cache-temp-file (superseded by 0.2.8266; its Windows `-n 4` rerun Not run;
    the Objective above spells its ID with underscores) and TASK-2026-09-22-shared-gauntlet-configuration-order-
    followup (obsolete; the lane-parity guard 5 passed with the GIL off and on at 3cf114b9d). melder_1 consumed
    M2-32, notched 0.2.8267 at 21:51 and has not yet edited the release note, so my bullet sits before its rebuild
    line for that landing to keep.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-04_per_process_conjure_cache_temp_file_task.md:3-9
  - context_compass/tickets/tasks/completed/2026-09-22_shared_gauntlet_configuration_order_followup_task.md:1-7
  - context_compass/attention_board.md:144-145
  - src/melder/__version__.py:12-12
  IMPACT: Every exit-gate item holds but the bundle rebuild, which the exit gate gives to the last lander; this
    ticket closes on the owner's word.
  NEXT: Sync the board, NOTICE melder_1 and melder_3, report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- DONE 2026-10-24T21:59:15Z: all four loose ends (Completed summary above). The code, texts and pins are in the
  owner's 3cf114b9d; the CI guide (.github/ci_cd/python_versions.md, scripts.md, workflows.md), BRANCH_WORKFLOW.md,
  the tests map and its index, the release-note bullet and the three ticket closures await his commit.
- Owner-owed: that commit; hosted CI (Not run); the LLM bundles and build assets are rebuilt last by melder_1's
  0.2.8267 landing (or melder_3 after it). The next speed run is a new comparison baseline (the speed manifest
  changed).

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
