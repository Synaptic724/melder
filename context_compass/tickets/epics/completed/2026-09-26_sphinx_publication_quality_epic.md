# Epic: Keep Melder documentation buildable and improve search metadata

## Metadata
- Epic ID: EPIC-2026-09-26-sphinx-publication-quality
- Status: done
- Owner: codex
- Agent Name: seo_0
- Priority: p1
- Created: 2026-09-26T23:15:00Z
- Updated: 2026-09-27T00:32:45Z
- Completed: 2026-09-27T00:30:31Z
- Summary: Delivered build repairs and bounded SEO improvements at 0.2.77; owner accepted turn-in before the
  final asset rebuild.
- Target Window: current owner-directed documentation work
- Related Program/Initiative: public Sphinx documentation

## Problem / Opportunity
The owner authorized the corrected documentation work and requested an epic. Two newly reported
build blockers take priority: RTD public API selection omits UnresolvedInputError, and a Windows
Git checkout refuses long paths in the archived site-plan graph descriptors. Direct site inspection
also identified repeated browser-title text, absent descriptions, and one off-site guide link.

## MRP Alignment
Keep the current working site and its complete learning material. Repair build contracts and
improve generated metadata through their existing source owners, with reproducible verification.

## Ticket Contract
- ENTRY_GATE: Owner authorization, certified seo_0, active board route, linked stories/tasks.
- EXECUTION_BOUNDARY: Documentation sources/tools/tests, affected publication workflows, bounded
  long-path repair, ContextCompass tracking, and normal version/release/generated-asset bookkeeping.
- DEPENDENCIES: Existing reviewed source model and direct site inspection.
- EXIT_GATE: Required tasks verified and reviewed; owner accepts closure; boards synchronized.
- FAILURE_ESCALATION: Record evidence for unresolved build, platform, or scope assumptions.

## Goals / Non-Goals
- Restore reliable API selection and Windows checkout.
- Improve browser titles, local guide linking, descriptions, and appropriate SEO validation.
- Verify robots.txt exists and its sitemap works.
- No homepage redesign, duplicated tutorials, runtime API changes, automatic remote publication,
  or blanket changes to RTD version visibility.

## Scope Boundaries
- In scope: the linked stories and tasks below.
- Out of scope: unrelated active runtime work and the withdrawn homepage draft.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner explicitly requested turn-in before the final asset rebuild.

## Success Metrics / Requirements
- API inventory includes all intended public exports; docs model check passes.
- Windows checkout no longer fails on the reported archived paths.
- Existing visible homepage and guide bodies are retained except the specific local-link correction.
- Targeted metadata survives generation and passes real HTML checks.
- robots.txt and sitemap HTTP responses verified, with platform behavior documented.

## Stories (Required to Complete)
- [x] STORY-2026-09-26-repair-documentation-builds:
  stories/completed/2026-09-26_repair_documentation_builds_story.md
- [x] STORY-2026-09-26-refine-sphinx-discoverability:
  stories/completed/2026-09-26_refine_sphinx_discoverability_story.md

## Milestones / Tasks
- [x] Repair the reported build/checkout failures.
- [x] Apply bounded title, link, and description improvements.
- [x] Integrate appropriate SEO regression checks and document crawler behavior.
- [x] Verify local build and rendered results; record exact limits.

## Acceptance / Validation
- Run the existing docs model/unit/rendered-site checks with the locked Python 3.14 environment.
- Validate path repair through the relevant checkout mechanism or explicit measured path evidence.
- Inspect representative rendered pages; record real command results and remaining hosting limits.
- Owner confirms acceptance before any ticket moves to completed.

## Risks / Mitigations
- Shared repository: inspect current changes before edits and preserve peers' files/board rows.
- Archived graph descriptors carry authored history: preserve their bytes and traceability.
- RTD already generates robots.txt; custom replacement must not silently discard hidden-version rules.

## Decision Log
- 2026-09-26: Corrected scope approved by the owner's request to create an epic and track the work.
- 2026-09-26: New build errors precede SEO refinements.
- 2026-09-26: Live robots.txt and sitemap return HTTP 200; RTD-managed crawler file is retained.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_seo_review_20260926/
  - artifacts/sphinx_publication_quality_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner acceptance; retain verification evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Sphinx build contracts, publication, metadata and Windows checkout
- IF_UNKNOWN: none

## Noting Behavior
Record program decisions here; tactical source findings belong in child tasks.

## Notes
- DATETIME: 2026-09-26T23:15:00Z
  TYPE: PLAN
  CLAIM: Prioritize API-selection and Windows path failures, then the approved narrow SEO work.
  EVIDENCE: Owner's messages and RTD/checkout logs in this chat; reviewed proposal and site_inspection
    under artifacts/melder_seo_review_20260926/.
  IMPACT: No redesign or duplicate guide work; all implementation is tracked by child tasks.
  NEXT: Open TASK-2026-09-26-repair-docs-build-blockers and trace both reported failure paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:09:03Z
  TYPE: MEASURE
  CLAIM: The epic's implementation and local verification are complete. Final asset generation ran
    after the release edits, then source-asset and LLM checks both passed at 0.2.77.
  EVIDENCE:
  - artifacts/sphinx_publication_quality_20260926/verification.md
  - artifacts/sphinx_publication_quality_20260926/windows-checkout-result.json
  - release_docs/next_version_release.md
  IMPACT: Ready for owner review/commit and the normal publication flow. No homepage redesign.
  NEXT: Owner reviews the changes and accepts ticket closure or requests a follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:18:52Z
  TYPE: MEASURE
  CLAIM: Final compatibility check preserves the published late-binding-with-spellcontract fragment.
    All 60 docs tests pass; full HTML, site and SEO checks pass again. Source assets and LLM bundles
    were rebuilt after the final source/release edits; every freshness check passes at 0.2.77.
  EVIDENCE:
  - docs/_build/html/examples/intermediate/36-late-binding-with-spellcontract.html:177-177
  - artifacts/sphinx_publication_quality_20260926/verification.md
  - docs/tests/test_page_metadata.py
  IMPACT: Implementation is complete and ready for owner review/commit; nothing was pushed.
  NEXT: Owner accepts the epic or requests follow-up; optional description coverage remains explicit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-27T00:26:30Z
  TYPE: DECISION
  CLAIM: The owner explicitly accepted turn-in: "turn in your epic then rebuild the assets".
    Close this epic, both stories, all three implementation tasks and the associated starter review;
    archive the promoted SEO patch contracts and synchronize boards before any final asset rebuild.
  EVIDENCE:
  - Owner's explicit turn-in and rebuild instruction in this chat.
  - context_compass/artifacts/sphinx_publication_quality_20260926/verification.md:1-60
  - context_compass/attention_board.md:100-106
  IMPACT: Closure is authorized. Preserve retained evidence and unrelated work; release remains 0.2.77.
    The post-closure rebuild is the owner's explicit finalization step under this accepted epic.
  NEXT: Close the selected tickets and archive the promoted patches, then run both builders and checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:30:31Z
  TYPE: DECISION
  CLAIM: Owner accepted this work with "turn in your epic then rebuild the assets".
    Delivered build repairs and bounded SEO improvements at 0.2.77; owner accepted turn-in before the final
    asset rebuild.
  EVIDENCE:
  - Owner's explicit turn-in instruction in this chat.
  - context_compass/artifacts/sphinx_publication_quality_20260926/verification.md:1-60
  IMPACT: Closed with the accepted SEO ticket set; evidence retained and current board routes cleared.
    SEO patch contracts are promoted to docs/maintaining.md and archived under patches/completed.
  NEXT: Run the owner-requested final asset regeneration after the entire selected set is turned in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:32:45Z
  TYPE: MEASURE
  CLAIM: The seven accepted tickets and four promoted patch contracts were turned in before the
    source-asset runner started at 00:31:56Z. All three manifests were rebuilt at 0.2.77.
    The LLM builder confirmed all three bundles already current; both freshness checks passed.
  EVIDENCE:
  - context_compass/artifacts/sphinx_publication_quality_20260926/post_turn_in_assets.log:1-5
  - context_compass/artifacts/sphinx_publication_quality_20260926/post_turn_in_llm.log:1-6
  - context_compass/artifacts/sphinx_publication_quality_20260926/post_turn_in_asset_checks.log:1-10
  IMPACT: Owner-requested ordering is fulfilled. Release details and generated outputs agree at 0.2.77.
  NEXT: None; accepted local work is complete.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:38:43Z
  TYPE: MEASURE
  CLAIM: Owner requested only a rebuild after CI reported the other corpus stale.
    The LLM builder refreshed other (375 files) and manifest.json; src/tests were already current.
    The subsequent check passed for all three corpora; both commands exited 0.
  EVIDENCE:
  - .venv_new/Scripts/python.exe llm_support/_builder.py: actual output in this chat.
  - .venv_new/Scripts/python.exe llm_support/_builder.py --check: all three OK in this chat.
  IMPACT: Requested local regeneration is complete; the epic remains turned in.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work and evidence reviewed with owner.
- [x] Acceptance confirmed and board/artifact sync completed.

## Implementation Result
- Both child stories and all three implementation tasks are accepted and done.
- 60 documentation tests and 29 workflow contract tests pass.
- HTML: 301 pages; 36,609 local links/source-fidelity checks pass; SEO audit has zero errors.
- Nine required descriptions pass. The 292 remaining descriptions are optional warnings, recorded
  explicitly rather than treated as completed coverage.
- Windows Git checkout with long-path support disabled succeeds for all 20 relocated descriptors;
  their bytes and original-path mapping are preserved.
- ePub and PDF compile; PDF retains compiler layout warnings. Browser inspection confirms the
  existing homepage layout, the corrected local guide route, and the public error reference.
- Release notes are 0.2.77. Final source assets and all three LLM corpora were rebuilt after release
  edits, and both freshness checks pass.
- Changes are local and uncommitted; no remote CI run or deployment is claimed.


## Context / Handoff Summary
Accepted and turned in at 2026-09-27T00:30:31Z. Delivered build repairs and bounded SEO improvements at
  0.2.77; owner accepted turn-in before the final asset rebuild.
Verification evidence is retained in artifacts/sphinx_publication_quality_20260926/.
Post-closure source assets rebuilt; LLM outputs already current; both freshness checks passed at 00:32:22Z.
