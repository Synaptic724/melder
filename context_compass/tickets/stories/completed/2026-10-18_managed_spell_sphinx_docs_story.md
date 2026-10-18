

# Story: A Sphinx page for managed spell pools, the release-note entry and the rebuild

## Metadata
- Story ID: STORY-2026-10-18-managed_spell_sphinx_docs
- Epic: EPIC-2026-10-18-managed_spell_examples_and_docs
- Status: done
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T21:14:51Z
- Updated: 2026-10-18T23:06:38Z
- Completed: 2026-10-18T23:06:38Z
- Summary: The Sphinx chapter docs/intermediate/managed-spells.md - registered in the curriculum after
  intermediate/ownership, linked from the level index, scopes.md and lessons 42-48 - with docs checks green (313
  pages) and one release-note bullet; the lane's rebuild waived by the owner.

## User Narrative
As a Melder user reading the documentation site, I want one page that explains managed spell pools - the modes,
the settings, leasing, releasing, resetting, the refusals and the teardown - with runnable examples behind it, so
that I can adopt them without reading the source.

## Value / MRP Alignment
Documentation is part of the API; the page states the contract the examples prove.

## Ticket Contract
- ENTRY_GATE: S2's examples and tests are green; the board row routes here.
- EXECUTION_BOUNDARY: a new page under `docs/` and its registrations (navigation and catalog files as
  `docs/maintaining.md` prescribes), one entry under `## Packaging and documentation` in
  `release_docs/next_version_release.md`, then the closure and the rebuild.
- DEPENDENCIES: STORY-2026-10-18-managed_spell_ux_examples; `docs/maintaining.md`; melder_0's landing and rebuild.
- EXIT_GATE: the Sphinx build passes with the page reachable; release-note entry; closure; rebuild with both checks
  OK.
- FAILURE_ESCALATION: a docs build tool missing or a check failing for reasons outside this lane - BLOCKER note,
  report to the owner; a rebuild collision - mailbox first.

## Requirements (Functional)
- The page covers every mode, setting, lifecycle step and refusal the examples cover, and links them.

## Requirements (Non-Functional)
- Follows the docs site's conventions in `docs/maintaining.md`; no claim beyond S1's map.

## Scope Boundaries
- In scope: the page, its registrations, the release note, the rebuild.
- Out of scope: other pages, beyond a link from where the existences are already listed if the conventions ask.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: exit gate met as the owner set it - the chapter builds and is reachable, the release-note
  entry is in, the examples are green on the current tree; the rebuild waived by the owner's directive
  (2026-10-18T23:01Z), which is also the acceptance.

## Dependencies / Related Work
- `docs/intermediate/scopes.md` (lists the existences); `docs/reference/glossary.md`.

## Tasks (Implementation Checklist)
- [x] Read `docs/maintaining.md` and the navigation/catalog files.
- [x] Write the page and register it.
- [x] Build the docs; save the log.
- [x] Release-note entry; close the stories and the epic; board sync.
- [x] NOTICE melder_0 (M2-17, M2-18, M2-19); the rebuild of build assets and LLM bundles and both `--check` runs
  waived by the owner's directive (2026-10-18T23:01Z) - not performed; melder_0's rebuild carries the changes.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- The page renders in the built site and is reachable from the navigation; the checks pass.

## Validation / Test Plan
- The documented Sphinx build; the two `--check` runs.

## UX / API / Data Notes
- None yet.

## Risks / Mitigations
- Sphinx missing in the VM: install from `docs/requirements.lock` in scratch.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No rebuild before the closure; no edit after the rebuild.

## Open Questions
- Resolved 2026-10-18: the page's place in the navigation - an authored curriculum chapter after
  intermediate/ownership (Decision Log).

## Decision Log
- 2026-10-18: the page is the authored curriculum chapter intermediate/managed-spells, placed after
  intermediate/ownership: its last section uses the dynamic posture and the ownership transfer that the chapters
  before it teach, and connected-subsystems stays the level's closing walkthrough. No navigation.toml entry -
  docs/maintaining.md puts guides in curriculum.toml and only standalone reference pages in navigation.toml.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/managed_spell_examples_20261018/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: epic closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_2; synaptic_python_developer; prose; this story; 2026-10-18T21:14:51Z
- Published By: UNKNOWN (local backend; no hosting service)
- Independent Review: none requested yet

## Notes
- DATETIME: 2026-10-18T21:14:51Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Page after the examples are green; the rebuild is the last write of the lane, after closure.
  EVIDENCE: context_compass/special_instructions/agent_contribution_guide.md:75-87
  IMPACT: Keeps the assets current and the checks green at hand-off.
  NEXT: Wait for S2.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T22:10:57Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The docs model (read whole: maintaining.md, navigation.toml, catalog.toml, curriculum.toml, conf.py and
    the builder's catalog, curriculum and navigation code): the catalog must list every numbered lesson of a
    level, so 42-48 join catalog.toml's intermediate sources now (S2's lessons make the docs check refuse catalog
    drift until they do). The page is an authored curriculum chapter, intermediate/managed-spells, source
    docs/intermediate/managed-spells.md with a myst.html_meta.description, lessons intermediate:42-48 and
    show_steps (lesson 42's main()); the level index gets one bullet, scopes.md a cross-link from its managed
    purge paragraph, seo.toml the page. Every claim comes from S1's map and S2's probe rows. Build on the cloud
    3.14t mirror (docs/ without .venv and _build, README.md, src/, UX_and_AIX_experiences/,
    architecture_and_design/) with docs/requirements.lock: the docs unit tests, build_docs.py check and build
    (-W) and check_site.py. Files named to melder_0 first (M2-17); the release-note entry and the rebuild wait for
    melder_0's rebuild-done NOTICE (M0-201).
  EVIDENCE:
  - docs/maintaining.md:90-120
  - docs/tools/example_catalog.py:107-141
  - docs/tools/curriculum.py:114-163
  - docs/tools/build_docs.py:84-165
  IMPACT: The page lands in the navigation with reciprocal lesson links, and the docs check passes again.
  NEXT: Register 42-48 in catalog.toml, then write the page on the mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:29:45Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-202 (melder_0's ACK of M2-16 and M2-17, 22:18:15Z) consumed after this agent's REONBOARD (context
    compaction): melder_0's docs/ sweep holds none of this lane's six docs/ files (catalog.toml, curriculum.toml,
    intermediate/managed-spells.md, intermediate/index.md, intermediate/scopes.md, seo.toml), so S3 goes ahead;
    the sweep's candidates are reference/glossary.md, reference/troubleshooting.md, advanced/worlds.md,
    advanced/inspection-walkthrough.md and intermediate/configuration.md, and melder_0 names a docs/ file before
    editing it. melder_0 now edits the existing UX_and_AIX_experiences/ files the one-object rule breaks, never
    lessons 42-48, test_managed_spell_probes.py or the concept map's managed section; its mirror run shows the
    same 17 pre-existing harness failures as S2's.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_sphinx_docs_story.md:132-155
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_ux_examples_story.md:171-196
  IMPACT: No docs/ write collision with melder_0; the release-note entry and the rebuild still wait for its
    rebuild-done NOTICE (M0-201).
  NEXT: Apply the registrations on the docs mirror (apply_s3_docs.py), then the docs unit tests,
    build_docs.py check and build (-W) and check_site.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:37:39Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S3's docs inputs pass every documented check on the cloud mirror of the current tree (CPython 3.14.6 with
    docs/requirements.txt; no device file under docs/, src/, UX_and_AIX_experiences/, README.md, release_docs/ or
    tests/ is newer than the mirror's tarball of 22:11:32Z): docs unit tests 60 OK; build_docs.py check "Navigation
    valid: 313 pages, 54 assets"; build (-W) "Built 313 pages", exit 0, its only stderr melder's GIL-mode
    UserWarning, as in the 312-page baseline; check_site "Site valid: 313 pages, 39253 local links; sources match";
    check_seo with the RTD canonical base: 0 errors and 303 warnings, every one "Missing nonempty description" on a
    page outside seo.toml's required list, none on the new page (title, description, canonical, one H1). The chapter
    sits after intermediate/ownership - its last section uses the dynamic posture and the transfer the chapters
    before it teach - and the level index, Full Contents, scopes.md and its neighbours' previous/next links reach it;
    every lesson 42-48 page links back to it, and its steps section shows lesson 42's main(). The page is CRLF, as
    its full-CRLF neighbours are; final bytes sha256 19505447ce0c7a68...; apply_s3_docs.py sha256 2f0a6d78c98979cc...
  EVIDENCE:
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/docs_unittests_final.txt:1-7
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/docs_check_final.txt:1-2
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/docs_build_final.txt:1-6
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/check_site_final.txt:1-2
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/check_seo_final.txt:1-3
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/docs_build_baseline.txt:1-6
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/check_site_baseline.txt:1-1
  IMPACT: The page and the four registrations can land on the device with the docs check green.
  NEXT: Commit the page, run apply_s3_docs.py from the repository root on the device, and compare the six files'
    sha256 with the mirror's.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:38:28Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S3's docs/ changes are on the device tree: docs/intermediate/managed-spells.md committed, and
    apply_s3_docs.py run from the repository root (python3 3.10) applied the curriculum chapter, the level-index
    bullet, the scopes.md cross-link and the seo.toml entry. All six docs/ files (the page, curriculum.toml,
    intermediate/index.md, intermediate/scopes.md, seo.toml, catalog.toml) now hash byte-for-byte to the mirror
    copies the MEASURE note validated, so those runs are runs of this tree's docs inputs.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_sphinx_docs_story.md:179-206
  - context_compass/artifacts/managed_spell_examples_20261018/scripts/apply_s3_docs.py:1-93
  IMPACT: The page is in the navigation of the tree the owner builds; the docs check stays green. The release-note
    entry, the closures and the lane's rebuild (build assets and LLM bundles, last) remain, after melder_0's
    rebuild-done NOTICE (M0-201).
  NEXT: NOTICE melder_0 (M2-18) that the six docs/ files landed, then prepare the 3.14 rebuild environment while
    waiting for its rebuild-done NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:45:21Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The lane's rebuild can run on the real tree from this agent's device VM: `uv python install 3.14` (uv
    0.12.13, already in the VM) installed CPython 3.14.7 under /tmp/m2_uv/python in 2.5 s, which corrects S1's
    finding that the VM had no route to 3.14. Both gates run read-only there with PYTHONDONTWRITEBYTECODE=1 and
    GIT_OPTIONAL_LOCKS=0 and leave no index.lock: the asset runner loads builders by path (no melder import, no
    cache write) and compares fingerprints on universal-newline reads; the LLM builder lists files with `git
    ls-files` and LF-normalizes what it reads. Every output under _build_assets/*/manifest|payloads and
    llm_support/ is LF on the device, which is what the VM writes, and os.replace over an existing file works in
    the connected folder without delete permission. Today both checks report STALE (assets: all three, expected
    v0.2.8256; bundles: src, tests, other), as they must before melder_0's landing and rebuild.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/rebuild_env_preflight_asset_check.txt:1-12
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/rebuild_env_preflight_llm_check.txt:1-8
  - src/melder/_build_assets/_build_asset_runner.py:147-361
  - llm_support/_builder.py:166-311
  IMPACT: No mirror round-trip for the final rebuild: build and check run in place, so the checks verify the
    owner's tree itself.
  NEXT: Wait for melder_0's rebuild-done NOTICE; then the release-note entry, the closures and the rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:49:00Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Lessons 42-48 and their probes are still green on the device tree as it stands now (__version__ 0.2.8256,
    before melder_0's notch and rebuild): an rsync copy under /tmp in this agent's device VM (src/,
    UX_and_AIX_experiences/, tests/, pyproject.toml; the tracked __melder_cache__ marker added back), CPython
    3.14.7t from uv with pytest 9.1.1: `pytest UX_and_AIX_experiences/pytest_examples -k managed` 55 passed with
    the GIL off and with it on; each lesson run as a script exits 0 in both modes, its output identical to S2's.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/preverify_managed_rows_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/preverify_managed_rows_gil1.txt:1-10
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/preverify_lessons_as_scripts_gil0.txt:1-49
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/preverify_lessons_as_scripts_gil1.txt:1-49
  IMPACT: Nothing landed since S2 has broken the lane's examples; the same run repeats on the tree after melder_0's
    rebuild-done NOTICE, before the closures.
  NEXT: Wait for melder_0's rebuild-done NOTICE.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:04:21Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-203 (melder_0's NOTICE, 22:55:41Z, re M2-18) consumed: melder_0's rebuild carries this lane's six docs/
    files, and its rebuild-done NOTICE follows that rebuild. Its S1 docs sweep edits only
    reference/glossary.md, reference/troubleshooting.md, advanced/inspection-walkthrough.md,
    intermediate/configuration.md and README.md's Frame Boundaries section - none of the six. Its rewrite of 15
    example files the one-object rule broke is on the tree (lesson text changes in beginner 18, 24, 30,
    intermediate 31, 37, advanced 02, 16, expert 11, 13, 16, 26), and it runs the docs checks on the whole change
    before its rebuild.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_sphinx_docs_story.md:179-206
  IMPACT: The docs runs above predate that rewrite; melder_0's own docs checks cover the combined tree. This lane's
    final examples run must use the tree with the rewrite.
  NEXT: Record the owner's directive (finish now, no rebuild for this lane).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:04:21Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's directive (chat, 2026-10-18T23:01Z): "ok please finish all those things off and skip build
    assets and llm bundles its not required since other agents are working". This lane therefore (1) adds its
    release-note entry now instead of after melder_0's rebuild-done NOTICE - M2-19 tells melder_0 before the edit,
    so it re-reads release_docs/next_version_release.md before writing it; (2) does not rebuild the build assets or
    the LLM bundles and runs neither --check: the rebuild item of this story's exit gate and the epic's is waived by
    the owner, and melder_0's rebuild (M0-203) carries this lane's docs and release-note changes; (3) reruns lessons
    42-48 and their probes on the current tree, then closes S3 and the epic with board and artifact sync.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-18_managed_spell_sphinx_docs_story.md:24-34
  - context_compass/special_instructions/agent_contribution_guide.md:75-87
  IMPACT: The lane closes without its own rebuild; the generated assets stay stale until melder_0's rebuild, which
    is the owner's accepted state, not an unrecorded skip.
  NEXT: Send M2-19, apply apply_s3_release_note.py on the device, rerun the examples on the current tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T23:06:38Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The release-note entry is in: apply_s3_release_note.py, run from the repository root on the device after
    M2-19 (23:04:33Z), inserted one eight-line bullet into `## Packaging and documentation` of
    release_docs/next_version_release.md directly above the closing rebuild line, and nothing else - the diff
    against the copy taken before the run is exactly those lines; the file stays LF; the header and the rebuild
    line ("rebuilt for 0.2.8256") are untouched, since this lane takes no notch and runs no rebuild.
  EVIDENCE:
  - release_docs/next_version_release.md:1063-1070
  - context_compass/artifacts/managed_spell_examples_20261018/scripts/apply_s3_release_note.py:1-52
  IMPACT: The running note records the chapter and the lessons; melder_0 re-reads the note before writing it
    (M2-19) and its rebuild carries the change.
  NEXT: Rerun lessons 42-48 and their probes on the current tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:06:38Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Lessons 42-48 and their probes are green on the current tree, which now carries melder_0's rewrite of 15
    example files (M0-203): a fresh rsync copy under /tmp in the device VM, CPython 3.14.7t from uv, pytest 9.1.1 -
    `pytest UX_and_AIX_experiences/pytest_examples -k managed` 55 passed with the GIL off and with it on (572
    deselected); every lesson exits 0 as a script in both modes, output identical to S2's; the lane's eight files
    hash as committed in S2 (4d25f247, 55db8c73, 8b512ba7, 66260ecf, a57f98ac, 27b47a8c, 6024ce52; probes
    de7cdb13).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/final_managed_rows_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/final_managed_rows_gil1.txt:1-10
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/final_lessons_as_scripts_gil0.txt:1-49
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/final_lessons_as_scripts_gil1.txt:1-49
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/run_started.txt:1-1
  IMPACT: The examples the page links still run as the page describes them; S3's exit gate, as the owner set it,
    is met.
  NEXT: Close S3, then the epic, with board and artifact sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T23:06:38Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S3 closed: exit gate met as the owner set it (DECISION note of 23:04:21Z) - the chapter builds and is
    reachable (MEASURE note of 22:37:39Z; the device files are byte-identical to the checked mirror), the
    release-note bullet is in, lessons 42-48 and their probes are green on the current tree, and the rebuild with
    its two --check runs is waived by the owner (not performed). ACCEPTANCE: the owner's directive (chat,
    2026-10-18T23:01Z, "finish all those things off"); VALIDATION: the docs runs and the final examples runs above;
    CHILDREN: none; ROUTING: the board row and its details go with the epic's closure. Open: the owner's answer on
    the root-held consumer teardown order (S1 RISK), and the stale failure-mode text in src_architecture and
    src_components, which melder_0 holds (M0-201).
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_sphinx_docs_story.md:179-206
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s3/final_managed_rows_gil1.txt:1-10
  - release_docs/next_version_release.md:1063-1070
  IMPACT: Users get a page with runnable, tested lessons behind every claim; the generated assets stay stale until
    melder_0's rebuild, as the owner accepted.
  NEXT: Close the epic.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
State: done - the chapter docs/intermediate/managed-spells.md and its registrations are on the tree (docs unit
tests, check, build -W, check_site and check_seo green on the checked mirror, 313 pages), the release-note bullet
is in `## Packaging and documentation`, and lessons 42-48 with their probes are green on the current tree. The
rebuild of build assets and LLM bundles was waived by the owner; melder_0's rebuild carries this lane's changes.
Open: the owner's answer on the root-held consumer teardown order; the stale failure-mode text in
src_architecture and src_components (melder_0, M0-201).
Update this view in place. Preserve historical Notes/comments and link unchanged context/full evidence.

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
