# Task: Audit complete documentation coverage and reader workflows

## Metadata
- Task ID: TASK-2026-09-04-rtd-quality-audit
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-quality-and-launch
- Story Path: ../stories/2026-09-04_rtd_quality_and_launch_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-05T14:09:36Z

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
- from_state: in_progress
- to_state: review
- transition_reason: Local audit and corrections are complete; hosted launch and documented manual
  browser checks remain explicit, with current evidence in the final audit artifact.

## Steps / Checklist
- [x] Read the exact inputs and record one bounded implementation decision.
- [x] Route needed corrections through the existing S1/S8 patch/task contracts.
- [x] Implement the scoped audit with notes before the next tranche.
- [x] Validate meaningful behavior/content and record actual outcomes and tool limits.
- [x] Synchronize parent story and hand off; formal acceptance remains open.

## Acceptance Criteria
- [x] Every numbered lesson and selected public API item has a disposition.
- [x] No unexplained missing pages, duplicate IDs, or broken local links remain.
- [x] Current code/outcome claims match source and actual example runs.
- [ ] Mobile/keyboard/zoom/diagram/code workflows are reviewed.
- [x] Hosted-dependent checks remain explicitly pending until verified.

## Validation
- Current evidence is in artifacts/2026-09-05_rtd_final_quality_audit.md.
- 36 docs tests and all 133 lessons pass across the normal run and one unchanged sandbox-free retry.
- 294 pages, 35,499 links, complete source/API inventory, and final offline/staged outputs pass.
- Native 200% zoom and exact clipboard payload readback could not be verified with this browser tool.
- Hosted RTD checks remain blocked; no service success is inferred from local simulation.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-09-05_rtd_final_quality_audit.md
  - artifacts/rtd_validation_20260904/final_inventory_20260905.json
  - artifacts/rtd_validation_20260904/final_docs_tests_20260905.log
  - artifacts/rtd_validation_20260904/final_examples_20260905.log
  - artifacts/rtd_validation_20260904/final_examples_20260905.xml
  - artifacts/rtd_validation_20260904/final_protocol_retry_20260905.log
  - artifacts/rtd_validation_20260904/final_protocol_retry_20260905.xml
  - artifacts/rtd_validation_20260904/final_html_20260905.log
  - artifacts/rtd_validation_20260904/final_links_20260905.log
  - artifacts/rtd_validation_20260904/final_source_assets_20260905.log
  - artifacts/rtd_validation_20260904/final_repo_assets_20260905.log
  - artifacts/rtd_validation_20260904/final_epub_20260905.log
  - artifacts/rtd_validation_20260904/final_pdf_20260905.log
  - artifacts/rtd_validation_20260904/final_archive_20260905.log
  - artifacts/rtd_validation_20260904/final_offline_20260905.json
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

- DATETIME: 2026-09-05T13:18:03Z
  TYPE: FACT
  CLAIM: Consumed codex_1's source-settled notice: ordered-disposal code/docs and v0.2.3 generated
    assets/corpora pass its checks. The changed public inputs include README teardown, Intermediate
    configuration, and Beginner 35 / Intermediate 30-31. Final RTD qualification may now run. Browser
    checks also confirmed all 17 engineering SVGs loaded at 375px, full-size download controls are
    available, and native Tab/Right moves long preformatted code horizontally (scrollLeft 0 -> 40).
  EVIDENCE:
  - tickets/tasks/2026-09-04_ordered_disposal_docs_assets_task.md
  - Browser reference/architecture/05_engineering_drawings/index.html and beginner/capstone.html.
  - docs/tools/example_catalog.py:108-143
  - docs/tools/check_site.py:110-156
  IMPACT: Final docs builds can use settled public inputs; no source/LLM regeneration should be
    necessary unless their explicit checks detect new drift. Notify codex_1 before more public prose edits.
  NEXT: Reconcile all sources/API dispositions and rebuild/test the final HTML/PDF/ePub outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:24:58Z
  TYPE: MEASURE
  CLAIM: Inventory reconciles 294 pages, 48 guide chapters, 133 lessons (41/37/19/36), 137 lesson/helper
    files, and 76 API dispositions (60 exports, eight values, eight returned surfaces). All four ZIPs
    match canonical bytes. All 36 docs tests pass. Current HEAD advanced to 20123b8a during owner work;
    the final HTML was rebuilt. The 3.14t lesson run passed 132/133; Expert 05 failed only at the
    temporary interface-file write with Windows PermissionError, matching the prior sandbox failure.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/final_inventory_20260905.json
  - artifacts/rtd_validation_20260904/final_docs_tests_20260905.log
  - artifacts/rtd_validation_20260904/final_examples_20260905.log:1-180
  - artifacts/rtd_validation_20260904/final_html_20260905.log
  - UX_and_AIX_experiences/04_expert/05_protocol_crafter_the_tool_that_writes.py:122-160
  IMPACT: No catalog/API/source omission or new lesson assertion failure was found. Retry only the
    unchanged filesystem-writing lesson outside the sandbox; keep its outcome separate from the 132.
  NEXT: Run the bounded ProtocolCrafter retry and final offline/link/asset qualification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:38:36Z
  TYPE: FACT
  CLAIM: Final HTML/link/source/asset checks pass; ePub has 62 XHTML pages with no local-link errors
    or scripts, and the 948-file HTML archive matches every built byte. Native PDF has 107 pages,
    but rendered physical page 23 clips two long configuration names at the next table column.
    Sphinx inline literal wrapping omits underscore breakpoints. Route this actual PDF defect to S8.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/final_offline_20260905.json
  - docs/_build/audit-pdf-pages/configuration-023.png
  - docs/_build/handbook-latex/sphinxlatexstyletext.sty:11-18
  - docs/_build/handbook-latex/sphinxlatexliterals.sty:1183-1223
  - https://www.sphinx-doc.org/en/master/latex.html
  IMPACT: Compilation success is not visual acceptance. The fix belongs in docs/conf.py's PDF
    presentation, preserving the canonical configuration names and runtime prose.
  NEXT: Add scoped inline-code underscore breaks and consistent highlighting, then re-render the PDF.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:09:36Z
  TYPE: FACT
  CLAIM: S8 final PDF/runbook correction is verified and the complete requirements-to-evidence
    matrix is current. Local implementation is ready for owner review. The public latest URL
    still displays 404 on fresh browser reload; actual hosted features require project/access.
  EVIDENCE:
  - artifacts/2026-09-05_rtd_final_quality_audit.md
  - artifacts/rtd_validation_20260904/release_qualification_20260905.json
  - tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md
  - Browser fresh reload of https://melder.readthedocs.io/en/latest/.
  IMPACT: No implementation is knowingly left unfinished locally. Keep exact zoom/clipboard
    limits and hosted dependencies visible; owner acceptance and publication are not claimed.
  NEXT: Obtain the actual RTD project/branch and authorized read-only dashboard/build-log access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Local quality audit is complete and in review. The final audit artifact is the entry point for all
evidence, fixes, and precise limits. Hosted-project verification remains blocked; native 200% zoom
and clipboard payload readback need manual/capable-browser checks. Owner retains final acceptance.
