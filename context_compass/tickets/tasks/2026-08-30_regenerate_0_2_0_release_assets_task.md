# Task: Regenerate release assets for version 0.2.0

## Metadata
- Task ID: TASK-2026-08-30-regenerate-0-2-0-release-assets
- Story: none
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T22:44:27Z
- Updated: 2026-08-30T22:47:20Z

## Objective
Regenerate every committed source and repository asset invalidated by the
owner's version 0.2.0 change and prove both exact GitHub checks pass.

## Ticket Contract
- ENTRY_GATE: Owner requested deterministic regeneration; attention routes here.
- EXECUTION_BOUNDARY: Version/read-only diagnosis, canonical source build-asset
  runner, canonical LLM support builder, generated diffs, and ContextCompass tracking.
- DEPENDENCIES: Existing 0.2.0 version change and committed builders/manifests.
- EXIT_GATE: Both exact CI check commands pass and generated scope is inspected.
- FAILURE_ESCALATION: Stop on runtime/source changes beyond the owner's version
  edit, unexpected generated membership drift, or any publish/push requirement.

## Scope Boundaries
- In scope: generated manifests, payloads, indexes, LLM bundles, shared manifest.
- Out of scope: commits, pushes, tags, GitHub releases, or PyPI publication.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Canonical regeneration produced only expected derived
  proofs and both exact CI checks pass at version 0.2.0.

## Steps / Checklist
- [x] Confirm active version/branch and current worktree scope.
- [x] Run the source build-asset runner and inspect generated changes.
- [x] Run the LLM support builder and inspect selective regeneration.
- [x] Run both exact CI check commands.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding before continuing.

## Deliverables
- Current 0.2.0 source/repository generated assets with green checks.

## Files / Paths Impacted
- `src/melder/_build_assets/`
- `llm_support/`
- `context_compass/attention_board.md`
- This task.

## Validation
- `python llm_support/_builder.py --check`: pass; all corpora current.
- `python src/melder/_build_assets/_build_asset_runner.py --check`: pass;
  all three assets current at version 0.2.0.
- Selective LLM regeneration: source only; tests/other unchanged.
- Final product diff: eight generated files, 17 insertions/17 deletions.
- LLM EOL and diff hygiene: pass.

## Risks / Rollback Notes
- Regeneration must change derived outputs only; unexpected source changes stop the lane.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board sync.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [x] Applicable anti-pattern checks are clear or escalated.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - version-stamped build assets
  - LLM source corpus fingerprint
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: exact stale cause, generated scope, and CI-equivalent checks.

## Notes
- DATETIME: 2026-08-30T22:46:20Z
  TYPE: MEASURE
  CLAIM: Both exact CI checks pass. LLM second generation is a true no-op for
    all corpora/manifest. The existing source runner deliberately rewrites its
    five target files even when current, so their mtimes move while their bytes/
    diff remain unchanged; the subsequent check still reports all three 0.2.0
    assets current. LLM outputs are LF-only and diff hygiene passes.
  EVIDENCE:
  - `llm_support/_builder.py --check`
  - `src/melder/_build_assets/_build_asset_runner.py --check`
  - `git -c core.whitespace=cr-at-eol diff --check`
  IMPACT: The supplied GitHub failures are resolved locally with CI-equivalent commands.
  NEXT: Inspect final generated-only diff and return the task/attention route to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:45:48Z
  TYPE: FACT
  CLAIM: LLM regeneration is selective and current-policy counts remain stable:
    source 584/270,707 lines, tests 794/298,909, other 262/55,572. Only
    `llm_full_src.txt`, its index, and manifest changed (10 added/10 removed
    lines); tests and other outputs were byte-verified and not rewritten.
  EVIDENCE:
  - `llm_support/llm_full_src.txt`
  - `llm_support/llm_full_src_index.md`
  - `llm_support/manifest.json`
  IMPACT: The version/source move affects only the source corpus as designed.
  NEXT: Run both exact CI check commands, a no-op second build, EOL/diff hygiene,
    and final generated-path inventory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:45:18Z
  TYPE: FACT
  CLAIM: Source regeneration completes at version 0.2.0 with unchanged
    membership counts (452 agent entries, 628 bind-guard entries, four system
    documents). The exact diff is five generated manifest/index files and only
    seven added/seven removed lines for version/source/output proof stamps.
  EVIDENCE:
  - `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py:21-23`
  - `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:16-18`
  - `src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:21-23`
  IMPACT: Source assets are regenerated without membership or payload drift.
  NEXT: Run the LLM repository builder and require selective source-only output changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:44:50Z
  TYPE: FACT
  CLAIM: Active branch is `codex_features2`; canonical
    `src/melder/__version__.py` is already committed at 0.2.0, and the
    product working tree is clean. Only this regeneration task/board route is
    uncommitted. CI failures therefore reflect stale committed derived assets,
    not an incomplete local version edit.
  EVIDENCE:
  - `src/melder/__version__.py:1-12`
  - `git status --short --branch`
  IMPACT: Canonical regeneration can run without merging or changing runtime source.
  NEXT: Run the source build-asset runner once and inspect every generated path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:44:27Z
  TYPE: PLAN
  CLAIM: Confirm version/worktree, regenerate source assets through their
    canonical runner, regenerate only stale LLM corpora, inspect diffs, and run
    both CI commands verbatim.
  EVIDENCE:
  - Owner-supplied GitHub Actions failures, 2026-08-30T22:44:27Z
  IMPACT: Regeneration follows the same entrypoints CI instructs without manual edits.
  NEXT: Read the version and current status before writing generated files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Version 0.2.0 regeneration is complete. Five source manifest/index proof files
and the LLM source bundle/index/manifest changed; membership and payloads did
not drift. Both GitHub-equivalent checks pass. No commit, push, tag, release, or
publication occurred.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
