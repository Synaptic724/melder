# Task: Audit complete documentation coverage and reader workflows

## Metadata
- Task ID: TASK-2026-09-04-rtd-quality-audit
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-quality-and-launch
- Story Path: ../stories/2026-09-04_rtd_quality_and_launch_story.md
- Status: in_progress
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-05T11:55:00Z

## Objective
Verify all four levels, complete contents, source/example/API coverage, accessible reading, search, and downloads with a requirements-to-evidence matrix.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: Docs-specific validation, existing example/probe runs, browser/download inspection, and defects routed to the owning content/build task.
- DEPENDENCIES: S1-S8 outputs; local checks may begin before hosted access is available, with hosted results tracked separately.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner explicitly requested completing the remaining documentation implementation
  and verification before considering the program finished.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] Every numbered lesson and selected public API item has a disposition.
- [ ] No unexplained missing pages, duplicate IDs, or broken local links remain.
- [ ] Current code/outcome claims match source and actual example runs.
- [ ] Mobile/keyboard/zoom/diagram/code workflows are reviewed.
- [ ] Hosted-dependent checks remain explicitly pending until verified.

## Validation
- Not run. Implementation task just created.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-05_rtd_final_quality_audit.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Audit complete documentation coverage and reader workflows
- IF_UNKNOWN: none

## Noting Behavior
- Finish a coherent read/work unit and append evidence, impact, and one next action.
- Keep notes append-only; label unverified claims explicitly.

## Notes
- DATETIME: 2026-09-04T22:07:46Z
  TYPE: PLAN
  CLAIM: Implement this bounded part of the accepted documentation program under its existing story.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - Owner implementation instruction on 2026-09-04.
  IMPACT: The complete program now has explicit execution tasks and dependency boundaries.
  NEXT: Activate this task when its dependency milestone is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T11:55:00Z
  TYPE: DECISION
  CLAIM: Activate the remaining S9 audit under the owner's explicit completion instruction. Review
    desktop/mobile/keyboard/zoom, examples and empty filters, search, code/diagrams, downloads,
    canonical/version behavior, and public-source coverage. Fix concrete documentation defects.
    Consume codex_1's notice: runtime/replay and disposal docs are changing; that lane will regenerate
    source assets and LLM corpora. Avoid competing asset regeneration while it runs.
  EVIDENCE:
  - tickets/tasks/2026-09-04_rtd_beginner_content_task.md
  - artifacts/2026-09-05_rtd_local_build_validation.md
  - tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md
  - Owner instruction to finish all remaining documentation work.
  IMPACT: Local UI/content review can proceed while the runtime lane settles. Verify actual RTD
    project access instead of assuming its setup; owner retains every commit and push.
  NEXT: Establish the requirements-to-evidence audit and inspect local/browser plus hosted availability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:06:59Z
  TYPE: FACT
  CLAIM: The public https://melder.readthedocs.io/en/latest/ URL displays RTD's Documentation page
    not found response in the browser. Automatic approval review rejected opening the advertised
    project dashboard because private account/project access was not explicitly authorized.
    Requested the actual project URL/branch and explicit read-only dashboard permission asynchronously.
    Local source review found the existing navigation observer, catalog filters, templates, and
    download/runbook surfaces; deterministic site report has zero errors at 294 declared pages.
  EVIDENCE:
  - Browser observation of https://melder.readthedocs.io/en/latest/.
  - Automatic review rejection of https://app.readthedocs.org/projects/melder/.
  - docs/_static/navigation.js:1-14
  - docs/_static/catalog.js:1-37
  - docs/_build/site-check.json:1-6
  IMPACT: Public live-version verification is genuinely unfinished. Do not bypass the dashboard
    rejection or infer settings. Continue all independent local quality checks while awaiting input.
  NEXT: Exercise the homepage/catalog/API on desktop and narrow viewports, including keyboard controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:21:46Z
  TYPE: FACT
  CLAIM: Reproduced two accessibility issues. Sphinx-design's stretched card link has zero height,
    so our generic focus outline renders as a narrow line below the card. At 375px, pressing Tab
    focuses a closed-sidebar button at x=-294px. The closed drawer remains keyboard-focusable.
    Native pointer activation of the example card succeeds; its earlier locator failure was the
    zero-height anchor, not a broken URL. ePub contains no JavaScript assets or index script tags.
  EVIDENCE:
  - docs/_static/melder.css:19-30
  - docs/_static/navigation.js:1-14
  - docs/_templates/layout.html:8-15
  - Browser geometry/focus observations at desktop and 375x812 viewport.
  - Native ePub archive index/asset inspection.
  IMPACT: Route the navigation/focus correction through S1. Add a skip link, hide closed mobile
    drawer controls from focus, outline the whole focused card, and manage Escape/open/close focus.
  NEXT: Implement and verify the bounded S1 navigation correction, then resume this audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:02:41Z
  TYPE: MEASURE
  CLAIM: S1 focus/contrast repairs are in review. Catalog browser checks passed: Beginner selects
    41/133; Beginner + Lifetimes/cleanup + disposal selects five named lessons; reload preserves all
    filters. An impossible query shows 0/133 through a polite live status; keyboard Clear filters
    restores all 133 and removes query parameters. Filters reflow to one column at 375px without
    page overflow. A strict no-custom-JS build keeps all 133 lessons and full contents usable at 320px.
  EVIDENCE:
  - tickets/tasks/2026-09-04_rtd_site_foundation_task.md
  - docs/_static/catalog.js:1-37
  - Browser checks on examples/index.html at local ports 8765/8766.
  IMPACT: Core reader navigation and catalog workflows are verified. Native 200% zoom and copied-byte
    readback are explicit browser-tool limits, while public RTD verification is still blocked.
  NEXT: Verify Sphinx search, diagram/code interaction, and complete source/API inventory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:11:00Z
  TYPE: MEASURE
  CLAIM: Local Sphinx search returns glossary/API/example results for SpellSpace; following the
    exact SpellSpace result opens the rendered signature/contracts page. Cleanup returns the public
    cleanup methods; request scope returns guides including Scope Work and Resources and lifetime
    guidance. An impossible query renders Search Results with explicit no-match guidance.
  EVIDENCE:
  - Browser search.html queries SpellSpace, cleanup, request scope, and no_such_melder_topic_7q9.
  - Browser reference/api/resolution/spellspace.html navigation from its exact search result.
  IMPACT: Local API/task/no-result search flows pass independently of the still-unverified RTD addon.
  NEXT: Verify diagram/code interactions and reconcile the final publication inventory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Defined task awaiting its dependency milestone.
Verify all four levels, complete contents, source/example/API coverage, accessible reading, search, and downloads with a requirements-to-evidence matrix.
