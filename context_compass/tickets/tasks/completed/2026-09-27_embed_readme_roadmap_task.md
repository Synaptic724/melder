# Task: Place the roadmap artwork in the README

## Metadata
- Task ID: TASK-2026-09-27-embed-readme-roadmap
- Story: none; standalone README presentation change
- Status: done
- Owner: codex
- Agent Name: seo_0
- Priority: p2
- Created: 2026-09-27T14:22:37Z
- Updated: 2026-09-27T14:29:31Z
- Completed: 2026-09-27T14:28:08Z
- Summary: Embedded the supplied roadmap after the introduction, with full-size and detailed-plan links.

## Objective
Embed the supplied roadmap artwork where readers can see the project direction after the introduction
and before the learning guide. Keep the image accessible at full size and link the detailed roadmap.

## Ticket Contract
- ENTRY_GATE: Existing certification, explicit owner request, image and README inspected, active route.
- EXECUTION_BOUNDARY: README.md, normal version/release/generated assets, this task and board records.
- DEPENDENCIES: Existing staged roadmap image and expanded roadmap; existing README picture convention.
- EXIT_GATE: Image renders in context, links resolve to intended repository assets, docs model is valid;
  task is turned in and final source/LLM freshness checks pass.
- FAILURE_ESCALATION: Preserve concurrent runtime changes; record any current-file conflict before writing.

## Scope / Deliverables
- Add a Roadmap section after What Melder Is and before How to Read This, plus a top quick link.
- Use the supplied image unchanged and link roadmap/melder-roadmap-expanded.md.
- Keep local/GitHub image selection and the public PyPI fallback used by the existing banner.
- Record release/version 0.2.81 under the existing per-change rule, then rebuild assets last.
- Do not change roadmap content, runtime behavior, existing tutorial sections or remote publication.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Requested placement is implemented and verified; turn-in precedes final asset regeneration.

## Steps / Acceptance
- [x] Add the image, full-size link, detailed-roadmap link and quick navigation.
- [x] Verify rendered placement and image sizing; validate documentation source selection.
- [x] Update the active release notes and version without replacing peer changes.
- [x] Turn in the task, then regenerate source assets and LLM bundles and verify freshness.

## Validation
Use an actual local README render and the existing docs model check. No new tests for this image embed.
Run both existing asset freshness checks after the final regeneration.

## Risks / Applicable Anti-Patterns
- A relative image alone would not survive PyPI rendering; follow the existing picture/fallback pattern.
- Dense roadmap text needs a full-size view and a link to the readable detailed plan.
- Existing runtime changes and the user's staged roadmap files must remain intact.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/readme_roadmap_20260927/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain the render and build verification after closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record placement rationale, actual render checks and final build results with evidence.

## Notes
- DATETIME: 2026-09-27T14:22:37Z
  TYPE: DECISION
  CLAIM: Viewed the 2.8 MB roadmap image and read the README. Place it after the product introduction
    and before the learning routes. The current release file is release_docs/0.2.77.md with header
    0.2.80; next_version_release.md is an empty placeholder. Preserve the current release content.
  EVIDENCE:
  - README.md:1-290
  - roadmap/melder-roadmap-expanded.md:1-49
  - release_docs/0.2.77.md:1-3
  - src/melder/__version__.py:12-12
  IMPACT: The image is visible before the long tutorial, with the existing README distribution pattern.
  NEXT: Add the bounded README section and release entry, then render and validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T14:25:00Z
  TYPE: FACT
  CLAIM: Added the roadmap section before How to Read This, a quick link, the existing local/public
    picture pattern, and full-size/detailed-plan links. Rendered the README locally; the roadmap
    anchor and local asset paths resolve. Docs model check passes for 301 pages and 54 assets.
    Release header and source version are 0.2.81; peer release content is retained.
  EVIDENCE:
  - README.md:27-33
  - README.md:252-269
  - context_compass/artifacts/readme_roadmap_20260927/readme_preview.html
  - src/melder/__version__.py:12-12
  IMPACT: The bounded edit and source checks are complete; visual inspection remains before closure.
  NEXT: Inspect the rendered roadmap section, then turn in and run final asset regeneration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T14:28:08Z
  TYPE: MEASURE
  CLAIM: Browser inspection confirms the supplied PNG loads at 1672 x 941 and displays at 932 pixels
    wide with proportional height. The section, quick link and detailed-plan/full-size links render.
    Docs model check passes. Turn in before final regeneration under the owner's standing order.
  EVIDENCE:
  - context_compass/artifacts/readme_roadmap_20260927/verification.md:1-14
  - README.md:252-269
  IMPACT: README placement is complete; image and roadmap text remain unchanged.
  NEXT: Run source-asset and LLM builders and both freshness checks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T14:29:31Z
  TYPE: MEASURE
  CLAIM: After turn-in, all source assets rebuilt at 0.2.81. LLM corpora rebuilt from 576 src files,
    1019 test files and 378 other files. Both freshness checks pass; all four commands exited 0.
  EVIDENCE:
  - context_compass/artifacts/readme_roadmap_20260927/final_assets.log:1-15
  IMPACT: README placement, release details, task turn-in and final regeneration are complete.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Roadmap placed after the introduction; local render and docs model verified. Turned in at 2026-09-27T14:28:08Z.
Release 0.2.81 is recorded. Assets were rebuilt after closure and both freshness checks pass; no remote publication requested.
