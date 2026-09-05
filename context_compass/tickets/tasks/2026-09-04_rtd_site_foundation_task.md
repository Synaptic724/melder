# Task: Implement the four-level site foundation and local Sphinx build

## Metadata
- Task ID: TASK-2026-09-04-rtd-site-foundation
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-navigation-and-site-shell
- Story Path: ../stories/2026-09-04_rtd_navigation_and_site_shell_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-05T13:02:41Z

## Objective
Create the working documentation source assembly, homepage, four level landings, complete contents, navigation, visual theme, and a representative real API/example/diagram build.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/conf.py, docs/requirements.txt, docs/navigation.toml, docs/index.md, docs/contents.rst, docs/tools/, docs/_static/, level landing pages, docs-focused checks, and this task's patch artifacts.
- DEPENDENCIES: Approved blueprint; required patch contracts; isolated Python 3.14 environment.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Observed focus/contrast defects corrected and verified; native browser zoom is
  unavailable through the current browser controls, with 320/375/640/768/1024px reflow verified.

## Steps / Checklist
- [x] Read the exact inputs and record one bounded implementation decision.
- [x] Complete required patch contracts when the change is system-impacting.
- [x] Implement the scoped deliverable with notes before the next tranche.
- [x] Validate meaningful behavior/content and record actual outcomes.
- [x] Synchronize parent story and hand off; formal acceptance remains open.

## Acceptance Criteria
- [x] Local build runs with a recorded compatible dependency set.
- [x] Exactly Beginner, Intermediate, Advanced, Expert appear as first-depth learning routes.
- [x] Examples and Full Contents are prominent and all generated page IDs have one parent.
- [x] A real saved example, public API signature, and architecture SVG render correctly.
- [ ] Keyboard/mobile/zoom navigation and source inclusion are inspected.

## Validation
- Strict HTML and local-link/source checks pass; see the linked logs and S9 audit report.
- Mobile/keyboard/skip/card/menu checks pass. A separate build with custom JavaScript removed exposes
  all 133 examples and the complete contents at 320px. Native 200% browser zoom is not verified.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/rtd_site_2026_09_04/architecture_patch.md
  - system_docs/patches/active/rtd_site_2026_09_04/component_patch_documentation_pipeline.md
  - system_docs/patches/active/rtd_site_2026_09_04/code_description_patch_documentation_pipeline.md
  - artifacts/rtd_validation_20260904/navigation_audit_build_20260905.log
  - artifacts/rtd_validation_20260904/navigation_audit_links_20260905.log
  - artifacts/rtd_validation_20260904/navigation_final_build_20260905.log
  - artifacts/rtd_validation_20260904/navigation_final_links_20260905.log
  - artifacts/rtd_validation_20260904/accessibility_build_20260905.log
  - artifacts/rtd_validation_20260904/accessibility_links_20260905.log
  - artifacts/rtd_validation_20260904/accessibility_final_build_20260905.log
  - artifacts/rtd_validation_20260904/no_custom_js_build_20260905.log
- DISPOSITION: promote_to_documentation
- VALIDATION_DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Promote the durable contract into docs/maintaining.md at accepted pipeline closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement the four-level site foundation and local Sphinx build
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
  NEXT: Prepare the docs pipeline patch contract and the isolated build environment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:14:08Z
  TYPE: DECISION
  CLAIM: Implement a documentation-only source assembly component with one navigation model and
    a strict public-input boundary. Patch architecture invariants map to path/source tests; component
    interfaces map to prepare/build/check CLI behavior; control-flow gates map to invalid-input and
    repeat-build checks. No Melder runtime behavior change is part of this task.
  EVIDENCE:
  - system_docs/patches/active/rtd_site_2026_09_04/architecture_patch.md
  - system_docs/patches/active/rtd_site_2026_09_04/component_patch_documentation_pipeline.md
  - system_docs/patches/active/rtd_site_2026_09_04/code_description_patch_documentation_pipeline.md
  IMPACT: Required patch scope and implementation/validation mapping are explicit before code edits.
  NEXT: Read the authored patch contracts and implement the navigation/build foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:14:08Z
  TYPE: MEASURE
  CLAIM: Isolated dependency installation succeeded after the authorized network escalation: Sphinx
    9.1.0, MyST 5.1.0, sphinx-rtd-theme 3.1.0, sphinx-design 0.7.0, and copybutton 0.5.2 are installed
    under the retained Python 3.14 docs environment. A Sphinx build has not yet run.
  EVIDENCE:
  - uv pip install output for context_compass/artifacts/rtd_probe_20260904/.venv on 2026-09-04T22:14:08Z
  IMPACT: The earlier network blocker no longer prevents local documentation implementation.
  NEXT: Build the first real site with those resolved versions and capture exact requirements.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:23:58Z
  TYPE: MEASURE
  CLAIM: Implemented the initial 10-page Sphinx site, four exact levels, complete contents generation,
    canonical example/SVG inclusion, theme, and validated prepare/check/build command. The first real
    HTML build rendered all pages and imported Melder successfully on Python 3.14, but strict status
    is failure because SpellMap's class docstring emitted six formatting warnings/errors. The expected
    GIL-mode UserWarning appeared separately; no runtime behavior was changed.
  EVIDENCE:
  - docs/tools/build_docs.py
  - docs/navigation.toml
  - docs/conf.py
  - docs/_build/html/index.html
  - Sphinx 9.1.0 first build output on 2026-09-04T22:23:58Z
  IMPACT: Actual rendering is available. Source docstring formatting is the first concrete strict-build
    defect to resolve before broadening API coverage or calling the foundation complete.
  NEXT: Read the SpellMap docstring and correct the narrow formatting mismatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:26:50Z
  TYPE: DECISION
  CLAIM: SpellMap's class documentation contains a single-backtick python block, which native
    reStructuredText cannot parse. Add a docs-only autodoc formatter that translates known fenced
    code blocks before Napoleon runs, preserving text and code while leaving canonical runtime source
    untouched. Malformed unclosed blocks must fail explicitly rather than discard content.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_map.py:35-58
  - docs/conf.py:27-37
  IMPACT: The publication layer handles the repository's existing docstring markup without a runtime
    edit or global warning suppression. Regression checks and the real strict build verify it.
  NEXT: Implement the format bridge and rerun the strict representative build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:43:42Z
  TYPE: MEASURE
  CLAIM: The 10-page foundation passes the strict Sphinx build after adding the content-preserving
    docstring fence bridge. All nine docs regression checks pass. Browser inspection verified the
    four levels, cards, real full-contents links, and the 390px mobile layout without horizontal
    overflow. The native theme's icon-only menu was replaced by a real button; Enter toggled its
    expanded state. Direct mobile Contents/Examples links and per-page contents are present.
    Full zoom and corpus-wide checks remain part of the later quality task.
  EVIDENCE:
  - docs/tools/build_docs.py
  - docs/tools/docstring_format.py
  - docs/tests/test_build_docs.py
  - docs/_templates/layout.html
  - docs/_templates/page.html
  - Local Sphinx/unittest output and browser inspection at http://127.0.0.1:8765/
  IMPACT: The source/build/navigation contract is ready for the catalog task. Initial test fixture
    failures were a Windows temporary-directory ACL issue and were resolved using contained generated
    test workspaces; the passing test run is recorded above, not inferred.
  NEXT: Extend the foundation with all 133 saved lesson pages under the catalog task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T12:21:46Z
  TYPE: DECISION
  CLAIM: Fix the S9 keyboard defects in docs/_static/melder.css, navigation.js, and _templates/layout.html.
    The parent theme exposes extrabody/content/navigation blocks. Use these blocks for a static
    skip-to-content target and navigation target; preserve the theme's toggle behavior. CSS will
    hide the closed mobile sidebar and outline complete focused cards. JavaScript will move focus
    into an opened menu and close/return focus on Escape without adding a second toggle mechanism.
  EVIDENCE:
  - tickets/tasks/2026-09-04_rtd_quality_audit_task.md
  - Sphinx RTD theme 3.1.0 layout.html:108-194
  - docs/_static/navigation.js:1-14
  IMPACT: The existing publication patch covers this accessibility fix. Validate real keyboard/
    pointer behavior and all generated pages; no runtime assets or LLM corpora are regenerated.
  NEXT: Implement the three-file fix and rebuild the site for focused browser verification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:31:02Z
  TYPE: MEASURE
  CLAIM: First fix passes strict rendering and all 35,492 links across 294 pages. At 375px, closed
    drawer controls no longer receive hidden focus; skip-link Enter focuses the content target.
    Menu Enter moves focus inside the visible drawer; Escape closes it and restores the toggle.
    A further Tab-out probe found the shifted brand link at x=397 outside a 375px viewport, so close
    the non-modal drawer when focus enters the surrounding page.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/navigation_audit_links_20260905.log:1-1
  - docs/_static/navigation.js
  - docs/_static/melder.css
  - Browser focus/geometry observations at 375x812.
  IMPACT: The final focus-in handler preserves ordinary page navigation without trapping focus or
    exposing shifted content. Rebuild and repeat the exact Tab-out case before returning to S9.
  NEXT: Verify the final drawer/card focus behavior, then resume the remaining quality audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:53:01Z
  TYPE: MEASURE
  CLAIM: Final drawer/card focus checks passed before recovery. Rendered article/download links use
    #2980b9 on #fcfcfc (4.192:1); this misses the normal-text 4.5:1 threshold. Python comments
    (4.580:1) and strings (5.943:1) pass. Copybutton 0.5.2 exposes buttons to keyboard focus but its
    CSS shows them only on hover/success. Complete the bounded CSS correction: darker links,
    keyboard-visible copy controls, consistent input/select/summary focus, and stronger filter borders.
  EVIDENCE:
  - docs/_static/melder.css:1-63
  - docs/_static/navigation.js:1-38
  - artifacts/rtd_validation_20260904/navigation_final_links_20260905.log:1-1
  - Browser computed styles and contrast measurements on examples/hello-melder.html.
  - sphinx_copybutton/_static/copybutton.css:1-43 (installed version 0.5.2).
  - https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
  IMPACT: Keep passing syntax highlighting; repair the observed reading/focus defects without
    changing Melder runtime behavior. ContextCompass recovery completed with existing approval.
  NEXT: Apply the CSS correction and verify rendered contrast, focus, and narrow layouts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:58:00Z
  TYPE: FACT
  CLAIM: Darker links and keyboard copy visibility are implemented; strict build and 35,497 local
    links pass. Copy control receives visible keyboard focus and reports Copied on Enter. Browser
    virtual clipboard readback is unavailable, so copied bytes are not claimed verified. Capstone
    plain inline literals still use the theme's #e74c3c on white; darken them to #b23a2d. Give sidebar
    focused links their own dark background/light inset ring to avoid low blue-on-charcoal contrast.
  EVIDENCE:
  - docs/_static/melder.css:1-75
  - artifacts/rtd_validation_20260904/accessibility_build_20260905.log
  - artifacts/rtd_validation_20260904/accessibility_links_20260905.log:1-1
  - Browser computed styles on beginner/capstone.html and keyboard interaction on Hello Melder.
  IMPACT: All observed text/focus contrast defects now have bounded style corrections. The in-app
    browser's Ctrl+= shortcut did not change CSS viewport or DPR; native 200% zoom remains unverified.
  NEXT: Complete responsive/focus checks on the final style rules and return S1 to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:02:41Z
  TYPE: MEASURE
  CLAIM: Final styles render correctly; capstone has no page overflow at 320, 375, 640, 768, or
    1024px. Phone menu Enter/Escape moves/returns focus correctly. Skip Enter targets main content;
    homepage retains all four named cards and visible Contents/Examples controls at 320px. Separate
    strict Sphinx output with html_js_files empty contains neither navigation.js nor catalog.js;
    native mobile links open Full Contents (293 links) and all 133 visible examples.
  EVIDENCE:
  - docs/_static/melder.css:1-72
  - artifacts/rtd_validation_20260904/accessibility_final_build_20260905.log
  - artifacts/rtd_validation_20260904/no_custom_js_build_20260905.log
  - Browser inspection of local ports 8765 and 8766 at the recorded viewport widths.
  IMPACT: S1 corrections are reviewable. Native zoom and copied-byte readback remain tool limitations,
    not claimed passes; S9 carries those precise limits with the remaining hosted audit.
  NEXT: Resume S9 catalog/search/reference/offline checks and final source qualification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Four-level site foundation and final focus/contrast fixes are implemented and locally verified.
S9 resumes the integrated audit. Native 200% browser zoom and copied-byte readback could not be
verified with this browser tool. Owner acceptance and hosted publication remain separate.
