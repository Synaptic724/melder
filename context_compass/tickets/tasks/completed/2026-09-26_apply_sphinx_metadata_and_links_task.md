# Task: Refine Sphinx metadata and local guide linking

## Metadata
- Task ID: TASK-2026-09-26-apply-sphinx-metadata-and-links
- Story: STORY-2026-09-26-refine-sphinx-discoverability
- Epic: EPIC-2026-09-26-sphinx-publication-quality
- Status: done
- Owner: codex
- Agent Name: seo_0
- Priority: p2
- Created: 2026-09-26T23:15:00Z
- Updated: 2026-09-27T00:32:45Z
- Completed: 2026-09-27T00:30:31Z
- Summary: Added nine descriptions, a short title suffix and the local configuration link while preserving
  existing content.

## Objective / Contract
- ENTRY_GATE: Build repairs verified; task routed and notes current.
- EXECUTION_BOUNDARY: docs/conf.py, existing page frontmatter, curriculum/catalog TOML and renderers,
  focused docs tests, maintaining guide, and required release bookkeeping.
- DEPENDENCIES: TASK-2026-09-26-repair-docs-build-blockers.
- EXIT_GATE: Correct titles/descriptions/local links in real HTML; existing content/layout preserved.
- FAILURE_ESCALATION: Stop on ambiguous ownership of metadata or an unexpected runtime change.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner explicitly requested turn-in before the final asset rebuild.

## Steps / Acceptance
- [x] Shorten html_title to Melder without changing the homepage heading.
- [x] Rewrite the known README configuration link to the matching Sphinx chapter during generation.
- [x] Add explicit descriptions through authored pages, chapter metadata and lesson metadata.
- [x] Test exact rendered descriptions/escaping and source preservation.
- [x] Run docs build/site validation and inspect representative pages.

## Validation
- Metadata milestone: 44 docs tests, full Sphinx build and site check passed.
- Final combined result: 60 docs tests, 301 pages, nine required descriptions, and browser checks pass.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/sphinx_publication_quality_20260926/
  - system_docs/patches/completed/sphinx_seo_2026_09_26/architecture_patch.md
  - system_docs/patches/completed/sphinx_seo_2026_09_26/component_patch_documentation_metadata.md
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Capture each meaningful implementation/validation result with evidence and a single next action.

## Notes
- DATETIME: 2026-09-26T23:15:00Z
  TYPE: PLAN
  CLAIM: Implement the revised metadata/link scope, not the withdrawn homepage patch.
  EVIDENCE: artifacts/melder_seo_review_20260926/improvement_proposal.md:1-133.
  IMPACT: Existing readers keep the same homepage, guide bodies, routes and example source.
  NEXT: Complete the build-blocker prerequisite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T23:29:20Z
  TYPE: PLAN
  CLAIM: Patch contracts authored and consumed in architecture/component/code-description order.
    Mapping: metadata component Interfaces -> pure PageMetadata formatter plus Lesson/chapter
    optional strings -> rendered-HTML escaping/ownership tests. Before/after -> html_title and
    known cross-link rewrite -> existing branding tests, generated route regression, browser inspection.
  EVIDENCE:
  - system_docs/patches/active/sphinx_seo_2026_09_26/architecture_patch.md
  - system_docs/patches/active/sphinx_seo_2026_09_26/component_patch_documentation_metadata.md
  IMPACT: Source owners remain explicit; malformed supplied values fail before source output replacement.
  NEXT: Implement the metadata helper, renderer inputs, selected descriptions and local link.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:33:19Z
  TYPE: FACT
  CLAIM: Implemented the pure metadata formatter, optional lesson descriptions and README-chapter
    descriptions with explicit source ownership. Nine selected pages now carry descriptions;
    html_title is Melder and the known cleanup configuration link rewrites locally. Visible page
    bodies remain the existing content. Added real-render escaping/ownership and local-link regressions.
  EVIDENCE:
  - docs/tools/page_metadata.py:1-39
  - docs/tools/curriculum.py
  - docs/tools/example_catalog.py
  - docs/tests/test_page_metadata.py
  - docs/tests/test_curriculum.py
  IMPACT: Metadata is authored in the actual source model and survives rebuilds; no new guide or
    homepage navigation was introduced. Generated example byte downloads remain source-owned.
  NEXT: Run the docs tests and full build, then inspect emitted metadata and local links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:39:47Z
  TYPE: MEASURE
  CLAIM: All 44 docs tests pass, including real Sphinx metadata escaping and source ownership.
    Full Sphinx build passes (301 pages); site check passes (36,607 links, source bytes match).
    Rendered homepage title is "A runtime you can build on — Melder"; reviewed descriptions and
    the generated cleanup-to-configuration link are present. Version/release header is 0.2.76.
  EVIDENCE:
  - docs/_build/site-check.json:1-6
  - docs/_build/html/index.html:7-18
  - docs/_build/html/beginner/cleanup.html:7-18
  - docs/_build/html/beginner/cleanup.html:171-171
  - docs/tests/test_page_metadata.py
  IMPACT: Metadata implementation is verified; integration checks can now require those descriptions.
  NEXT: Implement the adapted SEO checker and a single TOML policy listing the nine reviewed pages.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:30:31Z
  TYPE: DECISION
  CLAIM: Owner accepted this work with "turn in your epic then rebuild the assets".
    Added nine descriptions, a short title suffix and the local configuration link while preserving existing content.
  EVIDENCE:
  - Owner's explicit turn-in instruction in this chat.
  - context_compass/artifacts/sphinx_publication_quality_20260926/verification.md:1-60
  IMPACT: Closed with the accepted SEO ticket set; evidence retained and current board routes cleared.
    SEO patch contracts are promoted to docs/maintaining.md and archived under patches/completed.
  NEXT: Run the owner-requested final asset regeneration after the entire selected set is turned in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Accepted and turned in at 2026-09-27T00:30:31Z. Added nine descriptions, a short title suffix and the local
  configuration link while preserving existing content.
Verification evidence is retained in artifacts/sphinx_publication_quality_20260926/.
Post-closure source assets rebuilt; LLM outputs already current; both freshness checks passed at 00:32:22Z.
