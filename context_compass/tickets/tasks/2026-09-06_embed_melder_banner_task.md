# Task: Embed the approved Melder banner in README and documentation

## Metadata
- Task ID: TASK-2026-09-06-embed-melder-banner
- Story: none (owner-approved branding integration)
- Status: review
- Owner: codex
- Agent Name: codex_1
- Created: 2026-09-06T13:37:41Z
- Updated: 2026-09-06T14:27:09Z

## Objective
Use the approved richer upscaled banner as the README and Read the Docs homepage header,
remove the old mage emoji, and keep the existing documentation content and navigation intact.

## Ticket Contract
- ENTRY_GATE: Owner explicitly approved embedding the latest richer banner and removing the emoji.
- EXECUTION_BOUNDARY: README header, docs homepage presentation/template/CSS, one branding asset,
  targeted documentation validation, affected LLM corpus refresh, and ContextCompass coordination.
- DEPENDENCIES: Existing Sphinx/MyST pipeline and the approved 3966x1586 richer PNG.
- EXIT_GATE: Banner renders responsively on the README/docs homepage; docs build/link checks pass;
  affected generated proofs are current without overwriting another agent's changes.
- FAILURE_ESCALATION: Stop before runtime, workflow-policy, publication, or character-art changes.

## Scope Boundaries
- In scope: a web-ready copy of the approved image, readable alt text, homepage placement,
  preserved aspect ratio, and removal of the mage-emoji masthead.
- Out of scope: new artwork, face changes, dependency upgrades, commits, pushes, or hosted publication.
- Preserve workflows_1's existing CI/test/bundle edits and the pre-existing scratch .gitignore deletion.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: README local-source and public-fallback checks pass; generated corpus is current.

## Steps / Checklist
- [x] Inspect current README/docs opening and repository status.
- [x] Confirm static-asset staging and documentation build/validation commands.
- [x] Add the approved banner and scoped header/template styling.
- [x] Build and validate documentation and inspect desktop/mobile presentation.
- [x] Refresh only affected repository assets and report unpublished changes.

## Validation
39 documentation tests passed. Strict HTML build passed for 294 pages; local-link validation
passed for 35,496 links with staged sources matching. Desktop/mobile visual checks passed.
The other corpus was regenerated; all three corpus checks and all three source-asset checks pass.
Source/test bundles and indexes remain byte-identical to their pre-regeneration state.
git diff --check passes. Hosted rendering and publication were not performed.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_banner_20260906/ (desktop/mobile validation screenshots)
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: Remove validation screenshots after owner acceptance; product banner remains.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record image selection, exact integration boundary, generated-asset coordination and validation evidence.

## Notes
- DATETIME: 2026-09-06T13:37:41Z
  TYPE: FACT
  CLAIM: README still begins with the mage-emoji title; docs homepage has no banner. The theme
    already supports responsive images and has a homepage TOC injected ahead of page content.
    workflows_1 has existing dirty CI/test/LLM files; leave their source/test changes intact.
  EVIDENCE:
  - README.md:1-27
  - docs/index.md:1-20
  - docs/_static/melder.css:12-34
  - docs/_templates/page.html:1-11
  - git status --short --branch (2026-09-06T13:37:41Z)
  IMPACT: This is a presentation-only integration, not a runtime or workflow redesign.
  NEXT: Check the documentation staging pipeline and choose the canonical web asset location.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T13:47:54Z
  TYPE: DECISION
  CLAIM: Use one 3966x1586 high-quality JPEG derived from the approved richer PNG, preserving
    the original and retaining full dimensions. README uses an absolute public raw image URL;
    Sphinx reads the same file locally from its existing _static directory. Put the homepage
    banner in page.html before the body, replacing only that page's leading TOC. Keep index.md
    and all narrative text unchanged. Add focused template-render tests to the existing docs suite.
  EVIDENCE:
  - docs/conf.py:58-73
  - docs/tools/build_docs.py:194-263
  - docs/_templates/page.html:1-11
  - docs/tests/test_build_docs.py:1-186
  - .github/workflows/docs.yml:25-39
  IMPACT: No builder, navigation, runtime, workflow, or handbook-source change is needed.
    The source test interpreter lacks Sphinx; locate the already-created documentation environment.
  NEXT: Prepare the image and apply the scoped README/template/CSS/test edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T13:53:40Z
  TYPE: FACT
  CLAIM: README now uses the shared banner in place of the emoji heading. The page template
    renders it before homepage content and preserves TOCs on other pages; responsive CSS preserves
    aspect ratio. Three template tests cover homepage, lesson, and configured-root behavior.
    The web JPEG retains 3966x1586 dimensions at quality 95 with 4:4:4 color sampling, 2,147,896 bytes
    versus the approved 7,068,522-byte PNG. The master image remains untouched.
  EVIDENCE:
  - README.md:1-7
  - docs/_templates/page.html:1-16
  - docs/_static/melder.css:33-35
  - docs/tests/test_build_docs.py:145-186
  - docs/_static/branding/melder-banner.jpg
  IMPACT: Only the docs presentation and test surface changed. A previous foundation task identifies
    the documentation environment at artifacts/rtd_probe_20260904/.venv; no dependency upgrade is needed.
  NEXT: Run documentation contract tests and the strict site build with that environment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T13:56:05Z
  TYPE: MEASURE
  CLAIM: The existing documentation environment is Python 3.14.0 with Sphinx 9.1.0.
    All 39 documentation tests pass, including the three new homepage-branding contracts.
    Navigation check accepts 294 pages and 54 declared public assets.
  EVIDENCE:
  - artifacts/rtd_probe_20260904/.venv/Scripts/python.exe -m unittest discover -s docs/tests -q
  - artifacts/rtd_probe_20260904/.venv/Scripts/python.exe docs/tools/build_docs.py check
  IMPACT: No environment installation or dependency change was needed. Template behavior is verified.
  NEXT: Run the strict full HTML build and validate its generated links and image resource.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:11:19Z
  TYPE: MEASURE
  CLAIM: Before compaction, the strict HTML build completed successfully for 294 pages and
    check_site.py accepted 35,496 local links with staged sources matching. The copied site JPEG
    matched the branding asset hash. Re-onboarding is complete and the owner recertified codex_1.
  EVIDENCE:
  - docs/tools/build_docs.py build (prior turn: exit 0, 294 pages)
  - docs/tools/check_site.py (prior turn: exit 0, 35,496 local links)
  - docs/_build/html/index.html:106-114
  - docs/_static/branding/melder-banner.jpg
  IMPACT: The presentation change builds cleanly. No runtime, workflow, or artwork changes are needed.
  NEXT: Inspect desktop/mobile layouts, then refresh only the affected other corpus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:14:00Z
  TYPE: DECISION
  CLAIM: Final diff contains only the approved README header, homepage template, responsive CSS,
    and three focused template tests. The LLM builder supports an other-only regeneration and
    excludes ContextCompass, JPEG, HTML and CSS; README and docs tests are affected text inputs.
    Capture local desktop/mobile site screenshots with an isolated headless browser, without
    using a personal browser profile or accessing a hosted service.
  EVIDENCE:
  - README.md:1-7
  - docs/_templates/page.html:1-16
  - docs/_static/melder.css:33-35
  - llm_support/_builder.py:62-107
  - llm_support/_builder.py:703-767
  IMPACT: Only the other corpus needs regeneration. Preserve src/tests corpus proofs and all CI edits.
  NEXT: Render the built homepage at desktop and mobile widths and inspect both images.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:15:07Z
  TYPE: FACT
  CLAIM: The isolated browser launch was blocked by the Windows execution sandbox with spawn EPERM.
    No page was rendered and no screenshot was produced. Documentation build/test results remain valid.
  EVIDENCE:
  - Local Playwright validation command (spawn EPERM before page creation)
  IMPACT: Visual validation is not complete; this is an execution permission issue, not a layout failure.
  NEXT: Request an elevated sandbox run of the same isolated, local-only browser validation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-06T14:15:07Z
  TYPE: MEASURE
  CLAIM: The approved elevated local browser run passed. At 1440px the full banner renders
    1024x409.48; at 390px it renders 338.25x135.27. Both preserve its aspect ratio with no
    horizontal overflow. Visually inspected both screenshots: title and both characters remain
    visible, with clean spacing before the unchanged heading. The beginner page keeps its TOC
    and does not repeat the homepage banner. The isolated browser was closed after validation.
  EVIDENCE:
  - artifacts/melder_banner_20260906/homepage-1440.png
  - artifacts/melder_banner_20260906/homepage-390.png
  - docs/_templates/page.html:1-16
  IMPACT: Desktop/mobile documentation presentation is validated without hosted publication.
  NEXT: Rebuild the other corpus, verify all corpus proofs, and review the final scoped diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:16:51Z
  TYPE: MEASURE
  CLAIM: Regenerated only the other corpus (354 inputs). Full corpus verification passes for
    src, tests and other. Source/test bundles and indexes were hash-compared before/after and
    are unchanged. All three source assets report current for v0.2.36. git diff --check passes.
    The source and built-site JPEG hashes match; the richer PNG retains its pre-integration hash.
  EVIDENCE:
  - .venv_new/Scripts/python.exe llm_support/_builder.py --corpus other (exit 0)
  - .venv_new/Scripts/python.exe llm_support/_builder.py --check (exit 0)
  - .venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py --check (exit 0)
  - git diff --check (exit 0)
  - docs/_static/branding/melder-banner.jpg
  - docs/_build/html/_static/branding/melder-banner.jpg
  IMPACT: Integration is ready for owner review with generated proofs current. The README uses
    the existing prod-based public URL convention; the new image must reach prod before that
    remote image URL resolves. No commits, pushes, runtime edits, or hosted publication occurred.
  NEXT: Owner reviews the banner placement and accepts the documentation-only change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:20:11Z
  TYPE: FACT
  CLAIM: Owner reports a broken README preview. The image currently uses a public prod URL,
    although its JPEG is still local. README.md is also the package description, so replacing
    it with only a relative URL would leave a different rendering problem on PyPI.
  EVIDENCE:
  - README.md:1-7
  - pyproject.toml:9-9
  - docs/_static/branding/melder-banner.jpg
  IMPACT: Correct README image selection for local viewing while preserving a public fallback.
    Read the Docs already uses its local static copy and needs no further layout changes.
  NEXT: Select and validate a minimal local-image/public-fallback README markup change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:23:18Z
  TYPE: DECISION
  CLAIM: Use a picture element with a repository-relative source and the existing absolute img
    fallback. GitHub documents picture support and relative images; PyPA's current sanitizer
    permits picture/img but removes source, retaining the public fallback on PyPI. No packaging
    hook, second README, runtime change, or dependency is needed.
  EVIDENCE:
  - https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
  - https://raw.githubusercontent.com/pypa/readme_renderer/main/readme_renderer/clean.py:15-58
  - README.md:1-7
  IMPACT: Local and branch previews can use the checked-out image without waiting for a prod push.
  NEXT: Replace the README image markup and validate local-source selection in the browser.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:26:00Z
  TYPE: MEASURE
  CLAIM: The actual README header was rendered with MarkdownIt and loaded in an isolated browser.
    Its banner selected the local repository JPEG (3966x1586) with zero public-banner requests.
    Removing source, as the current PyPA sanitizer does, selected the retained absolute fallback;
    that request was intercepted with the local image, not fetched or published. All 39 docs tests pass.
  EVIDENCE:
  - README.md:1-11
  - artifacts/melder_banner_20260906/readme-local.png
  - Local MarkdownIt/Playwright source-selection check (exit 0)
  - Documentation environment: python -m unittest discover -s docs/tests -q (39 passed)
  IMPACT: Standard local HTML preview works without a pushed asset; fallback selection is preserved.
    The Codex file preview was queued for reopening; its own renderer was not directly inspected.
  NEXT: Refresh the affected other corpus and return the README adjustment for owner review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:27:09Z
  TYPE: MEASURE
  CLAIM: The other corpus was regenerated after the README markup change; src, tests and other
    fingerprint/output checks all pass. Owner responded positively to the result. No commits,
    pushes, additional artwork edits, packaging changes or Read the Docs changes were made.
  EVIDENCE:
  - llm_support/_builder.py --corpus other (354 inputs, exit 0)
  - llm_support/_builder.py --check (all three corpora pass, exit 0)
  - README.md:1-11
  IMPACT: The README follow-up is complete and available for review; source/test corpora stay untouched.
  NEXT: Await owner direction; close the ticket only upon explicit closure acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Approved richer banner is embedded in README and the Sphinx homepage; the mage emoji is removed.
The original image is unchanged. The README now uses a local picture source with an absolute public
fallback; local selection and fallback behavior passed browser checks. The other corpus is current.
Docs tests pass (39); prior strict HTML/link/desktop/mobile checks passed, and RTD code is unchanged.
Only the other corpus was rebuilt; concurrent CI edits remain.
The local desktop preview is saved in artifacts/melder_banner_20260906/homepage-1440.png;
the mobile preview is homepage-390.png in the same directory. Await owner acceptance.
Do not commit, push, publish, regenerate artwork, or close the ticket without owner acceptance.
