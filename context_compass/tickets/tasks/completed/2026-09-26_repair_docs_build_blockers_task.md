# Task: Fix public API selection and Windows checkout failures

## Metadata
- Task ID: TASK-2026-09-26-repair-docs-build-blockers
- Story: STORY-2026-09-26-repair-documentation-builds
- Epic: EPIC-2026-09-26-sphinx-publication-quality
- Status: done
- Owner: codex
- Agent Name: seo_0
- Priority: p1
- Created: 2026-09-26T23:15:00Z
- Updated: 2026-09-27T00:32:45Z
- Completed: 2026-09-27T00:30:31Z
- Summary: Fixed UnresolvedInputError selection and shortened 20 archive paths with byte-preserving Windows
  checkout verification.

## Objective
Resolve both owner-reported failures with their underlying contracts intact.

## Ticket Contract
- ENTRY_GATE: Parent story/epic exist and this task has an active board row.
- EXECUTION_BOUNDARY: docs/api.toml, API selection source/tests, affected checkout workflows or
  bounded archived-path layout, and version/release/generated-asset bookkeeping if needed.
- DEPENDENCIES: Current source and owner build logs.
- EXIT_GATE: Repairs verified, evidence recorded, owner acceptance recorded.
- FAILURE_ESCALATION: Do not delete archived authored content or suppress inventory validation.

## Scope Boundaries
- In scope: Missing UnresolvedInputError selection; reported retired-descriptor path failures.
- Out of scope: Homepage redesign, runtime semantics, unrelated archived content or peer changes.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner explicitly requested turn-in before the final asset rebuild.

## Steps / Checklist
- [x] Read API export/manifest/validator and reproduce the selection refusal.
- [x] Repair selection without weakening the drift guard; verify.
- [x] Measure offending tracked paths and trace the checkout environment.
- [x] Apply a portable, preserving path/checkout repair and verify.
- [x] Record release/bookkeeping and relevant tests.

## Validation
- Reproduced the missing-export refusal, then verified the corrected 301-page model and full build.
- Seven focused reference tests passed; the final combined docs suite has 60 passing tests.
- Windows Git checkout-index with core.longpaths=false passed for 20 relocated, byte-identical files.
- Locked documentation dependencies were installed in docs/.venv for verification.

## Risks / Applicable Anti-Patterns
- [x] Preserve every archived descriptor's authored contents and traceability.
- [x] Keep API selection fail-closed for future missing exports.
- [x] Do not report remote CI success from local checks.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/sphinx_publication_quality_20260926/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Append source findings, decisions, measured checks and one next action before each new work unit.

## Notes
- DATETIME: 2026-09-26T23:15:00Z
  TYPE: FACT
  CLAIM: RTD PR-160 build at 9c0805c8cdfca59ba483b0c9051bbb1b75914a12 reports public selection
    missing UnresolvedInputError. Checkout also reports eleven filename-too-long paths beneath
    the completed override_site_plan_2026_09_26 retired_graph_descriptors tree.
  EVIDENCE: Owner's two pasted error logs in this chat on 2026-09-26.
  IMPACT: Build and checkout block publication independently of SEO changes.
  NEXT: Read the manifest, export validator, and Windows checkout workflow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T23:20:31Z
  TYPE: FACT
  CLAIM: Reproduced the RTD refusal with the current Python 3.14t docs model check. __all__ and
    its concrete import include UnresolvedInputError; docs/api.toml's errors group omits it.
    The inventory guard correctly refuses the mismatch. The archive contains 20 descriptor JSON
    files plus retired_edges.json; the longest relative path is 272 characters (317 locally).
    The completed S6 task deliberately retained all 42 authored nodes and their retired edges.
  EVIDENCE:
  - docs/tools/api_reference.py:24-69
  - docs/api.toml:52-56
  - src/melder/__init__.py:152-162
  - src/melder/__init__.py:201-271
  - context_compass/tickets/tasks/completed/2026-09-26_build_site_plan_lowering_task.md:2730-2777
  IMPACT: Add the real public error to the existing group. Per the owner's rename/delete permission,
    flatten the 20 archived descriptor filenames with collision-safe names and an old-path/hash map;
    keep descriptor bytes and retired_edges.json intact. No validator or runtime code change is needed.
  NEXT: Apply the manifest correction and flatten the archive, then verify source-model and checkout behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:22:32Z
  TYPE: FACT
  CLAIM: Added UnresolvedInputError to the existing public-errors group. Flattened all 20 retired
    descriptors to basename-plus-original-path-hash filenames, with archive_index.json mapping old
    paths and SHA256 values. Every moved descriptor is byte-identical; retired_edges.json stays put.
    The longest local archive path is now 218 characters, down from 317.
  EVIDENCE:
  - docs/api.toml:52-56
  - context_compass/system_docs/patches/completed/override_site_plan_2026_09_26/retired_graph_descriptors/archive_index.json
  - context_compass/artifacts/sphinx_publication_quality_20260926/retired_descriptor_relocation.json
  IMPACT: The two source-level causes are corrected without changing runtime behavior or discarding
    authored history. Python's initial venv ensurepip step failed and needs an isolated-environment repair.
  NEXT: Verify the docs model and a real Windows Git checkout with long-path support disabled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:24:06Z
  TYPE: MEASURE
  CLAIM: Docs model now passes with 301 pages and 54 assets. All seven reference tests pass.
    A real isolated Windows git checkout-index of the twenty relocated descriptors succeeds with
    core.longpaths=false; all twenty files match their pre-move SHA256 values. Main Git index unchanged.
  EVIDENCE:
  - context_compass/artifacts/sphinx_publication_quality_20260926/windows-checkout-result.json
  - docs/api.toml:52-56
  - Commands: .venv_new/Scripts/python.exe docs/tools/build_docs.py check;
    .venv_new/Scripts/python.exe -m unittest discover -s docs/tests -p test_references.py -v.
  IMPACT: Both reported root causes have local verification. Full rendering still requires the
    locked docs environment, now installing after an ensurepip temporary-directory ACL failure.
  NEXT: Run the full docs suite/build with the locked dependencies, then record release bookkeeping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:29:20Z
  TYPE: MEASURE
  CLAIM: Locked Python 3.14t docs environment installed. All 39 existing docs tests pass; full
    Sphinx build passes for 301 pages; check_site validates 36,606 links and canonical source bytes.
    Build-repair version is 0.2.75 with release note; final asset regeneration follows later epic tasks.
  EVIDENCE:
  - docs/api.toml:52-56
  - docs/_build/site-check.json:1-6
  - context_compass/artifacts/sphinx_publication_quality_20260926/windows-checkout-result.json
  - src/melder/__version__.py:12-12
  IMPACT: Both blocker repairs are locally verified; move this task to review and proceed with metadata.
  NEXT: Apply the linked metadata patch contract in the successor task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:30:31Z
  TYPE: DECISION
  CLAIM: Owner accepted this work with "turn in your epic then rebuild the assets".
    Fixed UnresolvedInputError selection and shortened 20 archive paths with byte-preserving Windows checkout verification.
  EVIDENCE:
  - Owner's explicit turn-in instruction in this chat.
  - context_compass/artifacts/sphinx_publication_quality_20260926/verification.md:1-60
  IMPACT: Closed with the accepted SEO ticket set; evidence retained and current board routes cleared.
    SEO patch contracts are promoted to docs/maintaining.md and archived under patches/completed.
  NEXT: Run the owner-requested final asset regeneration after the entire selected set is turned in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Accepted and turned in at 2026-09-27T00:30:31Z. Fixed UnresolvedInputError selection and shortened 20 archive
  paths with byte-preserving Windows checkout verification.
Verification evidence is retained in artifacts/sphinx_publication_quality_20260926/.
Post-closure source assets rebuilt; LLM outputs already current; both freshness checks passed at 00:32:22Z.
