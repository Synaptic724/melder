# Task: Rebuild current release source and repository assets

## Metadata
- Task ID: TASK-2026-09-05-rebuild-current-release-assets
- Story: none (owner-requested regeneration)
- Status: review
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-06T00:11:17Z
- Updated: 2026-09-06T00:13:12Z

## Objective
Regenerate the current release's derived source and LLM assets through the existing builders,
then verify the same freshness checks used by GitHub Actions.

## Ticket Contract
- ENTRY_GATE: Owner requested the rebuild and renewed codex_1 certification; board routes here.
- EXECUTION_BOUNDARY: Existing builders, their generated outputs, and this task's coordination state.
- DEPENDENCIES: Current checkout inputs and existing source/repository build manifests.
- EXIT_GATE: Both freshness checks pass and the resulting generated-only product diff is inspected.
- FAILURE_ESCALATION: Stop if rebuilding requires source fixes, version changes, or publication.

## Scope Boundaries
- In scope: source build assets, LLM bundles/indexes/manifest, freshness and diff checks.
- Out of scope: runtime edits, test changes, dependency upgrades, commits, pushes, tags, or releases.
- Preserve the existing deletion of artifacts/release_candidate_20260905/.gitignore.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Both freshness checks pass, repeated repository generation is unchanged,
  and all eight product-file changes are generated outputs.

## Steps / Checklist
- [x] Confirm current version, branch, and pre-existing changes.
- [x] Check freshness, then run the source builder before the repository builder.
- [x] Verify both exact freshness checks and inspect generated diffs.
- [x] Record findings and return the task to owner review.

## Deliverables / Files
- src/melder/_build_assets/ generated outputs only.
- llm_support/ generated bundles, indexes, and manifest only.
- This ticket, attention_board.md, and mailbox_board.md for coordination.

## Validation
- Source builder --check: exit 0, all three assets current at 0.2.36.
- Repository builder --check: exit 0, all three corpus fingerprints and output proofs match.
- Repeated repository build: all corpora and manifest unchanged.
- git -c core.whitespace=cr-at-eol diff --check: exit 0.
- Runtime tests: Not run; this lane regenerates existing derived assets only.

## Risks / Rollback Notes
Run source generation first, then compile repository bundles against the final checkout inputs.
Do not include untracked files in LLM bundles or manually alter derived proofs.
Do not change the package version or restore/delete unrelated files.

## Applicable Anti-Patterns
- [x] No runtime repair or unrelated refactor in this lane.
- [x] No version inference: current source version was read directly.
- [x] No completion claim without successful freshness checks.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record actual builder results and changed paths, with one concrete next step per tranche.

## Notes
- DATETIME: 2026-09-06T00:11:17Z
  TYPE: FACT
  CLAIM: Current version is 0.2.36 on codex_features2. Before this task, the only product-independent
    change was deletion of the release-candidate scratch .gitignore; preserve it unchanged.
  EVIDENCE:
  - ../src/melder/__version__.py:1-12
  - git status --short --branch (2026-09-06T00:11:17Z)
  IMPACT: Rebuild current inputs, not the old 0.2.0 ticket's version or outputs.
  NEXT: Read the two asset workflows and run their freshness commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:12:10Z
  TYPE: PLAN
  CLAIM: Both reusable asset workflows prescribe --check and name the existing builders as
    regeneration commands. Use the available .venv_new Python 3.14 interpreter for both.
  EVIDENCE:
  - ../.github/workflows/build-src-assets.yml:26-36
  - ../.github/workflows/build-repo-assets.yml:20-31
  - .venv_new/Scripts/python.exe --version (Python 3.14.0)
  IMPACT: No workflow or builder changes are necessary to perform the requested rebuild.
  NEXT: Check both asset sets and regenerate through the prescribed commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:12:17Z
  TYPE: MEASURE
  CLAIM: Initial checks exit 1: all three source assets are stale at expected v0.2.36;
    only the LLM src fingerprint is stale. Tests and other corpus proofs already match.
  EVIDENCE:
  - .venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py --check
  - .venv_new/Scripts/python.exe llm_support/_builder.py --check
  IMPACT: Rebuild source assets first, then let the repository builder select changed corpora.
  NEXT: Run the source build-asset runner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:12:37Z
  TYPE: MEASURE
  CLAIM: Source builder succeeded: 452 agent entries, 629 guard entries, four system documents,
    all stamped 0.2.36. Five generated files changed. Besides stamps, the inventories now include
    CreationContextRebuild, which already exists as a tracked source file; this lane did not add it.
  EVIDENCE:
  - .venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py (exit 0)
  - git diff -- src/melder/_build_assets (five files, 12 insertions, 9 deletions)
  - git ls-files -- src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py
  IMPACT: Generated manifests reflect current tracked inputs; no runtime source was edited.
  NEXT: Run the repository builder and verify selective corpus regeneration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:12:52Z
  TYPE: MEASURE
  CLAIM: Repository builder succeeded and rewrote only the src bundle (585 files), its index,
    and manifest.json. Tests and other corpora were reported unchanged with matching proofs.
  EVIDENCE:
  - .venv_new/Scripts/python.exe llm_support/_builder.py (exit 0)
  - git diff --stat -- llm_support (three generated files)
  IMPACT: Selective rebuilding is working; unchanged corpora did not need regeneration.
  NEXT: Run both final freshness checks, an unchanged second repository build, and diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:13:12Z
  TYPE: MEASURE
  CLAIM: Both final freshness checks pass. A second repository build reports all corpora and
    manifest unchanged. Diff hygiene passes. Product changes are exactly five source-generated
    files and three LLM-generated files; no runtime, test, workflow, or version file changed.
  EVIDENCE:
  - .venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py --check (exit 0)
  - .venv_new/Scripts/python.exe llm_support/_builder.py --check (exit 0)
  - .venv_new/Scripts/python.exe llm_support/_builder.py (exit 0; UNCHANGED for all outputs)
  - git -c core.whitespace=cr-at-eol diff --check (exit 0)
  - git status --short and git diff -- llm_support/manifest.json
  IMPACT: Requested asset regeneration is complete and ready for owner review; no publication ran.
  NEXT: Owner reviews the generated changes before committing through the normal branch workflow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Rebuilt current assets for 0.2.36. Five source manifests/indexes and three LLM src files changed.
Both final freshness checks pass; tests/other corpus outputs are unchanged and a repeated repository
build is a no-op. Existing tracked CreationContextRebuild is now represented in the inventories/bundle;
this lane did not add or modify runtime source. Existing scratch .gitignore deletion was preserved.
No commit, push, version edit, test edit, or runtime repair occurred. Await owner acceptance.
