# Task: Replace the homepage slogan with the descriptive runtime heading

## Metadata
- Task ID: TASK-2026-09-27-replace-homepage-slogan
- Story: none; follow-up to EPIC-2026-09-26-sphinx-publication-quality
- Status: done
- Owner: codex
- Agent Name: seo_0
- Priority: p2
- Created: 2026-09-27T01:25:32Z
- Updated: 2026-09-27T01:30:51Z
- Completed: 2026-09-27T01:29:33Z
- Summary: Descriptive homepage heading and preserved old anchor verified; release details updated to 0.2.78.

## Objective
Replace the visible homepage slogan with "A dependency graph runtime for Python", the earlier
proposed wording the owner expected, while preserving the existing page structure and guides.

## Ticket Contract
- ENTRY_GATE: Existing certification and explicit owner correction; active board route.
- EXECUTION_BOUNDARY: docs/index.md, version/release bookkeeping, generated docs/assets and tracking.
- DEPENDENCIES: Completed Sphinx publication epic; existing metadata and publication checks.
- EXIT_GATE: New heading/title rendered, previous heading link preserved, checks pass, assets rebuilt last.
- FAILURE_ESCALATION: Record any real build failure or concurrent source/version conflict before continuing.

## Scope Boundaries
- In scope: Homepage H1 and its old fragment; release 0.2.78; normal generated outputs.
- Out of scope: Homepage layout, guide content, new runtime behavior and remote publication.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner-requested correction verified and turned in before final asset regeneration.

## Steps / Acceptance
- [x] Replace the heading and preserve a-runtime-you-can-build-on as an explicit target.
- [x] Record the change in the release and advance the patch version per the owner's standing rule.
- [x] Build Sphinx and verify rendered heading/title/old anchor plus site/SEO checks.
- [x] Turn in the task, then rebuild source assets and LLM bundles and check freshness.

## Deliverables / Files
- docs/index.md
- src/melder/__version__.py
- release_docs/next_version_release.md
- Existing generated documentation, source-asset and LLM outputs.

## Validation
Sphinx build passed for 301 pages. Site check passed for 36,609 links; SEO has zero errors and
292 existing optional-description warnings. Rendered H1/title and the old fragment passed.
No new tests or runtime test reruns for this text-only change. HTML archive regenerated.

## Risks / Applicable Anti-Patterns
- Preserve the published fragment when changing the H1.
- Keep release and generated version stamps consistent; build assets after source/tracking edits.
- Do not claim the live RTD site changed before publication.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/sphinx_homepage_heading_20260927/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain build and HTML verification evidence after turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Keep verified findings and results here; preserve earlier epic history and record this correction separately.

## Notes
- DATETIME: 2026-09-27T01:25:32Z
  TYPE: DECISION
  CLAIM: The owner expected the slogan replacement. Current docs/index.md retains the old H1;
    docs/conf.py already sets html_title to Melder. Change only the H1 and preserve its old target.
  EVIDENCE:
  - docs/index.md:1-16
  - docs/conf.py:55-57
  - Owner's current correction and earlier descriptive-heading proposal in this chat.
  IMPACT: Distinguish the heading correction from the previously rejected homepage redesign.
  NEXT: Apply the H1/anchor and release/version edits, then build and check the real HTML.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T01:27:00Z
  TYPE: FACT
  CLAIM: Homepage H1 now identifies the Python dependency graph runtime. The old heading target is
    explicit, and the release/header bookkeeping advances to 0.2.78. No layout or guide changes.
  EVIDENCE:
  - docs/index.md:1-18
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  IMPACT: Source correction is complete; generated HTML and asset stamps still need rebuilding.
  NEXT: Build HTML with the public canonical base and verify H1/title, old fragment and existing checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T01:29:33Z
  TYPE: MEASURE
  CLAIM: Built all 301 pages. Site checks pass for 36,609 links and source fidelity; SEO has zero
    errors and the existing 292 optional-description warnings. Rendered title/H1 use the descriptive
    heading and the previous fragment resolves. Turn in before the final asset build, as requested.
  EVIDENCE:
  - context_compass/artifacts/sphinx_homepage_heading_20260927/html_build.log:1-1
  - context_compass/artifacts/sphinx_homepage_heading_20260927/site_check.log:1-1
  - context_compass/artifacts/sphinx_homepage_heading_20260927/seo_check.log:1-2
  - context_compass/artifacts/sphinx_homepage_heading_20260927/rendered_heading.txt:1-7
  IMPACT: The requested heading correction is verified locally and release details are complete.
  NEXT: Rebuild source assets and LLM bundles, then run both freshness checks as finalization.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T01:30:51Z
  TYPE: MEASURE
  CLAIM: After turn-in, all three source-asset manifests rebuilt at 0.2.78. The LLM builder refreshed
    src (576 files), other (375 files) and the manifest; tests already matched. Both freshness
    checks passed. All four commands exited 0; only excluded ContextCompass records follow.
  EVIDENCE:
  - context_compass/artifacts/sphinx_homepage_heading_20260927/final_assets.log
  IMPACT: Requested correction, release details, task closure and final asset generation are complete.
  NEXT: None; normal commit/publication applies the homepage correction to the hosted site.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Turned in after verifying the requested heading correction and retained fragment. Release is 0.2.78.
Post-closure assets and LLM bundles are current; both checks pass. The live site updates through the normal publication flow.
