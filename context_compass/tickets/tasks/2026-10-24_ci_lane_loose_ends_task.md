# Task: ci_lane_loose_ends - say Melder depends on pip, pin pip where CI installs it, settle two stale backlog tickets

## Metadata
- Task ID: TASK-2026-10-24-ci_lane_loose_ends
- Story: none (standalone; the loose ends TASK-2026-10-24-ci_python_315_and_release_test_rerun flagged at closure)
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T21:14:14Z
- Updated: 2026-10-24T21:25:11Z

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
- from_state: draft
- to_state: in_progress
- transition_reason: opened and started on the owner's word (chat 2026-10-24, 15:07 MDT), quoted in Objective.

## Steps / Checklist
- [ ] Read `.github/ci_cd/`, the speed manifest, both probes and the tests that pin dependencies; record the plan.
- [ ] Item 1: the description and the README line.
- [ ] Item 2: pin pip in the speed manifest and both probes; `.github/ci_cd/` and the tests documents; tests.
- [ ] Item 3: close the 2026-10-04 cache temp-file task as superseded once 0.2.8266 is turned in.
- [ ] Item 4: reproduce the shared gauntlet's setup on the current tree; close or update that ticket.
- [ ] Release-note line; NOTICEs; closure; the bundles rebuilt last by whoever lands last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
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
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/github_workflows -q -p no:cacheprovider`
  - `python src/melder/_build_assets/_build_asset_runner.py --check`
  - `python llm_support/_builder.py --check --include-untracked`

## Risks / Rollback Notes
- The release note and the LLM bundles are shared with three landing lanes; edit the note by text anchor after a
  fresh read, and leave the rebuild to the last lander.
- Every edit is a few lines in a tracked file; git restores any of them.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

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
- Independent Review: none yet

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

## Context / Handoff Summary
- Scope: the four loose ends in Objective. State: in_progress, melder_2; nothing edited yet outside this ticket and
  its board row.
- Next: (1) read `.github/ci_cd/`, the speed manifest, both probes and the pin tests and record the plan; (2) items
  1 and 2; (3) items 3 and 4, the release-note line, closure.

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
